from __future__ import annotations


PACLitaxel_SAFETY_PROFILE = {
    "drug": "PACLITAXEL",
    "source_status": "curated_from_external_scientific_sources",
    "sources": [
        {
            "label": "Cancer Care Ontario PACLitaxel monograph",
            "url": "https://www.cancercareontario.ca/en/drugformulary/drugs/paclitaxel",
        },
        {
            "label": "BC Cancer paclitaxel monograph",
            "url": "https://www.bccancer.bc.ca/drug-database-site/Drug%20Index/Paclitaxel_monograph.pdf",
        },
        {
            "label": "DailyMed paclitaxel prescribing information",
            "url": "https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=paclitaxel",
        },
    ],
    "adverse_reactions_by_system": [
        {
            "system": "Hematologico",
            "items": ["Mielosupresion", "neutropenia", "anemia", "trombocitopenia", "infecciones asociadas a neutropenia"],
        },
        {
            "system": "Neurologico",
            "items": ["Neuropatia periferica", "parestesias", "neuropatia sensitiva", "somnolencia"],
        },
        {
            "system": "Inmunologico / infusion",
            "items": ["Reacciones de hipersensibilidad durante infusion", "broncoespasmo", "hipotension", "rubor", "prurito", "anafilaxia rara pero critica"],
        },
        {
            "system": "Gastrointestinal / mucosas",
            "items": ["Nauseas", "vomito", "diarrea", "mucositis"],
        },
        {
            "system": "Dermatologico",
            "items": ["Alopecia", "rash", "alteraciones ungueales", "recall cutaneo en sitios previos de extravasacion reportado raramente"],
        },
        {
            "system": "Musculoesqueletico",
            "items": ["Artralgias", "mialgias"],
        },
        {
            "system": "Hepatico / laboratorio",
            "items": ["Elevacion de transaminasas", "alteraciones de pruebas de funcion hepatica"],
        },
        {
            "system": "Cardiovascular",
            "items": ["Bradicardia", "hipotension", "eventos cardiovasculares infrecuentes"],
        },
    ],
    "hypersensitivity": {
        "risk": "Las reacciones suelen ocurrir en cursos tempranos y durante la primera hora de infusion.",
        "prevention": [
            "Premedicacion con corticosteroide, antihistaminico H1 y antagonista H2 cuando aplique a paclitaxel convencional.",
            "Vigilancia estrecha durante la infusion, especialmente en primeras administraciones.",
        ],
        "management": [
            "Detener infusion ante reaccion significativa.",
            "Evaluar via aerea, respiracion, circulacion y signos vitales.",
            "Administrar manejo de anafilaxia segun protocolo institucional, incluyendo epinefrina si hay criterios de anafilaxia.",
            "No reexponer si la reaccion fue severa salvo decision especializada y protocolo formal.",
        ],
    },
    "extravasation": {
        "classification": "Irritante; algunas fuentes describen propiedades vesicantes raras.",
        "prevention": [
            "Verificar retorno venoso y sitio de infusion antes y durante la administracion.",
            "Educar al paciente para reportar dolor, ardor, edema o cambio de coloracion en el sitio.",
        ],
        "management": [
            "Suspender infusion sin retirar inicialmente el acceso.",
            "Aspirar suavemente el remanente por el acceso si es posible.",
            "Elevar extremidad y seguir protocolo institucional de extravasacion.",
            "Considerar hialuronidasa si el protocolo local la contempla para taxanos.",
            "Documentar evento, delimitar zona y vigilar evolucion cutanea.",
        ],
    },
}


def get_clinical_safety_profile(query: str) -> dict | None:
    if "PACLITAXEL" in query.upper():
        return PACLitaxel_SAFETY_PROFILE
    return None
