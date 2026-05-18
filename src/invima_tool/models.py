from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InvimaRegistration:
    expediente: str
    cdgprod: str
    principio_activo: str
    producto: str
    registro_sanitario: str
    estado: str
    fecha_vencimiento: str
    modalidad: str
    inserto: str = ""


@dataclass(frozen=True)
class InvimaDetail:
    expediente: str
    cdgprod: str
    producto: str
    registro_sanitario: str
    estado: str
    forma_farmaceutica: str
    indicaciones: str
    contraindicaciones: str
    via_administracion: str
    principio_activo: str
    concentracion: str
    atc: str
    raw_fields: dict[str, str]


@dataclass(frozen=True)
class InvimaCumRecord:
    expediente: str
    producto: str
    titular: str
    registro_sanitario: str
    fecha_expedicion: str
    fecha_vencimiento: str
    estado_registro: str
    expediente_cum: str
    consecutivo_cum: str
    cantidad_cum: str
    descripcion_comercial: str
    estado_cum: str
    fecha_activo: str
    fecha_inactivo: str
    muestra_medica: str
    unidad: str
    atc: str
    descripcion_atc: str
    via_administracion: str
    concentracion: str
    principio_activo: str
    unidad_medida: str
    cantidad: str
    unidad_referencia: str
    forma_farmaceutica: str
    nombre_rol: str
    tipo_rol: str
    modalidad: str
    ium: str


@dataclass(frozen=True)
class UnirsIndication:
    principio_activo: str
    dci_concentracion: str
    forma_farmaceutica: str
    indicaciones: str
    tipo_indicacion: str
    indicacion_habilitada: str
    fecha_creacion: str
    fecha_modificacion: str


@dataclass(frozen=True)
class PosPopuliResult:
    nombre: str
    tipo: str
    codigo_atc: str
    descripcion: str
    detalle_url: str
    financiacion: str


@dataclass(frozen=True)
class ManualDrugProfile:
    nombre: str
    mecanismo: str
    efectos_adversos: str
    extravasacion: str
    indicacion_manual: str
    raw_text: str
