from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from .invima_client import fetch_invima_detail_by_expediente
from .invima_parser import parse_invima_detail_html, parse_invima_results_html
from .manual_parser import parse_manual_file
from .pospopuli_parser import parse_pospopuli_results_html
from .storage import (
    connect,
    init_db,
    replace_pospopuli,
    replace_unirs,
    upsert_manual_profiles,
    upsert_invima_detail,
    upsert_invima_registrations,
)
from .reporting import build_drug_report, build_drug_universe
from .text import normalize_key
from .unirs_parser import filter_unirs, parse_unirs_xlsx


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "Datos brutos"
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "invima.sqlite"


def _print_json(data) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_parse_fixtures(args: argparse.Namespace) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = connect(DB_PATH)
    init_db(con)

    results_path = RAW_DIR / "Pagina principa al buscar PACLITAXEL_files" / "blanco(4).html"
    detail_path = RAW_DIR / "Paclitaxel al hacer clic en la primera presentacion_files" / "blanco(4).html"
    unirs_path = RAW_DIR / "UNIRS V24-07-2025.xlsx"
    pos_path = RAW_DIR / "POS Pópuli - Busqueda Paclitaxel.html"

    registrations = parse_invima_results_html(results_path)
    detail = parse_invima_detail_html(detail_path)
    unirs = parse_unirs_xlsx(unirs_path)
    pos = parse_pospopuli_results_html(pos_path)

    upsert_invima_registrations(con, registrations)
    upsert_invima_detail(con, detail)
    replace_unirs(con, unirs)
    replace_pospopuli(con, pos)

    _print_json(
        {
            "db": str(DB_PATH),
            "invima_registrations": len(registrations),
            "invima_detail_expediente": detail.expediente,
            "unirs_rows": len(unirs),
            "pospopuli_results": len(pos),
        }
    )


def cmd_import_invima_results(args: argparse.Namespace) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    con = connect(DB_PATH)
    init_db(con)
    result = _import_invima_results_file(
        con,
        Path(args.html),
        only_vigente=args.only_vigente,
        fetch_details=args.fetch_details,
        sleep=args.sleep,
    )
    con.close()
    _print_json(result)


def _import_invima_results_file(con, html: Path, *, only_vigente: bool, fetch_details: bool, sleep: float) -> dict:
    registrations = parse_invima_results_html(html)
    if only_vigente:
        registrations = [row for row in registrations if row.estado == "Vigente"]
    upsert_invima_registrations(con, registrations)

    fetched = 0
    errors: list[dict[str, str]] = []
    if fetch_details:
        for row in registrations:
            if not row.cdgprod:
                errors.append(
                    {
                        "expediente": row.expediente,
                        "producto": row.producto,
                        "error": "Missing cdgprod in results HTML",
                    }
                )
                continue
            try:
                detail = fetch_invima_detail_by_expediente(row.expediente, row.cdgprod)
                upsert_invima_detail(con, detail)
                fetched += 1
                time.sleep(sleep)
            except Exception as exc:
                errors.append(
                    {
                        "expediente": row.expediente,
                        "cdgprod": row.cdgprod,
                        "producto": row.producto,
                        "error": str(exc),
                    }
                )
    return {
        "html": str(html),
        "registrations_imported": len(registrations),
        "details_fetched": fetched,
        "errors": errors,
    }


def cmd_import_invima_results_dir(args: argparse.Namespace) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    con = connect(DB_PATH)
    init_db(con)
    try:
        paths = sorted(Path(args.dir).rglob(args.pattern))
        results = [
            _import_invima_results_file(
                con,
                path,
                only_vigente=args.only_vigente,
                fetch_details=args.fetch_details,
                sleep=args.sleep,
            )
            for path in paths
        ]
    finally:
        con.close()
    _print_json(
        {
            "dir": str(args.dir),
            "pattern": args.pattern,
            "files": len(results),
            "registrations_imported": sum(item["registrations_imported"] for item in results),
            "details_fetched": sum(item["details_fetched"] for item in results),
            "errors": [error for item in results for error in item["errors"]],
            "results": results,
        }
    )


def cmd_paclitaxel_demo(args: argparse.Namespace) -> None:
    results_path = RAW_DIR / "Pagina principa al buscar PACLITAXEL_files" / "blanco(4).html"
    detail_path = RAW_DIR / "Paclitaxel al hacer clic en la primera presentacion_files" / "blanco(4).html"
    unirs_path = RAW_DIR / "UNIRS V24-07-2025.xlsx"
    pos_path = RAW_DIR / "POS Pópuli - Busqueda Paclitaxel.html"

    registrations = parse_invima_results_html(results_path)
    detail = parse_invima_detail_html(detail_path)
    unirs_hits = filter_unirs(parse_unirs_xlsx(unirs_path), "PACLITAXEL")
    pos_results = parse_pospopuli_results_html(pos_path)

    _print_json(
        {
            "query": "PACLITAXEL",
            "invima": {
                "registrations_total": len(registrations),
                "first_detail": asdict(detail),
            },
            "unirs": [asdict(item) for item in unirs_hits],
            "pospopuli": [asdict(item) for item in pos_results],
        }
    )


def cmd_fetch_invima(args: argparse.Namespace) -> None:
    try:
        detail = fetch_invima_detail_by_expediente(args.expediente, args.cdgprod)
    except Exception as exc:
        _print_json({"expediente": args.expediente, "ok": False, "error": str(exc)})
        return
    _print_json({"ok": True, "detail": asdict(detail)})


def cmd_query_db(args: argparse.Namespace) -> None:
    con = connect(DB_PATH)
    init_db(con)
    query = f"%{normalize_key(args.query).replace(' ', '%')}%"
    invima = [
        dict(row)
        for row in con.execute(
            """
            SELECT * FROM invima_registrations
            WHERE upper(principio_activo) LIKE upper(?)
               OR upper(producto) LIKE upper(?)
            ORDER BY estado DESC, expediente
            """,
            (f"%{args.query}%", f"%{args.query}%"),
        )
    ]
    unirs = [
        dict(row)
        for row in con.execute(
            """
            SELECT * FROM unirs_indications
            WHERE upper(principio_activo) LIKE upper(?)
            ORDER BY principio_activo, forma_farmaceutica
            """,
            (f"%{args.query}%",),
        )
    ]
    pos = [
        dict(row)
        for row in con.execute(
            """
            SELECT * FROM pospopuli_results
            WHERE upper(nombre) LIKE upper(?)
            ORDER BY nombre
            """,
            (f"%{args.query}%",),
        )
    ]
    manual = [
        dict(row)
        for row in con.execute(
            """
            SELECT * FROM manual_drug_profiles
            WHERE upper(nombre) LIKE upper(?)
            ORDER BY nombre
            """,
            (f"%{args.query}%",),
        )
    ]
    _print_json({"query": args.query, "invima": invima, "unirs": unirs, "pospopuli": pos, "manual": manual})


def cmd_invima_indications(args: argparse.Namespace) -> None:
    con = connect(DB_PATH)
    init_db(con)
    rows = [
        dict(row)
        for row in con.execute(
            """
            SELECT expediente, cdgprod, producto, registro_sanitario, estado,
                   forma_farmaceutica, principio_activo, concentracion, indicaciones
            FROM invima_details
            WHERE indicaciones IS NOT NULL AND indicaciones != ''
              AND (upper(producto) LIKE upper(?) OR upper(principio_activo) LIKE upper(?))
            ORDER BY producto, expediente
            """,
            (f"%{args.query}%", f"%{args.query}%"),
        )
    ]
    if args.only_vigente:
        rows = [row for row in rows if row["estado"] == "Vigente"]
    _print_json({"query": args.query, "count": len(rows), "details": rows})


def cmd_fetch_details_from_db(args: argparse.Namespace) -> None:
    con = connect(DB_PATH)
    init_db(con)
    rows = [
        dict(row)
        for row in con.execute(
            """
            SELECT expediente, cdgprod, producto, estado
            FROM invima_registrations
            WHERE cdgprod IS NOT NULL AND cdgprod != ''
              AND (upper(principio_activo) LIKE upper(?) OR upper(producto) LIKE upper(?))
            ORDER BY CASE WHEN estado = 'Vigente' THEN 0 ELSE 1 END, expediente
            """,
            (f"%{args.query}%", f"%{args.query}%"),
        )
    ]
    if args.only_vigente:
        rows = [row for row in rows if row["estado"] == "Vigente"]
    if args.limit:
        rows = rows[: args.limit]

    fetched = 0
    errors: list[dict[str, str]] = []
    for row in rows:
        try:
            detail = fetch_invima_detail_by_expediente(row["expediente"], row["cdgprod"])
            upsert_invima_detail(con, detail)
            fetched += 1
            time.sleep(args.sleep)
        except Exception as exc:
            errors.append(
                {
                    "expediente": row["expediente"],
                    "cdgprod": row["cdgprod"],
                    "producto": row["producto"],
                    "error": str(exc),
                }
            )
    _print_json({"query": args.query, "attempted": len(rows), "fetched": fetched, "errors": errors})


def cmd_import_manual(args: argparse.Namespace) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    con = connect(DB_PATH)
    init_db(con)
    targets = [args.query] if args.query else None
    rows = parse_manual_file(args.path, targets=targets)
    upsert_manual_profiles(con, rows)
    _print_json(
        {
            "path": str(args.path),
            "query": args.query,
            "manual_profiles_imported": len(rows),
            "profiles": [row.nombre for row in rows],
        }
    )


def cmd_report(args: argparse.Namespace) -> None:
    _print_json(build_drug_report(DB_PATH, args.query, only_vigente=args.only_vigente))


def _read_query_file(path: str | Path) -> list[str]:
    return [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def cmd_export_reports(args: argparse.Namespace) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    universe = build_drug_universe(DB_PATH)
    sources_by_name = {item["name"].upper(): item["sources"] for item in universe}
    names = _read_query_file(args.query_file) if args.query_file else [item["name"] for item in universe]
    if args.limit:
        names = names[: args.limit]

    reports = [
        {
            "drug": name,
            "sources": sources_by_name.get(name.upper(), []),
            "report": build_drug_report(DB_PATH, name, only_vigente=args.only_vigente),
        }
        for name in names
    ]

    if args.format == "jsonl":
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            for item in reports:
                handle.write(json.dumps(item, ensure_ascii=False))
                handle.write("\n")
    else:
        out.write_text(
            json.dumps(
                {
                    "count": len(reports),
                    "only_vigente": args.only_vigente,
                    "items": reports,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    _print_json(
        {
            "out": str(out),
            "format": args.format,
            "only_vigente": args.only_vigente,
            "exported": len(reports),
            "universe": len(universe),
        }
    )


def cmd_coverage(args: argparse.Namespace) -> None:
    con = connect(DB_PATH)
    init_db(con)
    try:
        manual = {row["nombre"] for row in con.execute("SELECT nombre FROM manual_drug_profiles")}
        unirs = {
            row["principio_activo"]
            for row in con.execute(
                """
                SELECT DISTINCT principio_activo FROM unirs_indications
                WHERE principio_activo != '' AND indicaciones != ''
                """
            )
        }
        universe = sorted(manual | unirs)
        rows = []
        for name in universe:
            like = f"%{name}%"
            details = con.execute(
                """
                SELECT COUNT(*) FROM invima_details
                WHERE upper(principio_activo) LIKE upper(?) OR upper(producto) LIKE upper(?)
                """,
                (like, like),
            ).fetchone()[0]
            rows.append({"drug": name, "has_invima_details": details > 0, "invima_details": details})
    finally:
        con.close()

    missing = [row for row in rows if not row["has_invima_details"]]
    _print_json(
        {
            "total": len(rows),
            "with_invima_details": len(rows) - len(missing),
            "missing_invima_details": len(missing),
            "missing": missing[: args.limit] if args.limit else missing,
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="invima-tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    fixtures = sub.add_parser("parse-fixtures")
    fixtures.set_defaults(func=cmd_parse_fixtures)

    import_results = sub.add_parser("import-invima-results")
    import_results.add_argument("html")
    import_results.add_argument("--only-vigente", action="store_true")
    import_results.add_argument("--fetch-details", action="store_true")
    import_results.add_argument("--sleep", type=float, default=0.3)
    import_results.set_defaults(func=cmd_import_invima_results)

    import_results_dir = sub.add_parser("import-invima-results-dir")
    import_results_dir.add_argument("dir")
    import_results_dir.add_argument("--pattern", default="*.html")
    import_results_dir.add_argument("--only-vigente", action="store_true")
    import_results_dir.add_argument("--fetch-details", action="store_true")
    import_results_dir.add_argument("--sleep", type=float, default=0.3)
    import_results_dir.set_defaults(func=cmd_import_invima_results_dir)

    demo = sub.add_parser("paclitaxel-demo")
    demo.set_defaults(func=cmd_paclitaxel_demo)

    fetch = sub.add_parser("fetch-invima")
    fetch.add_argument("expediente")
    fetch.add_argument("cdgprod")
    fetch.set_defaults(func=cmd_fetch_invima)

    query = sub.add_parser("query")
    query.add_argument("query")
    query.set_defaults(func=cmd_query_db)

    indications = sub.add_parser("invima-indications")
    indications.add_argument("query")
    indications.add_argument("--only-vigente", action="store_true")
    indications.set_defaults(func=cmd_invima_indications)

    fetch_details = sub.add_parser("fetch-details-from-db")
    fetch_details.add_argument("query")
    fetch_details.add_argument("--only-vigente", action="store_true")
    fetch_details.add_argument("--limit", type=int, default=0)
    fetch_details.add_argument("--sleep", type=float, default=0.3)
    fetch_details.set_defaults(func=cmd_fetch_details_from_db)

    manual = sub.add_parser("import-manual")
    manual.add_argument("path")
    manual.add_argument("--query", default="")
    manual.set_defaults(func=cmd_import_manual)

    report = sub.add_parser("report")
    report.add_argument("query")
    report.add_argument("--only-vigente", action="store_true")
    report.set_defaults(func=cmd_report)

    export_reports = sub.add_parser("export-reports")
    export_reports.add_argument("--out", default=str(DATA_DIR / "reports.audit.jsonl"))
    export_reports.add_argument("--format", choices=("jsonl", "json"), default="jsonl")
    export_reports.add_argument("--only-vigente", action="store_true")
    export_reports.add_argument("--query-file", default="")
    export_reports.add_argument("--limit", type=int, default=0)
    export_reports.set_defaults(func=cmd_export_reports)

    coverage = sub.add_parser("coverage")
    coverage.add_argument("--limit", type=int, default=0)
    coverage.set_defaults(func=cmd_coverage)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
