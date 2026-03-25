from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from backend.schemas.results import ResultsResponse
from backend.services.results import fetch_results, stream_results_csv
from backend.core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=ResultsResponse)
def list_results(
    year: int = Query(...),
    month: int = Query(...),
    language: str = Query(...),
    user=Depends(get_current_user),
):
    return fetch_results(year, month, language)


@router.get("/csv")
def download_csv(
    year: int = Query(...),
    month: int = Query(...),
    language: str = Query(...),
    user=Depends(get_current_user),
):
    generator = stream_results_csv(year, month, language)
    return StreamingResponse(generator, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=wer_results.csv"})