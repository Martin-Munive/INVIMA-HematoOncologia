from __future__ import annotations


ZOLEDRONIC_INVIMA_DETAILS = [
    {
        "expediente": "19938278",
        "cdgprod": "ACTA-46-2013-3.13.27",
        "producto": "ZOMETA 4 mg/5 mL CONCENTRADO DE SOLUCION PARA INFUSION",
        "registro_sanitario": "Fuente INVIMA Acta 46 de 2013",
        "estado": "Fuente INVIMA curada",
        "forma_farmaceutica": "Solucion inyectable",
        "principio_activo": "ACIDO ZOLEDRONICO",
        "concentracion": "4 mg/5 mL",
        "atc": "M05BA08",
        "indicaciones": (
            "Tratamiento de la hipercalcemia maligna, definida como una concentracion de calcio "
            "serico corregida en funcion de la albumina mayor de 12,0 mg/dL. Prevencion de "
            "complicaciones oseas, incluyendo fracturas patologicas, compresion medular, "
            "radioterapia o cirugia oseas, o hipercalcemia tumoral, en pacientes con neoplasias "
            "malignas avanzadas que afectan al hueso."
        ),
        "source_label": "INVIMA Acta No. 46 de 2013 SEMPB, numeral 3.13.27",
        "source_url": "https://invima.gov.co/invima_website/static/attachments/medicamentos_sala_especializada_medicamentos_sintesis/Acta_20No_2046_20de_202013_20SEMPB.pdf",
        "source_reference": "Paginas 54-55, lineas de ZOMETA 4 mg/5 mL.",
    },
    {
        "expediente": "ACTA-43-2013",
        "cdgprod": "ACTA-43-2013-ZOLEDRONICO",
        "producto": "ACIDO ZOLEDRONICO",
        "registro_sanitario": "Fuente INVIMA Acta 43 de 2013",
        "estado": "Fuente INVIMA curada",
        "forma_farmaceutica": "Solucion para infusion / polvo para reconstituir",
        "principio_activo": "ACIDO ZOLEDRONICO",
        "concentracion": "4 mg",
        "atc": "M05BA08",
        "indicaciones": (
            "Regulador del metabolismo oseo. Prevencion de complicaciones oseas, incluyendo "
            "fracturas patologicas, compresion medular, irradiacion o cirugia del hueso, o "
            "hipercalcemia inducida por tumor, en pacientes con neoplasias malignas avanzadas "
            "que afectan el hueso. Tratamiento de la hipercalcemia de neoplasia maligna."
        ),
        "source_label": "INVIMA Acta No. 43 de 2013 SEMPB",
        "source_url": "https://www.invima.gov.co/biblioteca/download/123581",
        "source_reference": "Pagina 86, consulta sobre productos con acido zoledronico.",
    },
]


def get_curated_invima_details(query: str) -> list[dict]:
    key = query.upper()
    if "ZOLEDRONICO" in key or "ZOLEDRONIC" in key or "ZOLEDRONATO" in key:
        return ZOLEDRONIC_INVIMA_DETAILS
    return []


def get_curated_invima_suggestions() -> list[dict]:
    return [
        {
            "name": "ACIDO ZOLEDRONICO",
            "sources": ["INVIMA acta curada"],
            "count": len(ZOLEDRONIC_INVIMA_DETAILS),
        }
    ]
