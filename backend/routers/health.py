from fastapi import APIRouter

from app.health_check import run_startup_health_checks

router = APIRouter()


@router.get("/")
def health_check():
    return run_startup_health_checks()