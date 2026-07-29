from pathlib import Path
import json
import zipfile
from datetime import datetime, timezone

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_ROOT / "project-assets"
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "output"
EXTRACT_DIR = PROJECT_ROOT / "data" / "raw" / "supporting_extracted"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

MASTER_FILE_NAME = "PBJ_Daily_Nurse_Staffing_Q2_2024.csv"
SUPPORTING_ZIP_PATTERN = "Nursing_Homes_data*.zip"

MASTER_KEY_COLUMNS = ["PROVNUM", "WorkDate"]
PROVIDER_JOIN_KEY = "PROVNUM"

STAFFING_HOUR_COLUMNS = [
    "Hrs_RNDON",
    "Hrs_RNadmin",
    "Hrs_RN",
    "Hrs_LPNadmin",
    "Hrs_LPN",
    "Hrs_CNA",
    "Hrs_NAtrn",
    "Hrs_MedAide",
]

CORE_METRIC_COLUMNS = [
    "PROVNUM",
    "PROVNAME",
    "CITY",
    "STATE",
    "COUNTY_NAME",
    "CY_Qtr",
    "WorkDate",
    "MDScensus",
    "Hrs_RN",
    "Hrs_RN_emp",
    "Hrs_RN_ctr",
    "Hrs_LPN",
    "Hrs_LPN_emp",
    "Hrs_LPN_ctr",
    "Hrs_CNA",
    "Hrs_CNA_emp",
    "Hrs_CNA_ctr",
]


def parse_workdate(series: pd.Series) -> pd.Series:
    """
    Parse WorkDate defensively.

    Public healthcare files sometimes store dates as:
    - YYYYMMDD numbers or strings
    - Excel serial dates
    - normal date strings

    This function tries the most likely formats and returns a pandas datetime series.
    """
    raw = series.copy()

    # First try YYYYMMDD, which is common for numeric date fields.
    as_str = (
        raw.astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    yyyymmdd_mask = as_str.str.fullmatch(r"\d{8}", na=False)
    if yyyymmdd_mask.mean() > 0.8:
        return pd.to_datetime(as_str, format="%Y%m%d", errors="coerce")

    # Then try Excel serial dates.
    numeric = pd.to_numeric(raw, errors="coerce")
    if numeric.notna().any():
        min_value = numeric.min()
        max_value = numeric.max()

        # Excel serial dates for modern dates are usually in this range.
        if 20000 <= min_value <= 60000 and 20000 <= max_value <= 60000:
            return pd.to_datetime(numeric, unit="D", origin="1899-12-30", errors="coerce")

    # Fallback to pandas general parser.
    return pd.to_datetime(raw, errors="coerce")


def find_one_file(pattern: str) -> Path:
    matches = list(ASSET_DIR.rglob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file found matching pattern: {pattern}")
    return matches[0]


def extract_supporting_zip(zip_path: Path) -> list[Path]:
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(EXTRACT_DIR)

    return sorted([p for p in EXTRACT_DIR.rglob("*.csv")])


def read_csv_flexible(path: Path, nrows: int | None = None) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding, low_memory=False, nrows=nrows)
        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Could not decode {path.name}. Last error: {last_error}",
    )


def summarize_dataframe(df: pd.DataFrame, key_columns: list[str] | None = None) -> dict:
    key_columns = key_columns or []

    missing_summary = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"index": "column", 0: "missing_count"})
    )
    missing_summary["missing_pct"] = (
        missing_summary["missing_count"] / len(df) * 100
    ).round(2)

    duplicate_key_count = None
    if key_columns and all(col in df.columns for col in key_columns):
        duplicate_key_count = int(df.duplicated(subset=key_columns).sum())

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": list(df.columns),
        "duplicate_full_rows": int(df.duplicated().sum()),
        "duplicate_key_count": duplicate_key_count,
        "missing_summary": missing_summary.to_dict(orient="records"),
    }


def profile_master(master_path: Path) -> tuple[dict, pd.DataFrame]:
    df = read_csv_flexible(master_path)

    profile = summarize_dataframe(df, MASTER_KEY_COLUMNS)

    date_series = parse_workdate(df["WorkDate"])
    profile["workdate_min"] = str(date_series.min().date()) if date_series.notna().any() else None
    profile["workdate_max"] = str(date_series.max().date()) if date_series.notna().any() else None
    profile["workdate_parse_success_count"] = int(date_series.notna().sum())
    profile["workdate_parse_failure_count"] = int(date_series.isna().sum())
    profile["distinct_providers"] = int(df["PROVNUM"].nunique())
    profile["distinct_states"] = int(df["STATE"].nunique())
    profile["states"] = sorted(df["STATE"].dropna().unique().tolist())

    numeric_cols = [
        col for col in ["MDScensus"] + STAFFING_HOUR_COLUMNS if col in df.columns
    ]

    numeric_summary = {}
    for col in numeric_cols:
        numeric = pd.to_numeric(df[col], errors="coerce")
        numeric_summary[col] = {
            "min": float(numeric.min()) if numeric.notna().any() else None,
            "max": float(numeric.max()) if numeric.notna().any() else None,
            "mean": float(numeric.mean()) if numeric.notna().any() else None,
            "zero_count": int((numeric == 0).sum()),
            "negative_count": int((numeric < 0).sum()),
            "missing_count": int(numeric.isna().sum()),
        }

    profile["numeric_summary"] = numeric_summary

    # Basic metric-readiness checks
    metric_df = df[CORE_METRIC_COLUMNS].copy()
    for col in [
        "MDScensus",
        "Hrs_RN",
        "Hrs_RN_emp",
        "Hrs_RN_ctr",
        "Hrs_LPN",
        "Hrs_LPN_emp",
        "Hrs_LPN_ctr",
        "Hrs_CNA",
        "Hrs_CNA_emp",
        "Hrs_CNA_ctr",
    ]:
        metric_df[col] = pd.to_numeric(metric_df[col], errors="coerce")

    metric_df["total_nurse_hours"] = (
        metric_df["Hrs_RN"].fillna(0)
        + metric_df["Hrs_LPN"].fillna(0)
        + metric_df["Hrs_CNA"].fillna(0)
    )
    metric_df["contract_nurse_hours"] = (
        metric_df["Hrs_RN_ctr"].fillna(0)
        + metric_df["Hrs_LPN_ctr"].fillna(0)
        + metric_df["Hrs_CNA_ctr"].fillna(0)
    )

    profile["metric_readiness"] = {
        "rows_with_positive_census": int((metric_df["MDScensus"] > 0).sum()),
        "rows_with_zero_or_missing_census": int(
            ((metric_df["MDScensus"].isna()) | (metric_df["MDScensus"] <= 0)).sum()
        ),
        "rows_with_positive_total_nurse_hours": int(
            (metric_df["total_nurse_hours"] > 0).sum()
        ),
        "rows_with_zero_total_nurse_hours": int(
            (metric_df["total_nurse_hours"] == 0).sum()
        ),
    }

    return profile, df


def profile_supporting_files(csv_paths: list[Path]) -> list[dict]:
    profiles = []

    for path in csv_paths:
        try:
            df_sample = read_csv_flexible(path, nrows=10000)
            full_row_count = None

            # Count rows without holding huge supporting files entirely in memory.
            try:
                full_df = read_csv_flexible(path)
                full_row_count = int(len(full_df))
                columns = list(full_df.columns)
                duplicate_full_rows = int(full_df.duplicated().sum())
                missing_top = (
                    full_df.isna()
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                    .rename(columns={"index": "column", 0: "missing_count"})
                    .to_dict(orient="records")
                )
            except Exception:
                columns = list(df_sample.columns)
                duplicate_full_rows = None
                missing_top = (
                    df_sample.isna()
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                    .rename(columns={"index": "column", 0: "missing_count"})
                    .to_dict(orient="records")
                )

            possible_provider_keys = [
                col for col in columns if col.upper() in ["PROVNUM", "CMS CERTIFICATION NUMBER (CCN)", "CMS CERTIFICATION NUMBER"]
            ]

            profiles.append(
                {
                    "file_name": path.name,
                    "relative_path": str(path.relative_to(PROJECT_ROOT)),
                    "row_count": full_row_count,
                    "column_count": len(columns),
                    "columns": columns,
                    "possible_provider_keys": possible_provider_keys,
                    "duplicate_full_rows": duplicate_full_rows,
                    "top_missing_columns": missing_top,
                }
            )
        except Exception as exc:
            profiles.append(
                {
                    "file_name": path.name,
                    "relative_path": str(path.relative_to(PROJECT_ROOT)),
                    "error": str(exc),
                }
            )

    return profiles


def write_markdown_report(master_profile: dict, supporting_profiles: list[dict]) -> None:
    md_path = OUTPUT_DIR / "source-profile-report.md"

    lines = []
    lines.append("# Healthcare Source Profile Report")
    lines.append("")
    lines.append(f"Generated at UTC: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append("")

    lines.append("## Master PBJ Staffing File")
    lines.append("")
    lines.append(f"- Row count: `{master_profile['row_count']}`")
    lines.append(f"- Column count: `{master_profile['column_count']}`")
    lines.append(f"- Duplicate full rows: `{master_profile['duplicate_full_rows']}`")
    lines.append(
        f"- Duplicate provider/date keys: `{master_profile['duplicate_key_count']}`"
    )
    lines.append(f"- Distinct providers: `{master_profile['distinct_providers']}`")
    lines.append(f"- Distinct states: `{master_profile['distinct_states']}`")
    lines.append(f"- WorkDate min: `{master_profile['workdate_min']}`")
    lines.append(f"- WorkDate max: `{master_profile['workdate_max']}`")
    lines.append(f"- WorkDate parse success count: `{master_profile['workdate_parse_success_count']}`")
    lines.append(f"- WorkDate parse failure count: `{master_profile['workdate_parse_failure_count']}`")
    lines.append("")

    lines.append("### Metric Readiness")
    lines.append("")
    for key, value in master_profile["metric_readiness"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")

    lines.append("### Numeric Summary")
    lines.append("")
    for col, summary in master_profile["numeric_summary"].items():
        lines.append(f"#### `{col}`")
        lines.append("")
        for key, value in summary.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")

    lines.append("### Master Missing Values")
    lines.append("")
    lines.append("| Column | Missing Count | Missing % |")
    lines.append("|---|---:|---:|")
    for item in master_profile["missing_summary"]:
        if item["missing_count"] > 0:
            lines.append(
                f"| {item['column']} | {item['missing_count']} | {item['missing_pct']} |"
            )
    lines.append("")

    lines.append("## Supporting Files")
    lines.append("")
    lines.append("| File | Rows | Columns | Possible Provider Key | Notes |")
    lines.append("|---|---:|---:|---|---|")
    for profile in supporting_profiles:
        if "error" in profile:
            lines.append(
                f"| {profile['file_name']} |  |  |  | ERROR: {profile['error']} |"
            )
        else:
            keys = ", ".join(profile["possible_provider_keys"]) or "Not obvious"
            lines.append(
                f"| {profile['file_name']} | {profile['row_count']} | {profile['column_count']} | {keys} |  |"
            )

    lines.append("")
    lines.append("## Initial Modeling Notes")
    lines.append("")
    lines.append("- The PBJ staffing file appears to be the driving source for daily staffing metrics.")
    lines.append("- `PROVNUM` is expected to be the main provider/facility join key.")
    lines.append("- `WorkDate` supports daily and monthly trend analysis.")
    lines.append("- `MDScensus` can be used as the resident/patient census denominator.")
    lines.append("- RN, LPN, and CNA hour fields can be used to calculate staffing coverage metrics.")
    lines.append("- Supporting provider files need to be narrowed to the files that help calculate bed utilization, ratings, quality indicators, or facility context.")
    lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote Markdown report: {md_path}")


def main() -> None:
    master_path = find_one_file(MASTER_FILE_NAME)
    zip_path = find_one_file(SUPPORTING_ZIP_PATTERN)

    print(f"Master file: {master_path}")
    print(f"Supporting ZIP: {zip_path}")

    print("Extracting supporting ZIP...")
    supporting_csvs = extract_supporting_zip(zip_path)
    print(f"Found {len(supporting_csvs)} supporting CSV files.")

    print("Profiling master PBJ staffing file...")
    master_profile, _ = profile_master(master_path)

    print("Profiling supporting files...")
    supporting_profiles = profile_supporting_files(supporting_csvs)

    output_json = OUTPUT_DIR / "source-profile-summary.json"
    output_json.write_text(
        json.dumps(
            {
                "master_profile": master_profile,
                "supporting_profiles": supporting_profiles,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"Wrote JSON summary: {output_json}")

    write_markdown_report(master_profile, supporting_profiles)

    print("Source profiling complete.")


if __name__ == "__main__":
    main()
