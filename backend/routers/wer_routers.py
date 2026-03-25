# from fastapi import APIRouter, HTTPException
# from typing import List, Dict

# from app.database.db_operations import (
#     save_wer_results,
#     get_all_results_for_parameters,
#     update_processing_metadata,
#     get_tool_summary_metrics
# )

# router = APIRouter()

# # ✅ SAVE DATA
# @router.post("/save")
# def save_results(data: Dict):
#     try:
#         result = save_wer_results(
#             data["year"],
#             data["month"],
#             data["language"],
#             data["results"]
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ✅ GET DATA
# @router.get("/get")
# def get_results(year: int, month: str, language: str):
#     try:
#         results = get_all_results_for_parameters(year, month, language)
#         return {"results": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ✅ UPDATE METADATA
# @router.post("/metadata")
# def update_metadata(data: Dict):
#     try:
#         return update_processing_metadata(
#             data["year"],
#             data["month"],
#             data["language"],
#             data["file_ids"]
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ✅ TOOL METRICS
# @router.get("/metrics")
# def get_metrics(year: int, month: str, language: str):
#     return get_tool_summary_metrics(year, month, language)

from fastapi import APIRouter, HTTPException
from app.database.mongo_connection import get_database

router = APIRouter(
    prefix="/api/wer",
    tags=["WER"]
)

db = get_database()

wer_results_col = db["wer_results"]
performance_col = db["performance_metrics"]
tool_metrics_col = db["tool_metrics"]


@router.post("/save-results")
def save_wer_results(payload: dict):
    try:
        wer_results_col.insert_one(payload)
        return {"status": "success", "message": "WER results saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-performance")
def save_performance_metrics(payload: dict):
    try:
        performance_col.insert_one(payload)
        return {"status": "success", "message": "Performance metrics saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-tool-metrics")
def save_tool_metrics(payload: dict):
    try:
        tool_metrics_col.insert_one(payload)
        return {"status": "success", "message": "Tool metrics saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))