
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