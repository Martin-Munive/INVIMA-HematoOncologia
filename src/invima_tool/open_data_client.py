from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import InvimaCumRecord


CUM_VIGENTES_ENDPOINT = "https://www.datos.gov.co/resource/i7cb-raxc.json"


def _value(row: dict, key: str) -> str:
    return str(row.get(key) or "").strip()


def _to_cum_record(row: dict) -> InvimaCumRecord:
    return InvimaCumRecord(
        expediente=_value(row, "expediente"),
        producto=_value(row, "producto"),
        titular=_value(row, "titular"),
        registro_sanitario=_value(row, "registrosanitario"),
        fecha_expedicion=_value(row, "fechaexpedicion"),
        fecha_vencimiento=_value(row, "fechavencimiento"),
        estado_registro=_value(row, "estadoregistro"),
        expediente_cum=_value(row, "expedientecum"),
        consecutivo_cum=_value(row, "consecutivocum"),
        cantidad_cum=_value(row, "cantidadcum"),
        descripcion_comercial=_value(row, "descripcioncomercial"),
        estado_cum=_value(row, "estadocum"),
        fecha_activo=_value(row, "fechaactivo"),
        fecha_inactivo=_value(row, "fechainactivo"),
        muestra_medica=_value(row, "muestramedica"),
        unidad=_value(row, "unidad"),
        atc=_value(row, "atc"),
        descripcion_atc=_value(row, "descripcionatc"),
        via_administracion=_value(row, "viaadministracion"),
        concentracion=_value(row, "concentracion"),
        principio_activo=_value(row, "principioactivo"),
        unidad_medida=_value(row, "unidadmedida"),
        cantidad=_value(row, "cantidad"),
        unidad_referencia=_value(row, "unidadreferencia"),
        forma_farmaceutica=_value(row, "formafarmaceutica"),
        nombre_rol=_value(row, "nombrerol"),
        tipo_rol=_value(row, "tiporol"),
        modalidad=_value(row, "modalidad"),
        ium=_value(row, "ium"),
    )


def fetch_cum_vigentes(query: str, *, limit: int = 5000, timeout: int = 60) -> list[InvimaCumRecord]:
    cleaned = " ".join(query.strip().split())
    if len(cleaned) < 3:
        raise ValueError("The CUM open-data query must contain at least 3 characters.")

    escaped = cleaned.upper().replace("'", "''")
    where = f"upper(principioactivo) like '%{escaped}%' OR upper(producto) like '%{escaped}%'"
    params = urlencode({"$limit": str(limit), "$where": where})
    request = Request(
        f"{CUM_VIGENTES_ENDPOINT}?{params}",
        headers={"User-Agent": "INVIMA-HematoOncologia/0.1"},
    )
    with urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8", errors="replace")
    rows = json.loads(payload)
    if not isinstance(rows, list):
        raise ValueError("Datos Abiertos CUM returned an unexpected response shape.")
    return [_to_cum_record(row) for row in rows]
