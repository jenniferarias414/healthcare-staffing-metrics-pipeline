#!/usr/bin/env python3
"""
AWS Glue Python Shell job: ingest Google Drive source files to S3 raw.

This script is an AWS-ready ingestion design for the approved architecture. It
keeps credentials out of source control, reads Google Drive file metadata,
compares that metadata to an S3 JSON manifest, downloads only files that are
new, changed, or previously failed, and updates the manifest with the result.

Expected Glue job arguments:
  --source_folder_id
  --raw_bucket
  --raw_prefix
  --manifest_key
  --google_credentials_secret_name

Google Drive authentication is intentionally isolated in build_drive_service().
If this runs as a Glue Python Shell job, package google-api-python-client and
google-auth dependencies with the job or provide them through a Glue Python
library path.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from typing import Any

import boto3
from awsglue.utils import getResolvedOptions


STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"
STATUS_SKIPPED = "SKIPPED"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> dict[str, str]:
    return getResolvedOptions(
        sys.argv,
        [
            "source_folder_id",
            "raw_bucket",
            "raw_prefix",
            "manifest_key",
            "google_credentials_secret_name",
        ],
    )


def read_secret(secret_name: str) -> dict[str, Any]:
    secrets = boto3.client("secretsmanager")
    response = secrets.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def build_drive_service(secret_name: str):
    """
    Build and return an authenticated Google Drive client.

    Run note:
    - Store the service account JSON or OAuth client material in AWS Secrets
      Manager.
    - Package google.oauth2.service_account and googleapiclient.discovery with
      the Glue Python Shell job.
    - Do not hardcode credentials in this repository.
    """
    credentials_info = read_secret(secret_name)

    # Real deployment example:
    #
    # from google.oauth2 import service_account
    # from googleapiclient.discovery import build
    #
    # scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    # credentials = service_account.Credentials.from_service_account_info(
    #     credentials_info,
    #     scopes=scopes,
    # )
    # return build("drive", "v3", credentials=credentials, cache_discovery=False)

    raise NotImplementedError(
        "Configure Google Drive client libraries in the Glue Python Shell job "
        "and return a Drive v3 service from build_drive_service(). "
        f"Loaded secret fields: {sorted(credentials_info.keys())}"
    )


def read_manifest(s3_client, bucket: str, key: str) -> dict[str, Any]:
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
    except s3_client.exceptions.NoSuchKey:
        return {"files": {}}
    except Exception as exc:
        if getattr(exc, "response", {}).get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
            return {"files": {}}
        raise
    return json.loads(response["Body"].read().decode("utf-8"))


def write_manifest(s3_client, bucket: str, key: str, manifest: dict[str, Any]) -> None:
    manifest["updated_at_utc"] = utc_now()
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(manifest, indent=2).encode("utf-8"),
        ContentType="application/json",
    )


def list_drive_files(drive_service, folder_id: str) -> list[dict[str, Any]]:
    """
    Return file metadata from the configured Google Drive folder.

    Fields used for incremental loading:
    - id
    - name
    - modifiedTime
    - size
    - md5Checksum, when Google Drive provides it
    """
    query = f"'{folder_id}' in parents and trashed = false"
    files: list[dict[str, Any]] = []
    page_token = None
    while True:
        response = (
            drive_service.files()
            .list(
                q=query,
                fields="nextPageToken, files(id, name, modifiedTime, size, md5Checksum, mimeType)",
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            return files


def file_changed(metadata: dict[str, Any], manifest_record: dict[str, Any] | None) -> bool:
    if not manifest_record:
        return True
    if manifest_record.get("processing_status") == STATUS_FAILED:
        return True
    return any(
        str(metadata.get(source_field, "")) != str(manifest_record.get(manifest_field, ""))
        for source_field, manifest_field in [
            ("id", "source_file_id"),
            ("modifiedTime", "google_drive_modified_time"),
            ("size", "file_size_bytes"),
            ("md5Checksum", "checksum"),
        ]
    )


def download_drive_file(drive_service, file_id: str) -> bytes:
    """
    Download one file from Google Drive.

    This uses the Drive v3 media download pattern. Export-only Google Docs files
    would need a separate export_media branch; the project source files are CSV
    and ZIP files, so get_media is the expected path.
    """
    # Real deployment example:
    #
    # from googleapiclient.http import MediaIoBaseDownload
    #
    # request = drive_service.files().get_media(fileId=file_id, supportsAllDrives=True)
    # buffer = io.BytesIO()
    # downloader = MediaIoBaseDownload(buffer, request)
    # done = False
    # while not done:
    #     _, done = downloader.next_chunk()
    # return buffer.getvalue()

    raise NotImplementedError("Enable googleapiclient MediaIoBaseDownload in the Glue job package.")


def raw_key(raw_prefix: str, file_name: str, batch_id: str) -> str:
    prefix = raw_prefix.strip("/")
    return f"{prefix}/google_drive/batch_id={batch_id}/{file_name}"


def checksum_bytes(payload: bytes) -> str:
    return hashlib.md5(payload).hexdigest()


def process_file(
    s3_client,
    drive_service,
    bucket: str,
    raw_prefix: str,
    batch_id: str,
    metadata: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    file_id = metadata["id"]
    existing = manifest.setdefault("files", {}).get(file_id)

    if not file_changed(metadata, existing):
        manifest["files"][file_id] = {
            **existing,
            "processing_status": STATUS_SKIPPED,
            "last_checked_at_utc": utc_now(),
        }
        return

    record = {
        "source_file_id": file_id,
        "source_file_name": metadata.get("name"),
        "source_system": "google_drive",
        "google_drive_modified_time": metadata.get("modifiedTime"),
        "file_size_bytes": metadata.get("size"),
        "checksum": metadata.get("md5Checksum"),
        "batch_id": batch_id,
        "last_checked_at_utc": utc_now(),
    }

    try:
        payload = download_drive_file(drive_service, file_id)
        record["checksum"] = metadata.get("md5Checksum") or checksum_bytes(payload)
        key = raw_key(raw_prefix, metadata["name"], batch_id)
        s3_client.put_object(Bucket=bucket, Key=key, Body=payload)
        record.update(
            {
                "s3_raw_path": f"s3://{bucket}/{key}",
                "processing_status": STATUS_SUCCESS,
                "loaded_at_utc": utc_now(),
                "error_message": None,
            }
        )
    except Exception as exc:
        record.update(
            {
                "processing_status": STATUS_FAILED,
                "loaded_at_utc": None,
                "error_message": str(exc),
            }
        )

    manifest["files"][file_id] = record


def main() -> None:
    args = parse_args()
    s3_client = boto3.client("s3")
    drive_service = build_drive_service(args["google_credentials_secret_name"])
    manifest = read_manifest(s3_client, args["raw_bucket"], args["manifest_key"])
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    for metadata in list_drive_files(drive_service, args["source_folder_id"]):
        process_file(
            s3_client=s3_client,
            drive_service=drive_service,
            bucket=args["raw_bucket"],
            raw_prefix=args["raw_prefix"],
            batch_id=batch_id,
            metadata=metadata,
            manifest=manifest,
        )

    write_manifest(s3_client, args["raw_bucket"], args["manifest_key"], manifest)


if __name__ == "__main__":
    main()
