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
    Get tool summary metrics for selected language.
    Auto-detects current month and fetches data.
    If no data for current month, searches backwards through previous months
    until the latest available data is found (up to 13 months back).
    Uses case-insensitive language search for better matching.
    
    Example: /api/wer/get-tool-summary-metrics?language=Hindi
    """
    try:
        from app.database.mongo_connection import get_database
        from app.config import Config
        from datetime import datetime, timedelta
        
        def get_previous_month(date):
            """Get the first day of the previous month"""
            first_of_current = date.replace(day=1)
            last_of_previous = first_of_current - timedelta(days=1)
            return last_of_previous.replace(day=1)
        
        db = get_database()
        col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]
        
        # Get current month and year
        now = datetime.now()
        doc = None
        search_date = now
        
        # Loop backwards to find the latest available data (up to 13 months back)
        for _ in range(13):
            search_month = search_date.strftime("%B")
            search_year = search_date.year
            
            doc = col.find_one({
                "language": {"$regex": f"^{language}$", "$options": "i"},  # Case-insensitive
                "year": search_year,
                "month": search_month
            }, {"_id": 0})
            
            if doc:
                # Found data, stop searching
                break
            
            # Move to previous month
            search_date = get_previous_month(search_date)
        
        # If no data found after searching 13 months back
        if not doc:
            return {
                "status": "warning",
                "message": f"No metrics found for {language} in the last 13 months",
                "data": {}
            }
        
        # Get tool metrics and sort by avg_wer (lower WER = higher rank)
        tool_metrics = doc.get("tool_metrics", {})
        
        # Convert to list of tuples and sort by avg_wer (ascending)
        sorted_tools = sorted(
            tool_metrics.items(),
            key=lambda x: x[1].get("avg_wer", float('inf'))
        )
        
        # Create ranked data structure
        ranked_data = []
        for rank, (tool_name, metrics) in enumerate(sorted_tools, start=1):
            ranked_data.append({
                "rank": rank,
                "tool": tool_name,
                "avg_wer": metrics.get("avg_wer"),
                "total_evaluations": metrics.get("total_evaluations")
            })
        
        return {
            "status": "success",
            "month": doc.get("month"),
            "year": doc.get("year"),
            "language": doc.get("language"),
            "data": ranked_data
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

