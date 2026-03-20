# # from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware

# # from backend.routers import auth, health, process, results, db  # Added 'db'
# # from backend.core.config import settings

# # app = FastAPI(
# #     title="WER Automation API",
# #     version="1.0.0",
# #     description="Backend API for WER Automation (MongoDB + Drive + WER calculator)",
# # )

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=settings.CORS_ORIGINS,
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# # app.include_router(health.router, prefix="/api/health", tags=["health"])
# # app.include_router(process.router, prefix="/api/process", tags=["process"])
# # app.include_router(results.router, prefix="/api/results", tags=["results"])
# # # ✅ Correct prefix for DB router
# # app.include_router(db.router, prefix="/api/db", tags=["WER Results"])


# from fastapi import FastAPI, HTTPException
# from datetime import datetime
# from app.database.mongo_connection import get_database
# from app.database.init_db import initialize_database
# from app.config import Config

# app = FastAPI()

# # Initialize DB at startup
# @app.on_event("startup")
# def startup():
#     initialize_database()

# @app.get("/")
# def home():
#     return {"message": "FastAPI is working 🚀"}

# # ✅ STORE WER RESULT
# @app.post("/store/wer")
# def store_wer(data: dict):
#     try:
#         db = get_database()
#         collection = db[Config.MONGODB_COLLECTIONS["wer_results"]]

#         data["last_updated"] = datetime.utcnow()

#         result = collection.insert_one(data)

#         return {
#             "message": "WER data stored successfully",
#             "id": str(result.inserted_id)
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ✅ FETCH WER RESULTS
# @app.get("/fetch/wer")
# def fetch_wer():
#     try:
#         db = get_database()
#         collection = db[Config.MONGODB_COLLECTIONS["wer_results"]]

#         data = list(collection.find({}, {"_id": 0}))

#         return data

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ✅ STORE METADATA
# @app.post("/store/metadata")
# def store_metadata(data: dict):
#     try:
#         db = get_database()
#         collection = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]

#         result = collection.insert_one(data)

#         return {"message": "Metadata stored", "id": str(result.inserted_id)}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ✅ FETCH METADATA
# @app.get("/fetch/metadata")
# def fetch_metadata():
#     try:
#         db = get_database()
#         collection = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]

#         data = list(collection.find({}, {"_id": 0}))
#         return data

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware
# Assume these DB functions exist
from app.database.init_db import initialize_database
from app.database.db_operations import (
    save_wer_results,
    update_processing_metadata,
    update_tool_summary_metrics,
    get_wer_results,
    get_processing_metadata,
    get_tool_summary_metrics
)

# -------------------------------
# CREATE APP
# -------------------------------
app = FastAPI(title="WER Automation API")

# -------------------------------
# STARTUP EVENT
# -------------------------------
@app.on_event("startup")
def startup_event():
    initialize_database()

# -------------------------------
# SCHEMAS
# -------------------------------
class WERResult(BaseModel):
    base_name: str
    ai_tool: str
    wer_score: float
    google_drive_file_id: Optional[str] = ""

class SaveWERResultsRequest(BaseModel):
    year: int
    month: str
    language: str
    results: List[WERResult]

class PerformanceMetadataRequest(BaseModel):
    year: int
    month: str
    language: str
    processed_file_ids: List[str]

class ToolMetric(BaseModel):
    average_wer: float
    best_wer: float
    worst_wer: float
    total_files: int

class ToolMetricsRequest(BaseModel):
    year: int
    month: str
    language: str
    tool_metrics: Dict[str, ToolMetric]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# HOME
# -------------------------------
@app.get("/")
def home():
    return {"message": "WER Backend API Running 🚀"}

# -------------------------------
# 1️⃣ SAVE WER RESULTS
# -------------------------------
@app.post("/api/wer/save-wer-results")
def save_wer_results_api(request: SaveWERResultsRequest):
    response = save_wer_results(
        year=request.year,
        month=request.month,
        language=request.language,
        wer_results_list=[
            {
                "base_name": r.base_name,
                "ai_tool": r.ai_tool,
                "wer_score": r.wer_score,
                "google_drive_file_id": r.google_drive_file_id or ""
            }
            for r in request.results
        ]
    )

    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["message"])

    return {"status": "success", "message": "WER results saved successfully"}

# -------------------------------
# 2️⃣ SAVE PROCESSING METADATA
# -------------------------------
@app.post("/api/wer/save-performance-metadata")
def save_performance_metadata(request: PerformanceMetadataRequest):
    response = update_processing_metadata(
        year=request.year,
        month=request.month,
        language=request.language,
        file_ids=request.processed_file_ids
    )

    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["message"])

    return {"status": "success", "message": "Performance metadata saved"}

# -------------------------------
# 3️⃣ SAVE TOOL SUMMARY METRICS
# -------------------------------
@app.post("/api/wer/save-tool-summary-metrics")
def save_tool_summary_metrics_api(request: ToolMetricsRequest):
    try:
        # Prepare tool_metrics dict
        tool_metrics_dict = {
            tool: {
                "average_wer": metric.average_wer,
                "best_wer": metric.best_wer,
                "worst_wer": metric.worst_wer,
                "total_files": metric.total_files
            }
            for tool, metric in request.tool_metrics.items()
        }

        # Call DB function with all required parameters
        response = update_tool_summary_metrics(
            year=request.year,
            month=request.month,
            language=request.language,
            tool_metrics=tool_metrics_dict
        )

        if not response.get("success", False):
            raise HTTPException(status_code=500, detail=response.get("message", "Unknown error"))

        return {"status": "success", "message": "Tool summary metrics saved/updated"}

    except Exception as e:
        print("❌ ERROR in save-tool-summary-metrics:", e)
        raise HTTPException(status_code=500, detail=str(e))


        # =========================================================
# ------------------ GET APIs ------------------------------
# =========================================================

# 4️⃣ GET WER RESULTS
# -------------------------------
# GET WER RESULTS (IMPORTANT)
# -------------------------------
from fastapi import HTTPException
from app.database.mongo_connection import get_database
from app.config import Config

@app.get("/api/wer/get-wer-results")
def get_wer_results_api(year: int = None, month: str = None, language: str = None):
    try:
        db = get_database()

        if db is None:
            raise Exception("Database connection failed")

        col_name = Config.MONGODB_COLLECTIONS.get("wer_results")

        if not col_name:
            raise Exception("Collection name not found in config")

        col = db[col_name]

        # ✅ Build query safely
        query = {}
        if year:
            query["year"] = year
        if month:
            query["month"] = month
        if language:
            query["language"] = language

        print("DEBUG QUERY:", query)

        docs = list(col.find(query, {"_id": 0}))

        print("DB DOCS:", docs)

        final_data = []

        for doc in docs:
            results = doc.get("results", [])

            # ✅ Ensure it's a list
            if not isinstance(results, list):
                continue

            for item in results:
                final_data.append({
                    "language": doc.get("language", ""),
                    "year": doc.get("year", ""),
                    "month": doc.get("month", ""),
                    "base_name": item.get("base_name", ""),
                    "ai_tool": item.get("ai_tool", ""),
                    "wer_score": item.get("wer_score", "")
                })

        return {
            "status": "success",
            "data": final_data
        }

    except Exception as e:
        print("❌ ERROR:", str(e))   # 🔥 IMPORTANT
        raise HTTPException(status_code=500, detail=str(e))
        
# 5️⃣ GET PROCESSING METADATA
@app.get("/api/wer/get-performance-metadata")
def get_performance_metadata_api(year: int, month: str, language: str):
    try:
        data = get_processing_metadata(year, month, language)

        if not data:
            return {"status": "success", "data": {}, "message": "No metadata found"}

        return {"status": "success", "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 6️⃣ GET TOOL SUMMARY METRICS
@app.get("/api/wer/get-tool-summary-metrics")
def get_tool_summary_metrics_api(year: int, month: str, language: str):
    try:
        data = get_tool_summary_metrics(year, month, language)

        if not data:
            return {"status": "success", "data": {}, "message": "No metrics found"}

        return {"status": "success", "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))