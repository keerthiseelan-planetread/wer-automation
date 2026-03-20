from fastapi import APIRouter, Depends
from backend.schemas.process import ProcessRequest, ProcessResponse
from backend.services.processing import run_processing
from backend.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=ProcessResponse)
def start_processing(body: ProcessRequest, user=Depends(get_current_user)):
    result = run_processing(body.year, body.month, body.language)
    return result