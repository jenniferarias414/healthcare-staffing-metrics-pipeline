#!/usr/bin/env python3
"""
Build local curated outputs for the Healthcare Staffing Metrics Pipeline.

This script is the local/dev version of the planned Glue/PySpark transformation layer.
It reads the downloaded Google Drive source files from project-assets, creates cleaned
silver tables, creates a dashboard-ready gold table, and writes Parquet/CSV outputs.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOWNLOADS = REPO_ROOT / "project-assets" / "source-downloads"
RAW_DIR = REPO_ROOT / "data" / "raw"
CURATED_DIR = REPO_ROOT / "data" / "curated"
REPORTS_DIR = REPO_ROOT / "reports" / "final-samples"
MANIFESTS_DIR = REPO_ROOT / "manifests"


def log(message: str) -> None:
    print(f"[healthcare-pipeline] {message}")


def normalize_name(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())).strip("_")


def find_first_existing(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def read_csv_flexible(path: Path, **kwargs) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding, low_memory=False, **kwargs)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise RuntimeError(f"Could not read {path} using supported encodings") from last_error


def find_master_csv() -> Path:
    candidates = [
        SOURCE_DOWNLOADS / "PBJ_Daily_Nurse_Staffing_Q2_2024.csv",
        RAW_DIR / "master" / "PBJ_Daily_Nurse_Staffing_Q2_2024.csv",
    ]
    found = find_first_existing(candidates)
    if found:
        return found
    matches = [m for m in REPO_ROOT.glob("**/PBJ_Daily_Nurse_Staffing_Q2_2024.csv") if ".venv" not in m.parts]
    if matches:
        return matches[0]
    raise FileNotFoundError("Could not find PBJ_Daily_Nurse_Staffing_Q2_2024.csv")


def find_supporting_zip() -> Path | None:
    candidates = list(SOURCE_DOWNLOADS.glob("Nursing_Homes_data*.zip"))
    if (RAW_DIR / "supporting").exists():
        candidates += list((RAW_DIR / "supporting").glob("Nursing_Homes_data*.zip"))
    candidates += [p for p in REPO_ROOT.glob("**/Nursing_Homes_data*.zip") if ".venv" not in p.parts]
    return candidates[0] if candidates else None


def extract_supporting_zip(zip_path: Path) -> Path:
    extract_dir = RAW_DIR / "supporting_extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    log(f"Extracting supporting files from {zip_path.name} to {extract_dir}")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)
    return extract_dir


def find_provider_info_csv(extract_dir: Path) -> Path:
    csv_files = [p for p in extract_dir.rglob("*.csv") if "__MACOSX" not in p.parts]
    for p in csv_files:
        name = p.name.lower()
        if "providerinfo" in name or "provider_info" in name or "provider information" in name:
            return p
    for p in csv_files:
        name = p.name.lower()
        if "provider" in name and "info" in name:
            return p
    raise FileNotFoundError("Could not identify a provider info CSV in supporting files")


def parse_workdate(series: pd.Series) -> pd.Series:
    raw = series.astype(str).str.strip()
    yyyymmdd = pd.to_datetime(raw.where(raw.str.fullmatch(r"\d{8}")), format="%Y%m%d", errors="coerce")
    numeric = pd.to_numeric(raw, errors="coerce")
    excel_dates = pd.to_datetime(numeric, unit="D", origin="1899-12-30", errors="coerce")
    parsed = pd.to_datetime(raw, errors="coerce")
    return yyyymmdd.fillna(excel_dates).fillna(parsed)


def pick_column(columns: Iterable[str], candidates: list[str]) -> str | None:
    normalized = {normalize_name(c): c for c in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def as_number(df: pd.DataFrame, column: str | None) -> pd.Series:
    if not column or column not in df.columns:
        return pd.Series(0.0, index=df.index)
    return pd.to_numeric(df[column], errors="coerce").fillna(0.0)


def build_silver_daily_staffing(master_path: Path) -> pd.DataFrame:
    log(f"Reading master staffing file: {master_path}")
    df = read_csv_flexible(master_path)
    required = ["PROVNUM", "WorkDate", "MDScensus"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Master staffing file missing required columns: {missing}")
    df["provider_id"] = df["PROVNUM"].astype(str).str.strip()
    df["work_date"] = parse_workdate(df["WorkDate"])
    df["mds_census"] = pd.to_numeric(df["MDScensus"], errors="coerce")
    rn_total = as_number(df, "Hrs_RN")
    lpn_total = as_number(df, "Hrs_LPN")
    cna_total = as_number(df, "Hrs_CNA")
    rn_emp = as_number(df, "Hrs_RN_emp")
    rn_ctr = as_number(df, "Hrs_RN_ctr")
    lpn_emp = as_number(df, "Hrs_LPN_emp")
    lpn_ctr = as_number(df, "Hrs_LPN_ctr")
    cna_emp = as_number(df, "Hrs_CNA_emp")
    cna_ctr = as_number(df, "Hrs_CNA_ctr")
    if rn_total.sum() == 0 and (rn_emp.sum() + rn_ctr.sum()) > 0:
        rn_total = rn_emp + rn_ctr
    if lpn_total.sum() == 0 and (lpn_emp.sum() + lpn_ctr.sum()) > 0:
        lpn_total = lpn_emp + lpn_ctr
    if cna_total.sum() == 0 and (cna_emp.sum() + cna_ctr.sum()) > 0:
        cna_total = cna_emp + cna_ctr
    out = pd.DataFrame({
        "provider_id": df["provider_id"],
        "work_date": df["work_date"],
        "year": df["work_date"].dt.year,
        "month": df["work_date"].dt.month,
        "year_month": df["work_date"].dt.to_period("M").astype(str),
        "mds_census": df["mds_census"],
        "rn_hours": rn_total,
        "lpn_hours": lpn_total,
        "cna_hours": cna_total,
        "rn_contract_hours": rn_ctr,
        "lpn_contract_hours": lpn_ctr,
        "cna_contract_hours": cna_ctr,
    })
    out["total_nurse_hours"] = out["rn_hours"] + out["lpn_hours"] + out["cna_hours"]
    out["contract_nurse_hours"] = out["rn_contract_hours"] + out["lpn_contract_hours"] + out["cna_contract_hours"]
    positive_census = out["mds_census"] > 0
    positive_hours = out["total_nurse_hours"] > 0
    out["total_nurse_hours_per_resident_day"] = np.where(positive_census, out["total_nurse_hours"] / out["mds_census"], np.nan)
    out["rn_hours_per_resident_day"] = np.where(positive_census, out["rn_hours"] / out["mds_census"], np.nan)
    out["contract_staff_ratio"] = np.where(positive_hours, out["contract_nurse_hours"] / out["total_nurse_hours"], np.nan)
    out = out[out["work_date"].notna()].copy()
    log(f"Built silver_daily_staffing rows: {len(out):,}")
    return out


def build_silver_provider(provider_path: Path) -> pd.DataFrame:
    log(f"Reading provider info file: {provider_path}")
    raw = read_csv_flexible(provider_path, dtype=str)
    raw.columns = [str(c).strip() for c in raw.columns]
    id_col = pick_column(raw.columns, ["cms_certification_number_ccn", "federal_provider_number", "provider_id", "provnum", "ccn"])
    name_col = pick_column(raw.columns, ["provider_name", "name"])
    state_col = pick_column(raw.columns, ["state"])
    beds_col = pick_column(raw.columns, ["number_of_certified_beds", "certified_beds"])
    overall_col = pick_column(raw.columns, ["overall_rating"])
    staffing_col = pick_column(raw.columns, ["staffing_rating"])
    qm_col = pick_column(raw.columns, ["qm_rating", "quality_measure_rating"])
    ownership_col = pick_column(raw.columns, ["ownership_type"])
    provider_type_col = pick_column(raw.columns, ["provider_type"])
    city_col = pick_column(raw.columns, ["city", "provider_city"])
    county_col = pick_column(raw.columns, ["county_name", "county"])
    if not id_col:
        raise ValueError(f"Could not find provider ID column in {provider_path.name}")
    out = pd.DataFrame({
        "provider_id": raw[id_col].astype(str).str.strip(),
        "provider_name": raw[name_col].astype(str).str.strip() if name_col else "",
        "state": raw[state_col].astype(str).str.strip() if state_col else "",
        "city": raw[city_col].astype(str).str.strip() if city_col else "",
        "county": raw[county_col].astype(str).str.strip() if county_col else "",
        "ownership_type": raw[ownership_col].astype(str).str.strip() if ownership_col else "",
        "provider_type": raw[provider_type_col].astype(str).str.strip() if provider_type_col else "",
        "certified_bed_count": pd.to_numeric(raw[beds_col], errors="coerce") if beds_col else np.nan,
        "overall_rating": pd.to_numeric(raw[overall_col], errors="coerce") if overall_col else np.nan,
        "staffing_rating": pd.to_numeric(raw[staffing_col], errors="coerce") if staffing_col else np.nan,
        "quality_measure_rating": pd.to_numeric(raw[qm_col], errors="coerce") if qm_col else np.nan,
    })
    out = out[out["provider_id"].notna() & (out["provider_id"] != "")].drop_duplicates("provider_id")
    log(f"Built silver_provider rows: {len(out):,}")
    return out


def build_silver_date(silver_daily: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DataFrame({"date": sorted(silver_daily["work_date"].dropna().unique())})
    dates["date"] = pd.to_datetime(dates["date"])
    dates["year"] = dates["date"].dt.year
    dates["month"] = dates["date"].dt.month
    dates["year_month"] = dates["date"].dt.to_period("M").astype(str)
    dates["quarter"] = dates["date"].dt.quarter
    dates["day_of_week"] = dates["date"].dt.day_name()
    return dates


def build_gold_monthly(silver_daily: pd.DataFrame, silver_provider: pd.DataFrame) -> pd.DataFrame:
    grouped = (silver_daily.groupby(["provider_id", "year_month"], dropna=False)
        .agg(days_reported=("work_date", "nunique"), avg_daily_census=("mds_census", "mean"),
             total_nurse_hours=("total_nurse_hours", "sum"), total_contract_nurse_hours=("contract_nurse_hours", "sum"),
             avg_total_nurse_hours_per_resident_day=("total_nurse_hours_per_resident_day", "mean"),
             avg_rn_hours_per_resident_day=("rn_hours_per_resident_day", "mean"),
             avg_contract_staff_ratio=("contract_staff_ratio", "mean"))
        .reset_index())
    gold = grouped.merge(silver_provider, on="provider_id", how="left")
    gold["bed_utilization_rate"] = np.where(gold["certified_bed_count"].fillna(0) > 0, gold["avg_daily_census"] / gold["certified_bed_count"], np.nan)
    return gold


def write_outputs(silver_provider, silver_daily, silver_date, gold_monthly) -> None:
    paths = {
        "silver_provider": CURATED_DIR / "silver" / "silver_provider",
        "silver_daily_staffing": CURATED_DIR / "silver" / "silver_daily_staffing",
        "silver_date": CURATED_DIR / "silver" / "silver_date",
        "gold_provider_monthly_staffing_metrics": CURATED_DIR / "gold" / "gold_provider_monthly_staffing_metrics",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    silver_provider.to_parquet(paths["silver_provider"] / "part-00000.parquet", index=False)
    silver_daily.to_parquet(paths["silver_daily_staffing"] / "part-00000.parquet", index=False)
    silver_date.to_parquet(paths["silver_date"] / "part-00000.parquet", index=False)
    gold_monthly.to_parquet(paths["gold_provider_monthly_staffing_metrics"] / "part-00000.parquet", index=False)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    gold_monthly.head(1000).to_csv(REPORTS_DIR / "gold_provider_monthly_staffing_metrics_sample.csv", index=False)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "silver_provider_rows": int(len(silver_provider)),
        "silver_daily_staffing_rows": int(len(silver_daily)),
        "silver_date_rows": int(len(silver_date)),
        "gold_provider_monthly_staffing_metrics_rows": int(len(gold_monthly)),
        "date_min": str(silver_daily["work_date"].min()),
        "date_max": str(silver_daily["work_date"].max()),
        "distinct_providers_in_staffing": int(silver_daily["provider_id"].nunique()),
        "distinct_providers_in_provider_dim": int(silver_provider["provider_id"].nunique()),
    }
    (REPORTS_DIR / "metric_output_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md = f"""# Metric Output Summary

Generated at UTC: {summary['generated_at_utc']}

## Output Row Counts

| Output | Rows |
|---|---:|
| silver_provider | {summary['silver_provider_rows']:,} |
| silver_daily_staffing | {summary['silver_daily_staffing_rows']:,} |
| silver_date | {summary['silver_date_rows']:,} |
| gold_provider_monthly_staffing_metrics | {summary['gold_provider_monthly_staffing_metrics_rows']:,} |

## Source Date Range

- Minimum work date: {summary['date_min']}
- Maximum work date: {summary['date_max']}

## Provider Counts

- Distinct providers in staffing data: {summary['distinct_providers_in_staffing']:,}
- Distinct providers in provider table: {summary['distinct_providers_in_provider_dim']:,}

## Metrics Created

- total nurse hours
- RN hours per resident day
- total nurse hours per resident day
- contract staff ratio
- bed utilization / occupancy proxy
"""
    (REPORTS_DIR / "metric_output_summary.md").write_text(md, encoding="utf-8")
    log("Wrote curated Parquet outputs:")
    for name, path in paths.items():
        log(f"  {name}: {path}")


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    master_path = find_master_csv()
    zip_path = find_supporting_zip()
    if not zip_path:
        raise FileNotFoundError("Could not find Nursing_Homes_data*.zip")
    extract_dir = extract_supporting_zip(zip_path)
    provider_path = find_provider_info_csv(extract_dir)
    silver_daily = build_silver_daily_staffing(master_path)
    silver_provider = build_silver_provider(provider_path)
    silver_date = build_silver_date(silver_daily)
    gold_monthly = build_gold_monthly(silver_daily, silver_provider)
    write_outputs(silver_provider, silver_daily, silver_date, gold_monthly)
    log("Pipeline build complete.")
    log("Next: review reports/final-samples/metric_output_summary.md")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[healthcare-pipeline] ERROR: {exc}", file=sys.stderr)
        raise
