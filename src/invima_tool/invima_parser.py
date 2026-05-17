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


def parse_invima_detail_html(path_or_html: str | Path, *, is_html: bool = False) -> InvimaDetail:
    html = str(path_or_html) if is_html else read_text_guess(path_or_html)
    rows = parse_table_rows(html)
    fields = _field_pairs(rows)

    atc = ""
    for row in rows:
        if row and row[0].upper().startswith("L") and len(row[0]) >= 5:
            atc = row[0]
            break

    principio = ""
    concentracion = ""
    for row in rows:
        if len(row) >= 3 and row[0] and row[0].upper() not in {"PRINCIPIO", "ATC"}:
            # The concentration table appears after a header: ["Principio", ...].
            if row[0].upper().startswith("PACLITAXEL"):
                principio, concentracion = row[0], row[1]
                break

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
