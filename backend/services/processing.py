from app.Services.incremental_processor import process_with_incremental_caching


def run_processing(year: int, month: int, language: str) -> dict:
    process_with_incremental_caching(year=year, month=month, language=language)
    return {"status": "ok", "message": "Processing started/completed"}