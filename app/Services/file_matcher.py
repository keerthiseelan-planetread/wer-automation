import os
import logging


def build_ai_mapping(ai_files):
    """
    Creates mapping:
    {
        "video1": [
            {"ai_tool": "whisper", "file_id": "..."},
            {"ai_tool": "google", "file_id": "..."}
        ]
    }
    """
    mapping = {}

    for file in ai_files:
        filename = file["name"]
        file_id = file["id"]

        name_without_ext = os.path.splitext(filename)[0]

        if "_" not in name_without_ext:
            logging.warning(f"Invalid AI filename format: {filename}")
            continue

        # Split on LAST underscore: "Bhagi_di_dhee_whisper" → base="Bhagi_di_dhee", tool="whisper"
        last_underscore = name_without_ext.rfind("_")
        base_name = name_without_ext[:last_underscore]
        ai_tool = name_without_ext[last_underscore + 1:].lower()  # Normalize to lowercase
        
        # Normalize to lowercase for case-insensitive matching
        base_name_key = base_name.lower()

        if base_name_key not in mapping:
            mapping[base_name_key] = []

        mapping[base_name_key].append({
            "ai_tool": ai_tool,
            "file_id": file_id,
            "filename": filename
        })

    return mapping


def match_original_with_ai(original_files, ai_mapping):
    """
    Returns:
    [
        {
            "base_name": "video1",
            "original_file": {...},
            "ai_versions": [...]
        }
    ]
    """
    matched = []
    unmatched_count = 0

    for original in original_files:
        filename = original["name"]
        base_name = os.path.splitext(filename)[0]
        base_name_key = base_name.lower()  # case-insensitive lookup

        if base_name_key in ai_mapping:
            matched.append({
                "base_name": base_name,
                "original_file": original,
                "ai_versions": ai_mapping[base_name_key]
            })
        else:
            # Silently track unmatched files - this is expected behavior
            # Files without AI versions are simply not processed
            unmatched_count += 1
    
    if unmatched_count > 0:
        logging.debug(f"{unmatched_count} original files have no matching AI files (expected behavior)")

    return matched
