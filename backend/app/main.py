# from fastapi import FastAPI, HTTPException
# from app.database import report_collection
# from app.schemas import WERReport
# from datetime import datetime

# app = FastAPI()

# @app.post("/api/wer/save-report")
# async def save_report(report: WERReport):
#     try:
#         report_data = report.dict()
#         report_data["created_at"] = datetime.utcnow()

#         result = report_collection.insert_one(report_data)

#         return {
#             "message": "Report saved successfully",
#             "report_id": str(result.inserted_id)
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/api/wer/reports")
# async def get_reports():
#     reports = list(report_collection.find({}, {"_id": 0}))
#     return reports

# from fastapi import FastAPI, HTTPException
# from app.database import report_collection
# from app.schemas import WERReport
# from datetime import datetime
# from bson import ObjectId

# app = FastAPI()

# @app.post("/api/wer/save-report")
# async def save_report(report: WERReport):
#     try:
#         report_data = report.dict()

#         existing_report = report_collection.find_one({
#             "language": report.language,
#             "year": report.year,
#             "month": report.month
#         })

#         if existing_report:
#             report_collection.update_one(
#                 {
#                     "language": report.language,
#                     "year": report.year,
#                     "month": report.month
#                 },
#                 {
#                     "$push": {
#                         "detailed_results": {
#                             "$each": report.detailed_results
#                         },
#                         "tool_wise_metrics": {
#                             "$each": report.tool_wise_metrics
#                         }
#                     },
#                     "$set": {
#                         "performance_summary": report.performance_summary,  # ✅ FIXED
#                         "updated_at": datetime.utcnow()
#                     }
#                 }
#             )

#             return {"message": "Existing report updated successfully"}

#         else:
#             report_data["created_at"] = datetime.utcnow()
#             report_collection.insert_one(report_data)

#             return {"message": "New report saved successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, HTTPException
from app.database import report_collection
from app.schemas import WERReport
from datetime import datetime

app = FastAPI()

@app.post("/api/wer/save-report")
async def save_report(report: WERReport):
    try:
        report_data = report.dict()

        existing_report = report_collection.find_one({
            "language": report.language,
            "year": report.year,
            "month": report.month
        })

        if existing_report:
            report_collection.update_one(
                {
                    "language": report.language,
                    "year": report.year,
                    "month": report.month
                },
                {
                    "$addToSet": {
                        "detailed_results": {
                            "$each": report.detailed_results
                        },
                        "tool_wise_metrics": {
                            "$each": report.tool_wise_metrics
                        }
                    },
                    "$set": {
                        "performance_summary": report.performance_summary,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            return {"message": "Existing report updated successfully"}

        else:
            report_data["created_at"] = datetime.utcnow()
            report_collection.insert_one(report_data)

            return {"message": "New report saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))