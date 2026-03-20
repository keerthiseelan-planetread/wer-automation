# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from typing import List, Dict, Any

# from backend.core.security import get_current_user
# from app.database.db_operations import save_wer_results, get_all_results_for_parameters, fetch_processed_file_ids
# from app.database.mongo_connection import get_database
# from app.config import Config

# router = APIRouter()


# class SaveResultsRequest(BaseModel):
#     year: int
#     month: str
#     language: str
#     results: List[Dict[str, Any]]


# @router.post("/save-results")
# def save_results(request: SaveResultsRequest, user=Depends(get_current_user)):
#     """
#     Save WER results to DB. Call this route to store data.
#     """
#     success = save_wer_results(
#         year=request.year,
#         month=request.month,
#         language=request.language,
#         wer_results_list=request.results
#     )
#     if success.get("success"):
#         return {"message": "Results saved successfully"}
#     else:
#         raise HTTPException(status_code=500, detail=success.get("message", "Save failed"))


# @router.get("/get-results/{year}/{month}/{language}")
# def get_results(year: int, month: str, language: str, user=Depends(get_current_user)):
#     """
#     Fetch WER results from DB for given params.
#     """
#     results = get_all_results_for_parameters(year=year, month=month, language=language)
#     return {"results": results}


# @router.get("/processed-files/{year}/{month}/{language}")
# def get_processed_files(year: int, month: str, language: str, user=Depends(get_current_user)):
#     """
#     Get list of processed file IDs from DB.
#     """
#     file_ids = fetch_processed_file_ids(year=year, month=month, language=language)
#     return {"processed_file_ids": file_ids}


# # @router.get("/db-info")
# # def db_info(user=Depends(get_current_user)):
# #     """
# #     Get DB connection info and collection names.
# #     """
# #     db = get_database()
# #     collections = db.list_collection_names()
# #     return {
# #         "db_name": Config.MONGODB_DB_NAME,
# #         "collections": collections,
# #         "uri": Config.MONGODB_URI[:50] + "..."  # Masked for security
# #     }
# @router.get("/")
# def root_db(user=Depends(get_current_user)):
#     """
#     Get DB connection info and collection names.
#     """
#     db = get_database()
#     collections = db.list_collection_names()
#     return {
#         "db_name": Config.MONGODB_DB_NAME,
#         "collections": collections,
#         "uri": Config.MONGODB_URI[:50] + "..."
#     }

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