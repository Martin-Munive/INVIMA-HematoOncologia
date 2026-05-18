from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import InvimaCumRecord, InvimaDetail, InvimaRegistration, ManualDrugProfile, PosPopuliResult, UnirsIndication


def connect(path: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def init_db(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS invima_registrations (
            expediente TEXT PRIMARY KEY,
            cdgprod TEXT,
            principio_activo TEXT,
            producto TEXT,
            registro_sanitario TEXT,
            estado TEXT,
            fecha_vencimiento TEXT,
            modalidad TEXT,
            inserto TEXT
        );

        CREATE TABLE IF NOT EXISTS invima_details (
            expediente TEXT PRIMARY KEY,
            cdgprod TEXT,
            producto TEXT,
            registro_sanitario TEXT,
            estado TEXT,
            forma_farmaceutica TEXT,
            indicaciones TEXT,
            contraindicaciones TEXT,
            via_administracion TEXT,
            principio_activo TEXT,
            concentracion TEXT,
            atc TEXT
        );

        CREATE TABLE IF NOT EXISTS invima_open_cum (
            expediente TEXT,
            producto TEXT,
            titular TEXT,
            registro_sanitario TEXT,
            fecha_expedicion TEXT,
            fecha_vencimiento TEXT,
            estado_registro TEXT,
            expediente_cum TEXT,
            consecutivo_cum TEXT,
            cantidad_cum TEXT,
            descripcion_comercial TEXT,
            estado_cum TEXT,
            fecha_activo TEXT,
            fecha_inactivo TEXT,
            muestra_medica TEXT,
            unidad TEXT,
            atc TEXT,
            descripcion_atc TEXT,
            via_administracion TEXT,
            concentracion TEXT,
            principio_activo TEXT,
            unidad_medida TEXT,
            cantidad TEXT,
            unidad_referencia TEXT,
            forma_farmaceutica TEXT,
            nombre_rol TEXT,
            tipo_rol TEXT,
            modalidad TEXT,
            ium TEXT,
            source_dataset TEXT,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (expediente, consecutivo_cum, principio_activo, cantidad, unidad_referencia)
        );

        CREATE TABLE IF NOT EXISTS unirs_indications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            principio_activo TEXT,
            dci_concentracion TEXT,
            forma_farmaceutica TEXT,
            indicaciones TEXT,
            tipo_indicacion TEXT,
            indicacion_habilitada TEXT,
            fecha_creacion TEXT,
            fecha_modificacion TEXT
        );

        CREATE TABLE IF NOT EXISTS pospopuli_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            tipo TEXT,
            codigo_atc TEXT,
            descripcion TEXT,
            detalle_url TEXT,
            financiacion TEXT
        );

        CREATE TABLE IF NOT EXISTS manual_drug_profiles (
            nombre TEXT PRIMARY KEY,
            mecanismo TEXT,
            efectos_adversos TEXT,
            extravasacion TEXT,
            indicacion_manual TEXT,
            raw_text TEXT
        );
        """
    )
    con.commit()


def upsert_invima_open_cum(con: sqlite3.Connection, rows: list[InvimaCumRecord]) -> None:
    con.executemany(
        """
        INSERT INTO invima_open_cum (
            expediente, producto, titular, registro_sanitario, fecha_expedicion,
            fecha_vencimiento, estado_registro, expediente_cum, consecutivo_cum,
            cantidad_cum, descripcion_comercial, estado_cum, fecha_activo,
            fecha_inactivo, muestra_medica, unidad, atc, descripcion_atc,
            via_administracion, concentracion, principio_activo, unidad_medida,
            cantidad, unidad_referencia, forma_farmaceutica, nombre_rol,
            tipo_rol, modalidad, ium, source_dataset
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(expediente, consecutivo_cum, principio_activo, cantidad, unidad_referencia)
        DO UPDATE SET
            producto=excluded.producto,
            titular=excluded.titular,
            registro_sanitario=excluded.registro_sanitario,
            fecha_expedicion=excluded.fecha_expedicion,
            fecha_vencimiento=excluded.fecha_vencimiento,
            estado_registro=excluded.estado_registro,
            expediente_cum=excluded.expediente_cum,
            cantidad_cum=excluded.cantidad_cum,
            descripcion_comercial=excluded.descripcion_comercial,
            estado_cum=excluded.estado_cum,
            fecha_activo=excluded.fecha_activo,
            fecha_inactivo=excluded.fecha_inactivo,
            muestra_medica=excluded.muestra_medica,
            unidad=excluded.unidad,
            atc=excluded.atc,
            descripcion_atc=excluded.descripcion_atc,
            via_administracion=excluded.via_administracion,
            concentracion=excluded.concentracion,
            unidad_medida=excluded.unidad_medida,
            forma_farmaceutica=excluded.forma_farmaceutica,
            nombre_rol=excluded.nombre_rol,
            tipo_rol=excluded.tipo_rol,
            modalidad=excluded.modalidad,
            ium=excluded.ium,
            source_dataset=excluded.source_dataset,
            imported_at=CURRENT_TIMESTAMP
        """,
        [
            (
                r.expediente,
                r.producto,
                r.titular,
                r.registro_sanitario,
                r.fecha_expedicion,
                r.fecha_vencimiento,
                r.estado_registro,
                r.expediente_cum,
                r.consecutivo_cum,
                r.cantidad_cum,
                r.descripcion_comercial,
                r.estado_cum,
                r.fecha_activo,
                r.fecha_inactivo,
                r.muestra_medica,
                r.unidad,
                r.atc,
                r.descripcion_atc,
                r.via_administracion,
                r.concentracion,
                r.principio_activo,
                r.unidad_medida,
                r.cantidad,
                r.unidad_referencia,
                r.forma_farmaceutica,
                r.nombre_rol,
                r.tipo_rol,
                r.modalidad,
                r.ium,
                "datos.gov.co:i7cb-raxc",
            )
            for r in rows
        ],
    )
    con.commit()


def upsert_invima_registrations(con: sqlite3.Connection, rows: list[InvimaRegistration]) -> None:
    con.executemany(
        """
        INSERT INTO invima_registrations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(expediente) DO UPDATE SET
            cdgprod=excluded.cdgprod,
            principio_activo=excluded.principio_activo,
            producto=excluded.producto,
            registro_sanitario=excluded.registro_sanitario,
            estado=excluded.estado,
            fecha_vencimiento=excluded.fecha_vencimiento,
            modalidad=excluded.modalidad,
            inserto=excluded.inserto
        """,
        [
            (
                r.expediente,
                r.cdgprod,
                r.principio_activo,
                r.producto,
                r.registro_sanitario,
                r.estado,
                r.fecha_vencimiento,
                r.modalidad,
                r.inserto,
            )
            for r in rows
        ],
    )
    con.commit()


def upsert_invima_detail(con: sqlite3.Connection, detail: InvimaDetail) -> None:
    con.execute(
        """
        INSERT INTO invima_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(expediente) DO UPDATE SET
            cdgprod=excluded.cdgprod,
            producto=excluded.producto,
            registro_sanitario=excluded.registro_sanitario,
            estado=excluded.estado,
            forma_farmaceutica=excluded.forma_farmaceutica,
            indicaciones=excluded.indicaciones,
            contraindicaciones=excluded.contraindicaciones,
            via_administracion=excluded.via_administracion,
            principio_activo=excluded.principio_activo,
            concentracion=excluded.concentracion,
            atc=excluded.atc
        """,
        (
            detail.expediente,
            detail.cdgprod,
            detail.producto,
            detail.registro_sanitario,
            detail.estado,
            detail.forma_farmaceutica,
            detail.indicaciones,
            detail.contraindicaciones,
            detail.via_administracion,
            detail.principio_activo,
            detail.concentracion,
            detail.atc,
        ),
    )
    con.commit()


def replace_unirs(con: sqlite3.Connection, rows: list[UnirsIndication]) -> None:
    con.execute("DELETE FROM unirs_indications")
    con.executemany(
        """
        INSERT INTO unirs_indications (
            principio_activo, dci_concentracion, forma_farmaceutica,
            indicaciones, tipo_indicacion, indicacion_habilitada,
            fecha_creacion, fecha_modificacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r.principio_activo,
                r.dci_concentracion,
                r.forma_farmaceutica,
                r.indicaciones,
                r.tipo_indicacion,
                r.indicacion_habilitada,
                r.fecha_creacion,
                r.fecha_modificacion,
            )
            for r in rows
        ],
    )
    con.commit()


def replace_pospopuli(con: sqlite3.Connection, rows: list[PosPopuliResult]) -> None:
    con.execute("DELETE FROM pospopuli_results")
    con.executemany(
        """
        INSERT INTO pospopuli_results (
            nombre, tipo, codigo_atc, descripcion, detalle_url, financiacion
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [(r.nombre, r.tipo, r.codigo_atc, r.descripcion, r.detalle_url, r.financiacion) for r in rows],
    )
    con.commit()


def upsert_manual_profiles(con: sqlite3.Connection, rows: list[ManualDrugProfile]) -> None:
    con.executemany(
        """
        INSERT INTO manual_drug_profiles (
            nombre, mecanismo, efectos_adversos, extravasacion, indicacion_manual, raw_text
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(nombre) DO UPDATE SET
            mecanismo=excluded.mecanismo,
            efectos_adversos=excluded.efectos_adversos,
            extravasacion=excluded.extravasacion,
            indicacion_manual=excluded.indicacion_manual,
            raw_text=excluded.raw_text
        """,
        [
            (
                r.nombre,
                r.mecanismo,
                r.efectos_adversos,
                r.extravasacion,
                r.indicacion_manual,
                r.raw_text,
            )
            for r in rows
        ],
    )
    con.commit()
