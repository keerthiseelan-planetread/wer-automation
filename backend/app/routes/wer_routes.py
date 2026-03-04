from fastapi import APIRouter
from app.database import reports_collection
from app.schemas import WERReport

router = APIRouter()

@router.post("/save-report")
def save_report(report: WERReport):
    reports_collection.insert_one(report.dict())
    return {"message": "Report saved successfully"}

@router.get("/get-reports")
def get_reports():
    reports = list(reports_collection.find({}, {"_id": 0}))
    return reports