

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from app.database.mongo_connection import get_database
from app.config import Config

router = APIRouter()

# ===========================
# REQUEST MODEL
# ===========================
class SaveResultsRequest(BaseModel):
    year: int
    month: str
    language: str
    results: List[Dict[str, Any]]


# ===========================
# SAVE WER RESULTS
# ===========================
@router.post("/save")
def save_results(data: SaveResultsRequest):
    try:
        db = get_database()

        # Collections
        wer_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
        metadata_col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]
        metrics_col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]

        parameter_hash = f"{data.year}_{data.month}_{data.language}"

        # ===========================
        # SAVE WER RESULTS
        # ===========================
        wer_doc = {
            "parameter_hash": parameter_hash,
            "year": data.year,
            "month": data.month,
            "language": data.language,
            "results": data.results,
            "total_files_processed": len(data.results),
            "last_updated": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }

        wer_col.update_one(
            {"parameter_hash": parameter_hash},
            {"$set": wer_doc},
            upsert=True
        )

        # ===========================
        # SAVE PROCESSING METADATA
        # ===========================
        metadata_doc = {
            "parameter_hash": parameter_hash,
            "year": data.year,
            "month": data.month,
            "language": data.language,
            "processed_file_ids": [
                r.get("google_drive_file_id")
                for r in data.results
                if r.get("google_drive_file_id")
            ],
            "last_sync_timestamp": datetime.utcnow(),
            "last_drive_folder_scan": datetime.utcnow()
        }

        metadata_col.update_one(
            {"parameter_hash": parameter_hash},
            {"$set": metadata_doc},
            upsert=True
        )

        # ===========================
        # SAVE TOOL SUMMARY METRICS
        # ===========================
        tool_stats = {}

        for r in data.results:
            tool = r.get("ai_tool", "unknown")
            wer = float(r.get("wer_score", 0))

            if tool not in tool_stats:
                tool_stats[tool] = []

            tool_stats[tool].append(wer)

        tool_metrics = {}
        for tool, scores in tool_stats.items():
            tool_metrics[tool] = {
                "average_wer": sum(scores) / len(scores),
                "best_wer": min(scores),
                "worst_wer": max(scores),
                "files_count": len(scores)
            }

        metrics_doc = {
            "parameter_hash": parameter_hash,
            "year": data.year,
            "month": data.month,
            "language": data.language,
            "tool_metrics": tool_metrics
        }

        metrics_col.update_one(
            {"parameter_hash": parameter_hash},
            {"$set": metrics_doc},
            upsert=True
        )

        return {
            "status": "success",
            "message": "✅ Data saved to MongoDB successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# GET RESULTS
# ===========================
@router.get("/get")
def get_results(year: int, month: str, language: str):
    try:
        db = get_database()
        collection = db[Config.MONGODB_COLLECTIONS["wer_results"]]

        param_hash = f"{year}_{month}_{language}"

        data = collection.find_one(
            {"parameter_hash": param_hash},
            {"_id": 0}
        )

        return data or {}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))