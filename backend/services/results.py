import calendar
import csv
import io
from typing import Generator

from app.config import Config
from app.database.db_operations import get_all_results_for_parameters, get_parameter_hash
from app.database.mongo_connection import get_database

from backend.schemas.results import ResultsResponse, WerResult


def fetch_results(year: int, month: int, language: str) -> ResultsResponse:
    """
    Fetch WER results for the given parameters, returning a ResultsResponse
    that matches the API schema.
    """
    month_name = calendar.month_name[month] if isinstance(month, int) else month
    results_list = get_all_results_for_parameters(year=year, month=month_name, language=language)

    # Get the underlying document for metadata fields
    db = get_database()
    wer_results_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
    param_hash = get_parameter_hash(year, month_name, language)
    record = wer_results_col.find_one({"parameter_hash": param_hash})

    wer_result_objects = [
        WerResult(
            base_name=r.get("base_name", ""),
            ai_tool=r.get("ai_tool", ""),
            wer_score=r.get("wer_score", 0.0),
            processed_timestamp=r.get("processed_timestamp", ""),
            file_status=r.get("file_status", ""),
            google_drive_file_id=r.get("google_drive_file_id"),
        )
        for r in results_list
    ]

    if record:
        return ResultsResponse(
            parameter_hash=record.get("parameter_hash", param_hash),
            year=year,
            month=month,
            language=language,
            results=wer_result_objects,
            total_files_processed=record.get("total_files_processed", len(results_list)),
            last_updated=record.get("last_updated", ""),
        )

    return ResultsResponse(
        parameter_hash=param_hash,
        year=year,
        month=month,
        language=language,
        results=wer_result_objects,
        total_files_processed=len(results_list),
        last_updated="",
    )


def stream_results_csv(year: int, month: int, language: str) -> Generator[str, None, None]:
    """
    Stream WER results as CSV rows (suitable for StreamingResponse).
    """
    response = fetch_results(year, month, language)
    results = response.results

    buffer = io.StringIO()

    # Define the exact CSV columns we want
    fieldnames = [
        "base_name",
        "ai_tool",
        "wer_score",
        "processed_timestamp",
        "file_status",
        "google_drive_file_id",
    ]

    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)

    for result in results:
        writer.writerow(
            {
                "base_name": result.base_name,
                "ai_tool": result.ai_tool,
                "wer_score": result.wer_score,
                "processed_timestamp": result.processed_timestamp,
                "file_status": result.file_status,
                "google_drive_file_id": result.google_drive_file_id or "",
            }
        )
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)