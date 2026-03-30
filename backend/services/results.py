import calendar
import csv
import io
from typing import Generator

from app.database.db_operations import get_wer_results


def fetch_results(year: int, month: int, language: str) -> dict:
    """
    Fetch WER results for the given parameters.
    """
    month_name = calendar.month_name[month] if isinstance(month, int) else month
    results_list = get_wer_results(year=year, month=month_name, language=language)

    return {
        "year": year,
        "month": month,
        "language": language,
        "results": results_list,
        "total_files_processed": len(results_list),
    }


def stream_results_csv(year: int, month: int, language: str) -> Generator[str, None, None]:
    """
    Stream WER results as CSV rows (suitable for StreamingResponse).
    """
    response = fetch_results(year, month, language)
    results = response.get("results", [])

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
                "base_name": result.get("base_name", ""),
                "ai_tool": result.get("ai_tool", ""),
                "wer_score": result.get("wer_score", 0.0),
                "processed_timestamp": result.get("processed_timestamp", ""),
                "file_status": result.get("file_status", ""),
                "google_drive_file_id": result.get("google_drive_file_id") or "",
            }
        )
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)