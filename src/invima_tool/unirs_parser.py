from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .models import UnirsIndication
from .text import normalize_key

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def _column_index(ref: str) -> int:
    letters = re.match(r"([A-Z]+)", ref).group(1)  # type: ignore[union-attr]
    idx = 0
    for char in letters:
        idx = idx * 26 + ord(char) - 64
    return idx - 1


def _read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    strings: list[str] = []
    for item in root.findall("a:si", NS):
        strings.append("".join(t.text or "" for t in item.iter(f"{{{NS['a']}}}t")))
    return strings


def _first_sheet_path(zf: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    sheet = workbook.find("a:sheets", NS)[0]  # type: ignore[index]
    rid = sheet.attrib[f"{{{NS['r']}}}id"]
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    target = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}[rid].lstrip("/")
    return target if target.startswith("xl/") else f"xl/{target}"


def read_xlsx_rows(path: str | Path) -> list[tuple[int, list[str]]]:
    with zipfile.ZipFile(path) as zf:
        shared = _read_shared_strings(zf)
        sheet_xml = ET.fromstring(zf.read(_first_sheet_path(zf)))

    rows: list[tuple[int, list[str]]] = []
    for row in sheet_xml.findall(".//a:row", NS):
        row_number = int(row.attrib["r"])
        values = [""] * 8
        for cell in row.findall("a:c", NS):
            idx = _column_index(cell.attrib["r"])
            if idx >= len(values):
                values.extend([""] * (idx - len(values) + 1))
            v = cell.find("a:v", NS)
            value = "" if v is None else v.text or ""
            if cell.attrib.get("t") == "s" and value:
                value = shared[int(value)]
            values[idx] = value
        if any(str(v).strip() for v in values):
            rows.append((row_number, values))
    return rows


def parse_unirs_xlsx(path: str | Path) -> list[UnirsIndication]:
    rows = read_xlsx_rows(path)
    header_row = None
    for row_number, values in rows:
        if values and normalize_key(values[0]) == "PRINCIPIO ACTIVO":
            header_row = row_number
            break
    if header_row is None:
        raise ValueError("UNIRS header row was not found")

    indications: list[UnirsIndication] = []
    for row_number, values in rows:
        if row_number <= header_row or len(values) < 4:
            continue
        if not values[0].strip():
            continue
        indications.append(
            UnirsIndication(
                principio_activo=values[0],
                dci_concentracion=values[1],
                forma_farmaceutica=values[2],
                indicaciones=values[3],
                tipo_indicacion=values[4] if len(values) > 4 else "",
                indicacion_habilitada=values[5] if len(values) > 5 else "",
                fecha_creacion=values[6] if len(values) > 6 else "",
                fecha_modificacion=values[7] if len(values) > 7 else "",
            )
        )
    return indications


def filter_unirs(indications: list[UnirsIndication], query: str) -> list[UnirsIndication]:
    query_key = normalize_key(query)
    return [item for item in indications if query_key in normalize_key(item.principio_activo)]
