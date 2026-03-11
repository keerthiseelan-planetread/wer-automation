"""MongoDB collection schemas and structure definitions."""

from datetime import datetime

# Schema for WER Results Collection
WER_RESULT_SCHEMA = {
    "bsonType": "object",
    "required": ["parameter_hash", "year", "month", "language", "results", "last_updated"],
    "properties": {
        "_id": {"bsonType": "objectId"},
        "parameter_hash": {
            "bsonType": "string",
            "description": "Hash of (year, month, language) for unique identification"
        },
        "year": {
            "bsonType": "int",
            "description": "Year (e.g., 2024)"
        },
        "month": {
            "bsonType": "string",
            "description": "Month name (e.g., 'March', 'January')"
        },
        "language": {
            "bsonType": "string",
            "description": "Language (e.g., 'English', 'Hindi')"
        },
        "results": {
            "bsonType": "array",
            "description": "Array of WER calculation results",
            "items": {
                "bsonType": "object",
                "required": ["base_name", "ai_tool", "wer_score"],
                "properties": {
                    "base_name": {
                        "bsonType": "string",
                        "description": "Base filename without AI tool suffix"
                    },
                    "ai_tool": {
                        "bsonType": "string",
                        "description": "AI tool name (e.g., 'whisper', 'google')"
                    },
                    "wer_score": {
                        "bsonType": "double",
                        "description": "WER score percentage"
                    },
                    "processed_timestamp": {
                        "bsonType": "date",
                        "description": "Timestamp when this result was calculated"
                    },
                    "file_modified_timestamp": {
                        "bsonType": "date",
                        "description": "Original file modification timestamp from Google Drive"
                    },
                    "google_drive_file_id": {
                        "bsonType": "string",
                        "description": "Google Drive file ID for traceability"
                    },
                    "file_status": {
                        "enum": ["current", "archived"],
                        "description": "Status of file (current or archived if deleted)"
                    }
                }
            }
        },
        "total_files_processed": {
            "bsonType": "int",
            "description": "Total number of files currently in this report"
        },
        "last_updated": {
            "bsonType": "date",
            "description": "Last update timestamp"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Initial creation timestamp"
        }
    }
}

# Schema for Processing Metadata Collection
PROCESSING_METADATA_SCHEMA = {
    "bsonType": "object",
    "required": ["parameter_hash", "year", "month", "language", "processed_file_ids"],
    "properties": {
        "_id": {"bsonType": "objectId"},
        "parameter_hash": {
            "bsonType": "string",
            "description": "Hash of (year, month, language) for unique identification"
        },
        "year": {
            "bsonType": "int",
            "description": "Year (e.g., 2024)"
        },
        "month": {
            "bsonType": "string",
            "description": "Month name"
        },
        "language": {
            "bsonType": "string",
            "description": "Language"
        },
        "processed_file_ids": {
            "bsonType": "array",
            "description": "List of Google Drive file IDs that have been processed",
            "items": {"bsonType": "string"}
        },
        "last_sync_timestamp": {
            "bsonType": "date",
            "description": "Last time file list was synced from Google Drive"
        },
        "last_drive_folder_scan": {
            "bsonType": "date",
            "description": "Last time we scanned the Google Drive folders"
        }
    }
}

# Schema for Tool Summary Metrics Collection (Optional - Future use)
TOOL_SUMMARY_METRICS_SCHEMA = {
    "bsonType": "object",
    "required": ["parameter_hash", "year", "month", "language", "tool_metrics"],
    "properties": {
        "_id": {"bsonType": "objectId"},
        "parameter_hash": {
            "bsonType": "string",
            "description": "Hash of (year, month, language)"
        },
        "year": {"bsonType": "int"},
        "month": {"bsonType": "string"},
        "language": {"bsonType": "string"},
        "tool_metrics": {
            "bsonType": "object",
            "description": "Tool-wise summary metrics",
            "additionalProperties": {
                "bsonType": "object",
                "properties": {
                    "average_wer": {"bsonType": "double"},
                    "best_wer": {"bsonType": "double"},
                    "worst_wer": {"bsonType": "double"},
                    "files_count": {"bsonType": "int"}
                }
            }
        }
    }
}
