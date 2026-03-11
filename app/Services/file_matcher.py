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

        parts = name_without_ext.split("_")

        base_name = parts[0]
        ai_tool = "_".join(parts[1:])  # Handles multi-word tool names

        if base_name not in mapping:
            mapping[base_name] = []

        mapping[base_name].append({
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

        if base_name in ai_mapping:
            matched.append({
                "base_name": base_name,
                "original_file": original,
                "ai_versions": ai_mapping[base_name]
            })
        else:
            # Silently track unmatched files - this is expected behavior
            # Files without AI versions are simply not processed
            unmatched_count += 1
    
    if unmatched_count > 0:
        logging.debug(f"{unmatched_count} original files have no matching AI files (expected behavior)")

    return matched
