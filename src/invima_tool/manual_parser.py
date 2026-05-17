from __future__ import annotations

from pathlib import Path
import re

from .models import ManualDrugProfile
from .text import clean_ws, normalize_key, read_text_guess


SECTION_MARKERS = {
    "EFECTOS ADVERSOS": "adverse_effects",
    "EXTRAVASACIÓN": "extravasation",
    "EXTRAVASACION": "extravasation",
    "INDICACIÓN INVIMA": "manual_indications",
    "INDICACION INVIMA": "manual_indications",
}

EXTRAVASATION_MARKERS = (
    "CLASIFICACION",
    "VESICANTE",
    "IRRITANTE",
    "EXFOLIANTE",
    "NO AGRESIVO",
    "NO VESICANTE",
    "MANEJO",
    "MEDIDAS GENERALES",
    "HIALURONIDASA",
    "MUCOPOLISACARIDASA",
    "COMPRESAS",
    "FRIO",
    "CALOR",
    "NO APLICAR FRIO",
)


def _is_heading(line: str) -> bool:
    value = clean_ws(line)
    if not value or len(value) < 3:
        return False
    key = normalize_key(value)
    if key in {"MEDICAMENTO", "EFECTOS ADVERSOS NO", "EXTRAVASACION Y CONTROL", "INDICACION INVIMA"}:
        return False
    if len(key.split()) > 5:
        return False
    return bool(re.fullmatch(r"[A-Z0-9 ÑÁÉÍÓÚÜ/®+.-]+", value))


def _is_drug_heading(line: str) -> bool:
    value = clean_ws(line)
    key = normalize_key(value)
    if not _is_heading(value):
        return False
    if any(char.isdigit() for char in value):
        return False
    if "®" in value or " PERFIL " in f" {key} ":
        return False
    return len(key.split()) <= 3


def parse_manual_text(text: str, targets: list[str] | None = None) -> list[ManualDrugProfile]:
    lines = [line.rstrip() for line in text.splitlines()]
    target_keys = {normalize_key(item) for item in targets} if targets else None
    headings: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        if not _is_heading(line):
            continue
        key = normalize_key(line)
        if target_keys is not None and key not in target_keys:
            continue
        headings.append((idx, clean_ws(line)))

    profiles: list[ManualDrugProfile] = []
    for pos, (start, name) in enumerate(headings):
        end = len(lines)
        if target_keys is not None:
            # For targeted extraction, stop at the next plausible heading even if it is not a target.
            for idx in range(start + 1, len(lines)):
                if _is_drug_heading(lines[idx]):
                    end = idx
                    break
        elif pos + 1 < len(headings):
            end = headings[pos + 1][0]

        block_lines = [clean_ws(line) for line in lines[start + 1 : end] if clean_ws(line)]
        mechanism: list[str] = []
        adverse: list[str] = []
        extravasation: list[str] = []
        indications: list[str] = []
        current = "mechanism"

        for line in block_lines:
            key = normalize_key(line)
            matched = False
            for marker, section in SECTION_MARKERS.items():
                if key.startswith(normalize_key(marker)):
                    current = section
                    matched = True
                    break
            if matched:
                continue
            if current == "mechanism":
                mechanism.append(line)
            elif current == "adverse_effects":
                adverse.append(line)
            elif current == "extravasation":
                extravasation.append(line)
            else:
                indications.append(line)

        if not adverse and not extravasation and not indications:
            indication_start = None
            for idx, line in enumerate(block_lines):
                key = normalize_key(line)
                if idx > 0 and not line.startswith("*") and (
                    normalize_key(name) in key or "®" in line or " INDICADO " in f" {key} "
                ):
                    indication_start = idx
                    break
            if indication_start is not None:
                before_indication = block_lines[:indication_start]
                indications = block_lines[indication_start:]
                extravasation_start = None
                for idx, line in enumerate(before_indication):
                    key = normalize_key(line)
                    if any(marker in key for marker in EXTRAVASATION_MARKERS):
                        extravasation_start = idx
                        break
                if extravasation_start is not None:
                    adverse = before_indication[:extravasation_start]
                    extravasation = before_indication[extravasation_start:]
                    mechanism = []
                else:
                    adverse = before_indication
                    mechanism = []

        profiles.append(
            ManualDrugProfile(
                nombre=name,
                mecanismo="\n".join(mechanism),
                efectos_adversos="\n".join(adverse),
                extravasacion="\n".join(extravasation),
                indicacion_manual="\n".join(indications),
                raw_text="\n".join(block_lines),
            )
        )
    return profiles


def parse_manual_file(path: str | Path, targets: list[str] | None = None) -> list[ManualDrugProfile]:
    return parse_manual_text(read_text_guess(path), targets=targets)
