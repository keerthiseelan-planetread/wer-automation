from fastapi import FastAPI, HTTPException
from app.database import report_collection
from app.schemas import WERReport
from datetime import datetime

app = FastAPI()

@app.post("/api/wer/save-report")
async def save_report(report: WERReport):
    try:
        report_data = report.dict()
        report_data["created_at"] = datetime.utcnow()

        result = report_collection.insert_one(report_data)

        return {
            "message": "Report saved successfully",
            "report_id": str(result.inserted_id)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wer/reports")
async def get_reports():
    reports = list(report_collection.find({}, {"_id": 0}))
    return reports