from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .cli import DB_PATH
from .reporting import build_drug_report


app = FastAPI(
    title="INVIMA Hemato-Oncologia API",
    description=(
        "API local para consultar reportes consolidados de medicamentos "
        "hemato-oncologicos desde SQLite."
    ),
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/drugs/{query}/report")
def drug_report(query: str, only_vigente: bool = Query(default=True)) -> dict:
    return build_drug_report(DB_PATH, query, only_vigente=only_vigente)
