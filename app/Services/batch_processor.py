import logging
from datetime import datetime
from app.Services.file_matcher import build_ai_mapping, match_original_with_ai
from app.wer_engine.wer_calculater import calculate_wer
from app.wer_engine.srt_parser import extract_text_from_srt


def process_batch(original_files, ai_files, drive_service):
    """
    Returns list of:
    {
        base_name,
        ai_tool,
        wer_score
    }
    """

    results = []

    # Step 1: Build AI Mapping
    ai_mapping = build_ai_mapping(ai_files)

    # Step 2: Match with Originals
    matched_data = match_original_with_ai(original_files, ai_mapping)

    for item in matched_data:
        base_name = item["base_name"]
        original_file = item["original_file"]
        ai_versions = item["ai_versions"]

        logging.info(f"Processing original file: {base_name}")

        # Download original once
        original_content = drive_service.download_file_content(original_file["id"])
        original_text = extract_text_from_srt(original_content)

        for ai in ai_versions:
            try:
                ai_tool = ai["ai_tool"]
                ai_content = drive_service.download_file_content(ai["file_id"])
                ai_text = extract_text_from_srt(ai_content)

                wer_score = calculate_wer(original_text, ai_text)

                results.append({
                    "base_name": base_name,
                    "ai_tool": ai_tool,
                    "wer_score": round(wer_score, 2),
                    "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                logging.info(f"WER computed for {base_name} - {ai_tool}: {wer_score}")

            except Exception as e:
                logging.error(f"Error processing {base_name} - {ai_tool}: {str(e)}")

    return results
