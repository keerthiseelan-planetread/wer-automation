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
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from app.database.mongo_connection import get_database
from app.database.init_db import initialize_database
from app.config import Config
from app.database.db_operations import (
    save_wer_results,
    update_processing_metadata,
    update_tool_summary_metrics,
    get_wer_results,
    get_processing_metadata,
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

from pydantic import BaseModel
class ToolMetricsRequest(BaseModel):
    year: int
    month: str
    language: str



# -------------------------------
# HOME
# -------------------------------
@app.get("/")
def home():
    return {"message": "WER Backend Running 🚀"}

# =========================================================
# ------------------ POST APIs -----------------------------
# =========================================================

# 1️⃣ SAVE WER RESULTS


# -------------------------------
# SAVE WER RESULTS API (FIXED)
# -------------------------------
@app.post("/api/wer/save-wer-results")
def save_wer_results_api(request: SaveWERResultsRequest):

    print("🔥 RECEIVED:", request)

    if not request.results:
        raise HTTPException(status_code=400, detail="Results list is empty ❌")

    response = save_wer_results(
        year=request.year,
        month=request.month,
        language=request.language,
        wer_results_list=[
            {
                "base_name": r.base_name,
                "ai_tool": r.ai_tool,
                "wer_score": r.wer_score,

                # ✅ FIX: DO NOT FORCE EMPTY STRING
                "google_drive_file_id": r.google_drive_file_id
            }
            for r in request.results
        ]
    )

    if not response["success"]:
        print("❌ ERROR FROM DB:", response)
        raise HTTPException(status_code=500, detail=response["message"])

    return {"status": "success", "message": "WER results saved"}



# 2️⃣ SAVE METADATA
@app.post("/api/wer/save-performance-metadata")
def save_metadata(request: PerformanceMetadataRequest):

    response = update_processing_metadata(
        year=request.year,
        month=request.month,
        language=request.language,
        file_ids=request.processed_file_ids
    )

    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["message"])

    return {"status": "success", "message": "Metadata saved"}


# 3️⃣ SAVE TOOL METRICS (AUTO)
@app.post("/api/wer/save-tool-summary-metrics")
def save_tool_metrics(request: ToolMetricsRequest):

    results = get_wer_results(
        year=request.year,
        month=request.month,
        language=request.language
    )

    if not results:
        return {"status": "warning", "message": "No results found"}

    response = update_tool_summary_metrics(
        year=request.year,
        month=request.month,
        language=request.language,
        results=results
    )

    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["message"])

    return {"status": "success", "message": "Metrics saved"}

# =========================================================
# ------------------ GET APIs ------------------------------
# =========================================================



# @app.get("/api/wer/get-wer-results")
# def get_results(year: int, month: str, language: str):
#     return {"data": get_wer_results(year, month, language)}


# @app.get("/api/wer/get-performance-metadata")
# def get_metadata(year: int, month: str, language: str):
#     return {"data": get_processing_metadata(year, month, language)}


# @app.get("/api/wer/get-tool-summary-metrics")
# def get_metrics(year: int, month: str, language: str):
#     return {"data": get_tool_summary_metrics(year, month, language)}

from fastapi import HTTPException
from typing import Optional
import os

@app.get("/api/wer/get-wer-results")
def get_wer_results_api(
    year: Optional[int] = None,
    month: Optional[str] = None,
    language: Optional[str] = None
):
    try:
        db = get_database()
        col = db[Config.MONGODB_COLLECTIONS["wer_results"]]

        query = {}
       
        if year:
            query["year"] = year
        if month:
            query["month"] = month
        if language:
            query["language"] = language

        docs = list(col.find(query, {"_id": 0}))
        final_data = []

        for doc in docs:
            for r in doc.get("results", []):

                file_name = r.get("file_name", "")
                base_name = os.path.splitext(file_name)[0] if file_name else "N/A"

                final_data.append({
                    "language": doc.get("language"),
                    "year": doc.get("year"),
                    "month": doc.get("month"),

                    # ✅ IMPORTANT
                    "file_name": file_name,
                    "base_name": base_name,
                    "base_name":doc.get("base_name", base_name),  # Try to get from doc, fallback to extracted base_name
                    "ai_tool": r.get("ai_tool"),
                    "wer_score": r.get("wer_score")
                })

        return {
            "status": "success",
            "count": len(final_data),
            "data": final_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/wer/get-performance-metadata")
def get_performance_metadata_api(year: int, month: str, language: str):
    try:
        data = get_processing_metadata(year, month, language)

        if not data:
            return {
                "status": "warning",
                "message": "No metadata found",
                "data": {}
            }

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:
        print("❌ ERROR in get-performance-metadata:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/wer/get-tool-summary-metrics")
def get_tool_summary_metrics_api(year: int, month: str, language: str):
    try:
        data = get_tool_summary_metrics(year, month, language)

        if not data:
            return {
                "status": "warning",
                "message": "No metrics found",
                "data": {}
            }

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:
        print("❌ ERROR in get-tool-summary-metrics:", e)
        raise HTTPException(status_code=500, detail=str(e))