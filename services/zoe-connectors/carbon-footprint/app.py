import hashlib
import os
from datetime import datetime, timezone
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import bigquery

app = FastAPI(title="Z1 Carbon Footprint Connector", version="1.0.0")

CARBON_TRANSFER_SOURCE = "61cede5a-0000-2440-ad42-883d24f8f7b8"
TRANSFER_BASE = "https://bigquerydatatransfer.googleapis.com/v1"

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
DATASET = os.environ.get("CARBON_BQ_DATASET", "z1_carbon")
BILLING_ACCOUNTS = [x.strip() for x in os.environ.get("CARBON_BILLING_ACCOUNTS", "").split(",") if x.strip()]


def _credentials():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not creds.valid:
        creds.refresh(Request())
    return creds


def create_transfer_config() -> dict[str, Any]:
    if not PROJECT_ID:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT/GCP_PROJECT is required")
    if not BILLING_ACCOUNTS:
        raise RuntimeError("CARBON_BILLING_ACCOUNTS is required")

    creds = _credentials()
    url = f"{TRANSFER_BASE}/projects/{PROJECT_ID}/locations/us/transferConfigs"
    payload = {
        "dataSourceId": CARBON_TRANSFER_SOURCE,
        "displayName": "Z1 Carbon Footprint",
        "params": {"billing_accounts": ",".join(BILLING_ACCOUNTS)},
        "destinationDatasetId": DATASET,
    }
    response = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {creds.token}"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(f"Carbon transfer creation failed: {response.status_code} {response.text}")
    return response.json()


def start_backfill(transfer_config: str, start_time: str, end_time: str) -> dict[str, Any]:
    creds = _credentials()
    url = f"{TRANSFER_BASE}/{transfer_config}:startManualRuns"
    response = requests.post(
        url,
        json={"requestedTimeRange": {"startTime": start_time, "endTime": end_time}},
        headers={"Authorization": f"Bearer {creds.token}"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(f"Carbon backfill failed: {response.status_code} {response.text}")
    return response.json()


def query_carbon(limit: int = 100) -> list[dict[str, Any]]:
    if not PROJECT_ID:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT/GCP_PROJECT is required")
    client = bigquery.Client(project=PROJECT_ID)
    table = f"`{PROJECT_ID}.{DATASET}.carbon_footprint`"
    sql = f"""
    SELECT
      CAST(usage_month AS STRING) AS usage_month,
      billing_account_id,
      project.id AS project_id,
      CAST(project.number AS STRING) AS project_number,
      project.name AS project_name,
      service.id AS service_id,
      service.description AS service_description,
      location.location AS region,
      carbon_footprint_kgCO2e.scope1 AS scope1_kgco2e,
      carbon_footprint_kgCO2e.scope2.market_based AS scope2_market_based_kgco2e,
      carbon_footprint_kgCO2e.scope2.location_based AS scope2_location_based_kgco2e,
      carbon_footprint_kgCO2e.scope3 AS scope3_kgco2e,
      carbon_footprint_total_kgCO2e.location_based AS total_location_based_kgco2e,
      carbon_footprint_total_kgCO2e.market_based AS total_market_based_kgco2e,
      carbon_footprint_total_kgCO2e.after_offsets AS total_after_offsets_kgco2e
    FROM {table}
    ORDER BY usage_month DESC
    LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", limit)]
    )
    return [dict(row) for row in client.query(sql, job_config=job_config).result()]


def row_hash(row: dict[str, Any]) -> str:
    stable = "|".join(str(row.get(k, "")) for k in sorted(row))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "z1-carbon-footprint-connector",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/v1/carbon/latest")
def latest(limit: int = 100) -> dict[str, Any]:
    try:
        rows = query_carbon(max(1, min(limit, 1000)))
        return {
            "status": "ok",
            "source": "google-cloud-carbon-footprint",
            "dataset": DATASET,
            "count": len(rows),
            "rows": rows,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/v1/carbon/export")
def export() -> dict[str, Any]:
    try:
        return create_transfer_config()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/v1/carbon/backfill")
def backfill(
    transfer_config: str,
    start_time: str,
    end_time: str,
) -> dict[str, Any]:
    try:
        return start_backfill(transfer_config, start_time, end_time)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
