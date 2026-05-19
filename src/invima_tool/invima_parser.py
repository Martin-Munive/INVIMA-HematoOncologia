from __future__ import annotations

from pathlib import Path
import re

from .html_tables import parse_table_rows
from .models import InvimaDetail, InvimaRegistration
from .text import clean_ws, read_text_guess


RESULT_HEADER = [
    "expediente sanitario",
    "principio activo",
    "nombre del producto",
    "registro sanitario",
    "estado registro",
    "fecha vencimiento",
    "modalidad",
]


def parse_invima_results_html(path: str | Path) -> list[InvimaRegistration]:
    html = read_text_guess(path)
    rows = parse_table_rows(html)
    cdgprod_by_expediente = {
        match.group(1): match.group(2)
        for match in re.finditer(r"prodexped2\((\d+),\s*2,\s*(\d+)\)", html)
    }
    if not rows:
        return []

    registrations: list[InvimaRegistration] = []
    for row in rows[1:]:
        if len(row) < 7:
            continue
        if not row[0].strip().isdigit():
            continue
        registrations.append(
            InvimaRegistration(
                expediente=row[0],
                cdgprod=cdgprod_by_expediente.get(row[0], ""),
                principio_activo=row[1],
                producto=row[2],
                registro_sanitario=row[3],
                estado=row[4],
                fecha_vencimiento=row[5],
                modalidad=row[6],
                inserto=row[7] if len(row) > 7 else "",
            )
        )
    return registrations


def _field_pairs(rows: list[list[str]]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for row in rows:
        idx = 0
        while idx + 1 < len(row):
            key = clean_ws(row[idx]).strip(" ?:")
            value = clean_ws(row[idx + 1])
            if key and value and key not in fields:
                fields[key] = value
            idx += 2
    return fields


def _find_value(rows: list[list[str]], key: str) -> str:
    key_norm = key.lower()
    for row in rows:
        for idx, cell in enumerate(row):
            if cell.lower().strip(" ?:") == key_norm and idx + 1 < len(row):
                return row[idx + 1]
    return ""


def _find_principle_and_concentration(rows: list[list[str]]) -> tuple[str, str]:
    for idx, row in enumerate(rows):
        normalized = [clean_ws(cell).lower() for cell in row]
        if "principio" not in normalized:
            continue
        principle_idx = normalized.index("principio")
        concentration_idx = -1
        for col_idx, value in enumerate(normalized):
            if "cantidad" in value or "concentr" in value:
                concentration_idx = col_idx
                break
        for candidate in rows[idx + 1 :]:
            if len(candidate) <= principle_idx:
                continue
            principle = clean_ws(candidate[principle_idx])
            concentration = clean_ws(candidate[concentration_idx]) if concentration_idx >= 0 and len(candidate) > concentration_idx else ""
            if principle and principle.lower() not in {"principio", "atc", "rol"}:
                return principle, concentration
    return "", ""


def _find_atc(rows: list[list[str]]) -> str:
    for idx, row in enumerate(rows):
        normalized = [clean_ws(cell).lower() for cell in row]
        if "atc" not in normalized:
            continue
        for candidate in rows[idx + 1 :]:
            for cell in candidate:
                value = clean_ws(cell)
                if re.match(r"^[A-Z]\d{2}[A-Z]{2}\d{2}$", value):
                    return value
    for row in rows:
        for cell in row:
            value = clean_ws(cell)
            if re.match(r"^[A-Z]\d{2}[A-Z]{2}\d{2}$", value):
                return value
    return ""


def parse_invima_detail_html(path_or_html: str | Path, *, is_html: bool = False) -> InvimaDetail:
    html = str(path_or_html) if is_html else read_text_guess(path_or_html)
    rows = parse_table_rows(html)
    fields = _field_pairs(rows)

    principio, concentracion = _find_principle_and_concentration(rows)
    atc = _find_atc(rows)

    return InvimaDetail(
        expediente=_find_value(rows, "Expediente Sanitario"),
        cdgprod="",
        producto=_find_value(rows, "Nombre producto"),
        registro_sanitario=_find_value(rows, "Registro Sanitario"),
        estado=_find_value(rows, "Estado Registro"),
        forma_farmaceutica=_find_value(rows, "Forma Farmaceutica"),
        indicaciones=_find_value(rows, "Indicaciones"),
        contraindicaciones=_find_value(rows, "Contraindicaciones"),
        via_administracion=_find_value(rows, "Via Administracion"),
        principio_activo=principio,
        concentracion=concentracion,
        atc=atc,
        raw_fields=fields,
    )
