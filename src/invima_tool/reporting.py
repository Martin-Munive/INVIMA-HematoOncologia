from __future__ import annotations

from pathlib import Path
import sqlite3

from .clinical_profiles import get_clinical_safety_profile
from .storage import connect, init_db


def _first_row(con: sqlite3.Connection, sql: str, params=()):
    row = con.execute(sql, params).fetchone()
    return dict(row) if row else None


def _query_terms(query: str) -> list[str]:
    cleaned = " ".join(query.strip().split())
    terms = [cleaned]
    upper = cleaned.upper()
    prefixes = (
        "ACETATO DE ",
        "ACIDO ",
        "ÁCIDO ",
        "CLORHIDRATO DE ",
        "FOSFATO DE ",
        "SULFATO DE ",
    )
    for prefix in prefixes:
        if upper.startswith(prefix):
            terms.append(cleaned[len(prefix) :].strip())
    seen = set()
    unique = []
    for term in terms:
        key = term.upper()
        if term and key not in seen:
            unique.append(term)
            seen.add(key)
    return unique


def _like_any(row: sqlite3.Row | dict, fields: tuple[str, ...], terms: list[str]) -> bool:
    values = [str(row[field] or "").upper() for field in fields]
    return any(term.upper() in value for term in terms for value in values)


def build_drug_report(db_path: str | Path, query: str, *, only_vigente: bool = False) -> dict:
    terms = _query_terms(query)
    con = connect(db_path)
    try:
        init_db(con)

        registration_counts = [
            dict(row)
            for row in con.execute(
                """
                SELECT estado, principio_activo, producto
                FROM invima_registrations
                """,
            )
            if _like_any(row, ("principio_activo", "producto"), terms)
        ]
        open_cum = [
            dict(row)
            for row in con.execute(
                """
                SELECT expediente, producto, titular, registro_sanitario, fecha_expedicion,
                       fecha_vencimiento, estado_registro, expediente_cum, consecutivo_cum,
                       cantidad_cum, descripcion_comercial, estado_cum, fecha_activo,
                       fecha_inactivo, muestra_medica, unidad, atc, descripcion_atc,
                       via_administracion, concentracion, principio_activo, unidad_medida,
                       cantidad, unidad_referencia, forma_farmaceutica, nombre_rol,
                       tipo_rol, modalidad, ium, source_dataset, imported_at
                FROM invima_open_cum
                ORDER BY producto, expediente, consecutivo_cum
                """
            )
            if _like_any(row, ("principio_activo", "producto", "descripcion_atc"), terms)
        ]
        if not registration_counts and open_cum:
            registration_counts = [
                {
                    "estado": row["estado_registro"],
                    "principio_activo": row["principio_activo"],
                    "producto": row["producto"],
                }
                for row in open_cum
            ]
        counts_by_status: dict[str, int] = {}
        for row in registration_counts:
            counts_by_status[row["estado"]] = counts_by_status.get(row["estado"], 0) + 1
        registration_counts = [
            {"estado": estado, "n": n}
            for estado, n in sorted(counts_by_status.items(), key=lambda item: (0 if item[0] == "Vigente" else 1, -item[1]))
        ]
        details = [
            dict(row)
            for row in con.execute(
                """
                SELECT expediente, cdgprod, producto, registro_sanitario, estado,
                       forma_farmaceutica, principio_activo, concentracion, atc, indicaciones
                FROM invima_details
                ORDER BY producto, expediente
                """
            )
            if _like_any(row, ("producto", "principio_activo"), terms)
        ]
        if only_vigente:
            details = [row for row in details if row["estado"] == "Vigente"]

        unirs = [
            dict(row)
            for row in con.execute(
                """
                SELECT principio_activo, dci_concentracion, forma_farmaceutica,
                       indicaciones, tipo_indicacion, indicacion_habilitada
                FROM unirs_indications
                ORDER BY principio_activo, forma_farmaceutica
                """
            )
            if _like_any(row, ("principio_activo", "dci_concentracion"), terms)
        ]
        pos = [
            dict(row)
            for row in con.execute(
                """
                SELECT nombre, tipo, codigo_atc, descripcion, detalle_url, financiacion
                FROM pospopuli_results
                ORDER BY nombre
                """
            )
            if _like_any(row, ("nombre",), terms)
        ]
        manual_rows = [
            row
            for row in con.execute(
                """
                SELECT nombre, mecanismo, efectos_adversos, extravasacion, indicacion_manual
                FROM manual_drug_profiles
                ORDER BY nombre
                """
            )
            if _like_any(row, ("nombre",), terms)
        ]
        manual = dict(manual_rows[0]) if manual_rows else None
    finally:
        con.close()

    missing = []
    if not registration_counts and not open_cum:
        missing.append("INVIMA registrations")
    if not details:
        missing.append("INVIMA details/indications")
    if not unirs:
        missing.append("UNIRS")
    if not pos:
        missing.append("POS Populi")
    if not manual:
        missing.append("manual oncology profile")

    return {
        "query": query,
        "only_vigente": only_vigente,
        "completion": {
            "is_complete_for_current_sources": not missing,
            "missing_sources": missing,
        },
        "manual_profile": manual,
        "invima": {
            "registration_counts": registration_counts,
            "details_count": len(details),
            "details": details,
            "open_cum_count": len(open_cum),
            "open_cum": open_cum,
        },
        "unirs": {"count": len(unirs), "items": unirs},
        "pospopuli": {"count": len(pos), "items": pos},
        "clinical_safety": get_clinical_safety_profile(query),
        "source_policy": {
            "regulatory_indications_source": "INVIMA details only",
            "registration_source": "INVIMA HTML results or Datos Abiertos CUM when available",
            "coverage_source": "POS Populi / UPC",
            "complementary_indications_source": "UNIRS",
            "manual_profile_source": "curated local oncology profile",
            "clinical_safety_source": "curated external scientific sources when available",
        },
    }
