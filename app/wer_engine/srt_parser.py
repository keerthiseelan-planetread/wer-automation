import re


def parse_srt(content: str) -> str:
    """
    Converts SRT file content into clean normalized text
    suitable for WER calculation.
    """

    lines = content.splitlines()
    text_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip subtitle numbering
        if line.isdigit():
            continue

        # Skip timestamps
        if "-->" in line:
            continue

        text_lines.append(line)

    # Join all dialogue lines
    full_text = " ".join(text_lines)

    # Remove punctuation (keep letters and spaces)
    full_text = re.sub(r"[^\w\s]", "", full_text)

    # Normalize whitespace
    full_text = re.sub(r"\s+", " ", full_text)

    return full_text.strip().lower()
