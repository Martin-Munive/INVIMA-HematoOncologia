from __future__ import annotations

from pathlib import Path
import sqlite3

from .clinical_profiles import get_clinical_safety_profile
from .curated_regulatory import get_curated_invima_details, get_curated_invima_suggestions
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


def build_drug_suggestions(db_path: str | Path, query: str, *, limit: int = 12) -> list[dict]:
    cleaned = " ".join(query.strip().split())
    if len(cleaned) < 2:
        return []

    con = connect(db_path)
    try:
        init_db(con)
        candidates: dict[str, dict] = {}
        sources = (
            ("manual_drug_profiles", "nombre", "Perfil manual"),
            ("invima_details", "principio_activo", "INVIMA detalle"),
            ("unirs_indications", "principio_activo", "UNIRS"),
            ("pospopuli_results", "nombre", "POS Populi"),
        )
        for table, column, source in sources:
            for row in con.execute(f"SELECT {column} AS name, COUNT(*) AS n FROM {table} WHERE {column} <> '' GROUP BY {column}"):
                name = " ".join(str(row["name"] or "").split())
                key = name.upper()
                if not name:
                    continue
                item = candidates.setdefault(key, {"name": name, "sources": set(), "count": 0})
                item["sources"].add(source)
                item["count"] += int(row["n"] or 0)
        for curated in get_curated_invima_suggestions():
            key = curated["name"].upper()
            item = candidates.setdefault(key, {"name": curated["name"], "sources": set(), "count": 0})
            item["sources"].update(curated["sources"])
            item["count"] += int(curated["count"])
    finally:
        con.close()

    needle = cleaned.upper()
    matched = [
        item
        for item in candidates.values()
        if needle in item["name"].upper()
    ]
    matched.sort(key=lambda item: (0 if item["name"].upper().startswith(needle) else 1, len(item["name"]), item["name"]))
    return [
        {
            "name": item["name"],
            "sources": sorted(item["sources"]),
            "count": item["count"],
        }
        for item in matched[:limit]
    ]


def build_drug_universe(db_path: str | Path) -> list[dict]:
    candidates: dict[str, dict] = {}

    def add_candidate(name: str | None, source: str) -> None:
        cleaned = " ".join(str(name or "").split())
        if not cleaned:
            return
        key = cleaned.upper()
        item = candidates.setdefault(key, {"name": cleaned, "sources": set()})
        item["sources"].add(source)

    db_path = Path(db_path)
    if db_path.parent:
        db_path.parent.mkdir(parents=True, exist_ok=True)

    con = connect(db_path)
    try:
        init_db(con)
        for row in con.execute("SELECT nombre FROM manual_drug_profiles WHERE nombre <> ''"):
            add_candidate(row["nombre"], "Perfil manual")
        for row in con.execute("SELECT principio_activo FROM invima_registrations WHERE principio_activo <> ''"):
            add_candidate(row["principio_activo"], "INVIMA registros")
        for row in con.execute("SELECT principio_activo FROM invima_details WHERE principio_activo <> ''"):
            add_candidate(row["principio_activo"], "INVIMA detalle")
        for row in con.execute("SELECT principio_activo FROM unirs_indications WHERE principio_activo <> ''"):
            add_candidate(row["principio_activo"], "UNIRS")
        for row in con.execute("SELECT nombre FROM pospopuli_results WHERE nombre <> ''"):
            add_candidate(row["nombre"], "POS Populi")
    finally:
        con.close()

    for curated in get_curated_invima_suggestions():
        for source in curated["sources"]:
            add_candidate(curated["name"], source)

    return [
        {"name": item["name"], "sources": sorted(item["sources"])}
        for item in sorted(candidates.values(), key=lambda value: value["name"].upper())
    ]


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
        curated_details = get_curated_invima_details(query)
        if curated_details:
            existing_keys = {(row["expediente"], row["producto"]) for row in details}
            for detail in curated_details:
                key = (detail["expediente"], detail["producto"])
                if key not in existing_keys:
                    details.append(detail)
            if not registration_counts:
                registration_counts = [{"estado": "Fuente INVIMA curada", "n": len(curated_details)}]

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
        "clinical_safety": get_clinical_safety_profile(query),
        "source_policy": {
            "regulatory_indications_source": "INVIMA details or curated INVIMA act/source documents",
            "registration_source": "INVIMA HTML results or curated INVIMA source documents",
            "coverage_source": "POS Populi / UPC",
            "complementary_indications_source": "UNIRS",
            "manual_profile_source": "curated local oncology profile",
            "clinical_safety_source": "curated external scientific sources when available",
        },
    }
