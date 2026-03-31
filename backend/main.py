from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.middleware.cors import CORSMiddleware
from app.database.init_db import initialize_database
from app.database.db_operations import (
    update_tool_summary_metrics,
    get_tool_summary_metrics
)



app = FastAPI(title="WER Automation API")

# -------------------------------
# STARTUP
# -------------------------------
@app.on_event("startup")
def startup_event():
    initialize_database()

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# SCHEMAS
# -------------------------------
class ToolMetricsRequest(BaseModel):
    year: int
    month: str
    language: str

# ===== COMMENTED OUT ROUTERS - NOT USED FOR WORDPRESS ==========
# from backend.routers.auth_routers import router as auth_router
# from backend.routers.db import router as db_router
# from backend.routers.process import router as process_router
# from backend.routers.results import router as results_router
#
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
# app.include_router(db_router, prefix="/db", tags=["db"])
# app.include_router(process_router, prefix="/process", tags=["process"])
# app.include_router(results_router, prefix="/results", tags=["results"])
# ======================================================================

# =====
# ===== IMPORT & REGISTER ROUTERS =====
from backend.routers.health import router as health_router
from backend.routers.wer_routers import router as wer_router

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(wer_router, prefix="/wer", tags=["wer"])

# ===== END ROUTERS =====


# -------------------------------
# HOME
# -------------------------------
@app.get("/")
def home():
    return {"message": "WER Backend Running 🚀"}

# =========================================================
# ============= WORDPRESS ENDPOINTS ONLY =================
# =========================================================

# -------------------------------------------------------
# TOOL SUMMARY METRICS - FOR WORDPRESS TOP 10 RANKING
# -------------------------------------------------------
@app.post("/api/wer/save-tool-summary-metrics")
def save_tool_summary_metrics_api(request: ToolMetricsRequest):
    """
    Save aggregated tool summary metrics (avg WER per tool).
    Used by WordPress plugin to rank AI tools.
    """
    try:
        # Call the database operation from db_operations.py
        response = update_tool_summary_metrics(
            year=request.year,
            month=request.month,
            language=request.language,
            results=[]  # Results are pre-aggregated in DB
        )

        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["message"])

        return {"status": "success", "message": "Tool summary metrics saved"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wer/get-tool-summary-metrics")
def get_tool_summary_metrics_api(language: str):
    """
    Get aggregated tool summary metrics for a language across ALL months.
    Returns top 10 AI tools ranked by lowest average WER.
    
    Example: /api/wer/get-tool-summary-metrics?language=hi
    """
    try:
        from app.database.mongo_connection import get_database
        from app.config import Config
        
        db = get_database()
        col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]
        
        # Fetch all documents for this language across all months/years
        docs = list(col.find({"language": language}, {"_id": 0}))
        
        if not docs:
            return {
                "status": "warning",
                "message": "No metrics found for this language",
                "data": {}
            }
        
        # Aggregate tool metrics across all months
        aggregated_metrics = {}
        
        for doc in docs:
            tool_metrics = doc.get("tool_metrics", {})
            
            for tool_name, metrics in tool_metrics.items():
                if tool_name not in aggregated_metrics:
                    aggregated_metrics[tool_name] = {
                        "total_wer": 0,
                        "count": 0,
                        "best_wer": float('inf'),
                        "worst_wer": 0,
                        "total_files": 0
                    }
                
                # Aggregate data
                avg_wer = float(metrics.get("average_wer", 0))
                best_wer = float(metrics.get("best_wer", 0))
                worst_wer = float(metrics.get("worst_wer", 0))
                files = metrics.get("files_count", 0)
                
                aggregated_metrics[tool_name]["total_wer"] += avg_wer
                aggregated_metrics[tool_name]["count"] += 1
                aggregated_metrics[tool_name]["best_wer"] = min(
                    aggregated_metrics[tool_name]["best_wer"], best_wer
                )
                aggregated_metrics[tool_name]["worst_wer"] = max(
                    aggregated_metrics[tool_name]["worst_wer"], worst_wer
                )
                aggregated_metrics[tool_name]["total_files"] += files
        
        # Calculate final averages
        final_metrics = {}
        for tool_name, metrics in aggregated_metrics.items():
            final_metrics[tool_name] = {
                "average_wer": round(metrics["total_wer"] / metrics["count"], 2),
                "best_wer": round(metrics["best_wer"], 2),
                "worst_wer": round(metrics["worst_wer"], 2),
                "files_count": metrics["total_files"]
            }
        
        return {
            "status": "success",
            "data": final_metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# ========== COMMENTED OUT - NOT USED FOR WORDPRESS =====
# =========================================================

# 🔴 SAVE WER RESULTS - COMMENTED OUT
# @app.post("/api/wer/save-wer-results")
# def save_wer_results_api(request: SaveWERResultsRequest):
#     """
#     DEPRECATED: Individual WER results no longer saved.
#     Use save_tool_summary_metrics instead.
#     """
#     pass


# 🔴 GET WER RESULTS - COMMENTED OUT
# @app.get("/api/wer/get-wer-results")
# def get_wer_results_api(
#     year: Optional[int] = None,
#     month: Optional[str] = None,
#     language: Optional[str] = None
# ):
#     """
#     DEPRECATED: Individual WER results no longer fetched.
#     Use get_tool_summary_metrics instead.
#     """
#     pass


# 🔴 SAVE PERFORMANCE METADATA - COMMENTED OUT
# @app.post("/api/wer/save-performance-metadata")
# def save_metadata(request: PerformanceMetadataRequest):
#     """
#     DEPRECATED: Performance metadata no longer saved.
#     """
#     pass


# 🔴 GET PERFORMANCE METADATA - COMMENTED OUT
# @app.get("/api/wer/get-performance-metadata")
# def get_performance_metadata_api(year: int, month: str, language: str):
#     """
#     DEPRECATED: Performance metadata no longer fetched.
#     """
#     pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
