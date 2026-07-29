from pathlib import Path
import csv
import hashlib
import json
import zipfile
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_ROOT / "project-assets"
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MASTER_FILE_NAME = "PBJ_Daily_Nurse_Staffing_Q2_2024.csv"
SUPPORTING_ZIP_PATTERN = "Nursing_Homes_data*.zip"

EXPECTED_MASTER_COLUMNS = [
    "PROVNUM",
    "PROVNAME",
    "CITY",
    "STATE",
    "COUNTY_NAME",
    "COUNTY_FIPS",
    "CY_Qtr",
    "WorkDate",
    "MDScensus",
    "Hrs_RNDON",
    "Hrs_RNDON_emp",
    "Hrs_RNDON_ctr",
    "Hrs_RNadmin",
    "Hrs_RNadmin_emp",
    "Hrs_RNadmin_ctr",
    "Hrs_RN",
    "Hrs_RN_emp",
    "Hrs_RN_ctr",
    "Hrs_LPNadmin",
    "Hrs_LPNadmin_emp",
    "Hrs_LPNadmin_ctr",
    "Hrs_LPN",
    "Hrs_LPN_emp",
    "Hrs_LPN_ctr",
    "Hrs_CNA",
    "Hrs_CNA_emp",
    "Hrs_CNA_ctr",
    "Hrs_NAtrn",
    "Hrs_NAtrn_emp",
    "Hrs_NAtrn_ctr",
    "Hrs_MedAide",
    "Hrs_MedAide_emp",
    "Hrs_MedAide_ctr",
]


def sha256_file(path: Path) -> str:
    hash_obj = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def count_csv_rows_and_columns(path: Path) -> dict:
    """
    Read a CSV using a small set of common encodings.

    Some public healthcare/government CSVs contain Windows-style characters
    that fail under strict UTF-8. Trying cp1252 keeps the file readable
    without treating the file as corrupt.
    """
    encodings_to_try = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    last_error = None

    for encoding in encodings_to_try:
        try:
            with path.open("r", encoding=encoding, newline="") as file:
                reader = csv.reader(file)
                header = next(reader, [])
                row_count = sum(1 for _ in reader)

            return {
                "columns": header,
                "column_count": len(header),
                "data_row_count": row_count,
                "encoding_used": encoding,
            }
        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Could not decode CSV using encodings {encodings_to_try}. Last error: {last_error}",
    )


def inspect_zip(path: Path) -> dict:
    result = {
        "zip_path": str(path.relative_to(PROJECT_ROOT)),
        "zip_can_open": False,
        "zip_file_count": 0,
        "zip_csv_count": 0,
        "zip_pdf_count": 0,
        "zip_files": [],
        "bad_zip_members": [],
    }

    try:
        with zipfile.ZipFile(path, "r") as z:
            bad_file = z.testzip()
            result["bad_zip_members"] = [] if bad_file is None else [bad_file]
            names = [name for name in z.namelist() if not name.endswith("/")]
            result["zip_can_open"] = True
            result["zip_file_count"] = len(names)
            result["zip_csv_count"] = sum(name.lower().endswith(".csv") for name in names)
            result["zip_pdf_count"] = sum(name.lower().endswith(".pdf") for name in names)
            result["zip_files"] = names
    except zipfile.BadZipFile:
        result["bad_zip_members"] = ["ZIP file could not be opened"]

    return result


def main() -> None:
    timestamp = datetime.now(timezone.utc).isoformat()

    files = sorted([p for p in ASSET_DIR.rglob("*") if p.is_file()])

    inventory = []
    for path in files:
        inventory.append(
            {
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "file_name": path.name,
                "file_size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    master_matches = list(ASSET_DIR.rglob(MASTER_FILE_NAME))
    zip_matches = list(ASSET_DIR.rglob(SUPPORTING_ZIP_PATTERN))

    checks = {
        "verified_at_utc": timestamp,
        "asset_dir": str(ASSET_DIR.relative_to(PROJECT_ROOT)),
        "master_file_found": len(master_matches) > 0,
        "master_file_count": len(master_matches),
        "supporting_zip_found": len(zip_matches) > 0,
        "supporting_zip_count": len(zip_matches),
        "inventory_file_count": len(inventory),
        "inventory": inventory,
        "master_csv_check": None,
        "supporting_zip_checks": [],
    }

    if master_matches:
        master_path = master_matches[0]
        csv_info = count_csv_rows_and_columns(master_path)
        missing_columns = [
            col for col in EXPECTED_MASTER_COLUMNS if col not in csv_info["columns"]
        ]
        extra_columns = [
            col for col in csv_info["columns"] if col not in EXPECTED_MASTER_COLUMNS
        ]

        checks["master_csv_check"] = {
            "path": str(master_path.relative_to(PROJECT_ROOT)),
            "can_read": True,
            "file_size_bytes": master_path.stat().st_size,
            "data_row_count": csv_info["data_row_count"],
            "column_count": csv_info["column_count"],
            "expected_column_count": len(EXPECTED_MASTER_COLUMNS),
            "missing_expected_columns": missing_columns,
            "extra_columns": extra_columns,
            "columns": csv_info["columns"],
        }

    for zip_path in zip_matches:
        checks["supporting_zip_checks"].append(inspect_zip(zip_path))

    json_path = OUTPUT_DIR / "download-integrity-manifest.json"
    md_path = OUTPUT_DIR / "download-integrity-report.md"

    json_path.write_text(json.dumps(checks, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Download Integrity Report")
    lines.append("")
    lines.append(f"Verified at UTC: `{timestamp}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Master CSV found: `{checks['master_file_found']}`")
    lines.append(f"- Supporting ZIP found: `{checks['supporting_zip_found']}`")
    lines.append(f"- Local inventory file count: `{checks['inventory_file_count']}`")
    lines.append("")

    lines.append("## Master CSV Check")
    lines.append("")
    master_check = checks["master_csv_check"]
    if master_check:
        lines.append(f"- Path: `{master_check['path']}`")
        lines.append(f"- File size bytes: `{master_check['file_size_bytes']}`")
        lines.append(f"- Data row count: `{master_check['data_row_count']}`")
        lines.append(f"- Column count: `{master_check['column_count']}`")
        lines.append(f"- Expected column count: `{master_check['expected_column_count']}`")
        lines.append(f"- Missing expected columns: `{master_check['missing_expected_columns']}`")
        lines.append(f"- Extra columns: `{master_check['extra_columns']}`")
    else:
        lines.append("- Master CSV was not found.")
    lines.append("")

    lines.append("## Supporting ZIP Check")
    lines.append("")
    if checks["supporting_zip_checks"]:
        for zip_check in checks["supporting_zip_checks"]:
            lines.append(f"### `{zip_check['zip_path']}`")
            lines.append("")
            lines.append(f"- ZIP can open: `{zip_check['zip_can_open']}`")
            lines.append(f"- ZIP file count: `{zip_check['zip_file_count']}`")
            lines.append(f"- CSV count: `{zip_check['zip_csv_count']}`")
            lines.append(f"- PDF count: `{zip_check['zip_pdf_count']}`")
            lines.append(f"- Bad ZIP members: `{zip_check['bad_zip_members']}`")
            lines.append("")
            lines.append("Files inside ZIP:")
            lines.append("")
            for name in zip_check["zip_files"]:
                lines.append(f"- `{name}`")
            lines.append("")
    else:
        lines.append("- Supporting ZIP was not found.")
        lines.append("")

    lines.append("## Local File Inventory")
    lines.append("")
    for item in inventory:
        lines.append(
            f"- `{item['relative_path']}` | size: `{item['file_size_bytes']}` bytes | sha256: `{item['sha256']}`"
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Download integrity verification complete.")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")

    if not checks["master_file_found"]:
        raise SystemExit("ERROR: Master CSV not found.")

    if not checks["supporting_zip_found"]:
        raise SystemExit("ERROR: Supporting ZIP not found.")

    if checks["master_csv_check"]["missing_expected_columns"]:
        raise SystemExit("ERROR: Master CSV is missing expected columns.")

    for zip_check in checks["supporting_zip_checks"]:
        if not zip_check["zip_can_open"] or zip_check["bad_zip_members"]:
            raise SystemExit("ERROR: Supporting ZIP failed integrity check.")

    print("All required integrity checks passed.")


if __name__ == "__main__":
    main()
