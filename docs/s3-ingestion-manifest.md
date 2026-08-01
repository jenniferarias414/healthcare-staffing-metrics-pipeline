# S3 Ingestion Manifest

## Purpose

The S3 ingestion manifest tracks the Google Drive source files that have been checked and loaded into the S3 raw zone.

The manifest gives the ingestion job a simple way to identify files that are new, changed, already loaded, or previously failed.

This keeps the first version of the pipeline simple and avoids adding another database service just for file tracking.

## Manifest Location

Example location:

```text
s3://healthcare-staffing-pipeline/manifest/ingestion_manifest.json
```

For local development, the manifest can also be represented as a local JSON file before being moved to S3.

## Suggested Fields

| Field | Purpose |
|---|---|
| `source_file_id` | Unique Google Drive file ID, if available |
| `source_file_name` | Human-readable source file name |
| `source_system` | Source system name, such as `google_drive` |
| `google_drive_modified_time` | Last modified timestamp from Google Drive metadata |
| `file_size_bytes` | File size used as a change-detection signal |
| `checksum` | File fingerprint used to detect content changes, if available |
| `s3_raw_path` | Location where the raw file was written in S3 |
| `batch_id` | Pipeline run that loaded or attempted the file |
| `processing_status` | Current status for the file load |
| `loaded_at` | Time the file was successfully loaded |
| `error_message` | Failure message if ingestion did not complete |

## Processing Status Values

| Status | Meaning |
|---|---|
| `PENDING` | File has been identified for loading |
| `IN_PROGRESS` | Ingestion job is currently attempting to load the file |
| `SUCCESS` | File was successfully written to S3 raw |
| `FAILED` | File failed during download, upload, or validation |
| `SKIPPED` | File was already loaded and has not changed |

## Incremental Logic

The Glue Python Shell ingestion job performs the incremental logic:

1. Read the current file list and metadata from Google Drive.
2. Read the existing ingestion manifest from S3.
3. Compare each current source file to the stored manifest record.
4. Load the file if it is new, changed, or previously failed.
5. Skip the file if it already loaded successfully and has not changed.
6. Write loaded files to the S3 raw zone.
7. Update the manifest with the latest status, batch ID, S3 path, timestamps, and errors.

## Example Manifest Record

```json
{
  "source_file_id": "1abc123",
  "source_file_name": "PBJ_Daily_Nurse_Staffing_Q2_2024.csv",
  "source_system": "google_drive",
  "google_drive_modified_time": "2024-07-15T18:42:10Z",
  "file_size_bytes": 219661827,
  "checksum": "2d85abc...",
  "s3_raw_path": "s3://healthcare-staffing-pipeline/raw/google_drive/pbj_daily_staffing/batch_id=20260801_070000/PBJ_Daily_Nurse_Staffing_Q2_2024.csv",
  "batch_id": "20260801_070000",
  "processing_status": "SUCCESS",
  "loaded_at": "2026-08-01T07:04:45Z",
  "error_message": null
}
```

## Failure Recovery

If ingestion fails, the manifest keeps the failed status and error message so the file can be retried in a later run.

If transformation fails after the file already landed in S3 raw, the pipeline can rerun the Glue PySpark transformation from the preserved raw file instead of downloading the file again from Google Drive.

## Summary

The S3 manifest gives the ingestion step lightweight file tracking.

It helps the pipeline know what already loaded, what changed, what failed, and what should be retried.
