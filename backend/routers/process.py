from fastapi import APIRouter, Depends
from backend.services.processing import run_processing
from backend.core.security import get_current_user

router = APIRouter()


@router.post("/")
def start_processing(body: dict, user=Depends(get_current_user)):
    result = run_processing(body["year"], body["month"], body["language"])
    return result