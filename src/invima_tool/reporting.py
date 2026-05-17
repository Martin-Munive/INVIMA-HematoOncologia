from __future__ import annotations

from pathlib import Path
import sqlite3

from .storage import connect, init_db


def _first_row(con: sqlite3.Connection, sql: str, params=()):
    row = con.execute(sql, params).fetchone()
    return dict(row) if row else None


def build_drug_report(db_path: str | Path, query: str, *, only_vigente: bool = False) -> dict:
    con = connect(db_path)
    try:
        init_db(con)
        term = f"%{query}%"

        registration_counts = [
            dict(row)
            for row in con.execute(
                """
                SELECT estado, count(*) AS n
                FROM invima_registrations
                WHERE upper(principio_activo) LIKE upper(?) OR upper(producto) LIKE upper(?)
                GROUP BY estado
                ORDER BY CASE WHEN estado = 'Vigente' THEN 0 ELSE 1 END, n DESC
                """,
                (term, term),
            )
        ]
        details = [
            dict(row)
            for row in con.execute(
                """
                SELECT expediente, cdgprod, producto, registro_sanitario, estado,
                       forma_farmaceutica, principio_activo, concentracion, atc, indicaciones
                FROM invima_details
                WHERE upper(producto) LIKE upper(?) OR upper(principio_activo) LIKE upper(?)
                ORDER BY producto, expediente
                """,
                (term, term),
            )
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
                WHERE upper(principio_activo) LIKE upper(?)
                ORDER BY principio_activo, forma_farmaceutica
                """,
                (term,),
            )
        ]
        pos = [
            dict(row)
            for row in con.execute(
                """
                SELECT nombre, tipo, codigo_atc, descripcion, detalle_url, financiacion
                FROM pospopuli_results
                WHERE upper(nombre) LIKE upper(?)
                ORDER BY nombre
                """,
                (term,),
            )
        ]
        manual = _first_row(
            con,
            """
            SELECT nombre, mecanismo, efectos_adversos, extravasacion, indicacion_manual
            FROM manual_drug_profiles
            WHERE upper(nombre) LIKE upper(?)
            ORDER BY nombre
            LIMIT 1
            """,
            (term,),
        )
    finally:
        con.close()

    missing = []
    if not registration_counts:
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
        },
        "unirs": {"count": len(unirs), "items": unirs},
        "pospopuli": {"count": len(pos), "items": pos},
        "source_policy": {
            "regulatory_indications_source": "INVIMA details only",
            "coverage_source": "POS Populi / UPC",
            "complementary_indications_source": "UNIRS",
            "manual_profile_source": "curated local oncology profile",
        },
    }
