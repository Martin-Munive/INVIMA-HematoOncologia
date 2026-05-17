from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from .html_tables import parse_links, parse_table_rows
from .models import PosPopuliResult
from .text import clean_ws, read_text_guess


def parse_pospopuli_results_html(path: str | Path) -> list[PosPopuliResult]:
    html = read_text_guess(path)
    rows = parse_table_rows(html)
    links = [
        unquote(link.replace("&amp;", "&"))
        for link in parse_links(html)
        if "resultadomedicamentos.aspx" in link
    ]

    results: list[PosPopuliResult] = []
    for idx, row in enumerate(rows):
        text = clean_ws(" ".join(row))
        if "Código ATC" not in text and "Codigo ATC" not in text:
            continue
        atc_match = re.search(r"C[oó]digo ATC\s+([A-Z0-9]+)", text, re.IGNORECASE)
        atc = atc_match.group(1) if atc_match else ""
        financing = (
            "Financiado con recursos de la Unidad de Pago por Capitación (UPC)"
            if "Financiado con recursos de la Unidad de Pago" in text
            else ""
        )
        result_type = "Medicamento" if "Medicamento" in text else ""
        name = text
        for marker in ("Medicamento", "Código ATC", "Codigo ATC"):
            if marker in name:
                name = name.split(marker, 1)[0]
                break
        results.append(
            PosPopuliResult(
                nombre=clean_ws(name),
                tipo=result_type,
                codigo_atc=atc,
                descripcion="Incluye todas las concentraciones y formas farmacéuticas"
                if "Incluye todas las concentraciones" in text
                else "",
                detalle_url=links[idx] if idx < len(links) else "",
                financiacion=financing,
            )
        )
    return results
