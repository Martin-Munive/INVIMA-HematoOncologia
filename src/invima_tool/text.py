from __future__ import annotations

import re
import unicodedata
from pathlib import Path


def clean_ws(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def normalize_key(value: str | None) -> str:
    value = clean_ws(value).upper()
    value = "".join(
        ch for ch in unicodedata.normalize("NFD", value)
        if unicodedata.category(ch) != "Mn"
    )
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    return clean_ws(value)


def read_text_guess(path: str | Path) -> str:
    data = Path(path).read_bytes()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")
