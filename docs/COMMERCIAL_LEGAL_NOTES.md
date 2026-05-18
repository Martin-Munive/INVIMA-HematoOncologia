# Commercial and legal notes

## Scope

This project is designed as an independent software mechanism that organizes and presents information from public or locally curated sources. The code can be commercialized under its own license model, but the official source data, trademarks, clinical authority and regulatory authority remain with their respective institutions.

This document is not legal advice. Before a commercial release, the project should be reviewed by counsel familiar with Colombian health regulation, copyright, data reuse and medical software.

## INVIMA / Colombian open data

Preliminary conclusion: a commercial product appears possible if it respects the conditions for public information and open data reuse.

Operational requirements:

- preserve source attribution for INVIMA, UNIRS and POS Populi;
- show retrieval/import date when the data model supports it;
- do not imply endorsement, certification or partnership with INVIMA, Ministerio de Salud, OPS/OMS or another public institution;
- do not alter official regulatory meaning;
- separate regulatory indication from scientific literature and local manual interpretation;
- keep the application as decision support/information unless formally evaluated for medical-device obligations;
- avoid automated CAPTCHA bypass or circumvention of access controls;
- audit any raw downloaded file before redistribution.

Current footer policy:

```text
INVIMA Hemato-Oncologia es una aplicacion independiente. Integra fuentes publicas y locales para apoyo informativo; no reemplaza la consulta de la fuente oficial, el criterio clinico ni los procesos regulatorios aplicables. INVIMA, UNIRS y POS Populi conservan la titularidad y autoridad sobre sus datos oficiales.
```

## Software as medical device risk

Commercial positioning matters. A passive search, citation and source-navigation tool has a lower regulatory risk than software that recommends, authorizes, denies or automates clinical treatment decisions.

Before commercialization, define the intended use in writing:

- informational/reference support;
- no autonomous diagnosis;
- no autonomous authorization;
- no replacement for clinician, pharmacist or payer review;
- visible source trail for each regulatory or clinical statement.

If the product later automates clinical recommendations or patient-specific decisions, evaluate whether it becomes regulated medical software.

## AIEPI / PAHO

Preliminary conclusion: a commercial app that automates or substantially adapts PAHO/WHO AIEPI manuals probably requires permission from PAHO unless the specific source material is under a license that permits commercial reuse.

PAHO states that commercial use of PAHO materials requires permission. PAHO publications after its open-access policy commonly use Creative Commons Attribution-NonCommercial-ShareAlike for intergovernmental organizations, which allows noncommercial reuse but not commercial reuse without permission.

Commercial AIEPI strategy:

- do not copy the manual verbatim into a paid product without permission;
- identify the exact AIEPI edition and license;
- request PAHO permission for commercial use if the product depends on PAHO text, tables, algorithms or adapted flowcharts;
- consider building an original clinical decision workflow from national norms and licensed sources, with legal review;
- keep attribution and disclaimers visible.

## Sources reviewed

- INVIMA open data license: https://www.invima.gov.co/biblioteca/licencia-abierta-datos-abiertos-invimapdf
- Datos Abiertos Colombia terms: https://herramientas.datos.gov.co/terminos
- Ley 1712 de 2014, transparencia y acceso a informacion publica: https://www1.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=56882
- INVIMA software as possible medical device: https://www.invima.gov.co/node/184
- PAHO permissions and licenses: https://www.paho.org/es/publicaciones/permisos-licencias
