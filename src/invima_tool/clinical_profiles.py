from __future__ import annotations


PACLitaxel_SAFETY_PROFILE = {
    "drug": "PACLITAXEL",
    "source_status": "curated_from_external_scientific_sources",
    "definition": "Antineoplasico de la familia de los taxanos usado en varios tumores solidos; actua como inhibidor de microtubulos.",
    "mechanism": "Se une a la tubulina, favorece el ensamblaje y estabilizacion de microtubulos e impide su despolimerizacion; esto bloquea la reorganizacion normal del citoesqueleto necesaria para mitosis y otras funciones celulares.",
    "mechanism_sources": [
        {
            "label": "NCI Drug Dictionary - paclitaxel",
            "url": "https://www.cancer.gov/publications/dictionaries/cancer-drug/def/paclitaxel",
        },
        {
            "label": "DailyMed paclitaxel prescribing information",
            "url": "https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=paclitaxel",
        },
    ],
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


ZOLEDRONIC_ACID_SAFETY_PROFILE = {
    "drug": "ACIDO ZOLEDRONICO",
    "source_status": "curated_from_external_scientific_sources",
    "definition": "Bifosfonato nitrogenado usado para inhibir la resorcion osea osteoclastica y reducir complicaciones oseas relacionadas con cancer.",
    "mechanism": "Se une a la hidroxiapatita del hueso e inhibe la farnesil pirofosfato sintasa en osteoclastos; esto altera la prenilacion de proteinas pequenas GTPasas, reduce la actividad osteoclastica y disminuye la resorcion osea y el calcio serico.",
    "mechanism_sources": [
        {
            "label": "NCI Drug Dictionary - zoledronic acid",
            "url": "https://www.cancer.gov/publications/dictionaries/cancer-drug/def/zoledronic-acid",
        },
        {
            "label": "DailyMed zoledronic acid prescribing information",
            "url": "https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=zoledronic%20acid",
        },
    ],
    "sources": [
        {
            "label": "Cancer Care Ontario zoledronic acid monograph",
            "url": "https://www.cancercareontario.ca/drugformulary/drugs/zoledronicacid",
        },
        {
            "label": "BC Cancer zoledronic acid monograph",
            "url": "https://www.bccancer.bc.ca/drug-database-site/Drug%20Index/Zoledronic%20acid_monograph.pdf",
        },
        {
            "label": "DailyMed zoledronic acid prescribing information",
            "url": "https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=zoledronic%20acid",
        },
    ],
    "adverse_reactions_by_system": [
        {
            "system": "Metabolico / electrolitos",
            "items": ["Hipocalcemia", "hipofosfatemia", "hipomagnesemia", "sintomas por reaccion de fase aguda"],
        },
        {
            "system": "Renal",
            "items": ["Elevacion de creatinina", "deterioro renal", "falla renal aguda rara", "proteinuria"],
        },
        {
            "system": "Oseo / odontologico",
            "items": ["Osteonecrosis de mandibula", "dolor oseo", "fracturas femorales atipicas raras"],
        },
        {
            "system": "Neuromuscular",
            "items": ["Mialgias", "artralgias", "dolor musculoesqueletico", "dolor de extremidades"],
        },
        {
            "system": "General / infusion",
            "items": ["Fiebre", "escalofrios", "sindrome gripal", "fatiga", "astenia"],
        },
        {
            "system": "Gastrointestinal",
            "items": ["Nauseas", "vomito", "diarrea", "dolor abdominal", "dispepsia"],
        },
        {
            "system": "Ocular",
            "items": ["Conjuntivitis", "uveitis", "escleritis", "dolor ocular"],
        },
        {
            "system": "Inmunologico",
            "items": ["Hipersensibilidad", "urticaria", "angioedema", "anafilaxia rara"],
        },
    ],
    "hypersensitivity": {
        "risk": "Las reacciones de hipersensibilidad son infrecuentes, pero se han reportado urticaria, angioedema y anafilaxia con zoledronato.",
        "prevention": [
            "Verificar antecedente de hipersensibilidad a acido zoledronico, excipientes u otros bifosfonatos.",
            "Corregir hipocalcemia y evaluar funcion renal antes de la infusion.",
        ],
        "management": [
            "Suspender la infusion ante reaccion inmediata significativa.",
            "Evaluar via aerea, respiracion, circulacion y signos vitales.",
            "Tratar anafilaxia segun protocolo institucional, incluyendo epinefrina si cumple criterios.",
            "No reexponer sin evaluacion especializada si la reaccion fue severa.",
        ],
    },
    "extravasation": {
        "classification": "No antineoplasico vesicante; puede causar irritacion local por infusion intravenosa.",
        "prevention": [
            "Administrar por via intravenosa con acceso permeable y tiempo de infusion no menor al recomendado.",
            "Evitar mezclar con soluciones que contienen calcio.",
        ],
        "management": [
            "Suspender infusion si hay dolor, edema, eritema o infiltracion.",
            "Retirar o manejar el acceso segun protocolo institucional de infiltracion no vesicante.",
            "Elevar la extremidad, vigilar evolucion local y documentar el evento.",
            "Escalar a farmacia/enfermeria oncologica si hay necrosis, dolor progresivo o compromiso funcional.",
        ],
    },
}


def get_clinical_safety_profile(query: str) -> dict | None:
    key = query.upper()
    if "PACLITAXEL" in key:
        return PACLitaxel_SAFETY_PROFILE
    if "ZOLEDRONICO" in key or "ZOLEDRONIC" in key or "ZOLEDRONATO" in key:
        return ZOLEDRONIC_ACID_SAFETY_PROFILE
    return None
