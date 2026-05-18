# UI clinical presentation notes

## Design direction

The medication report should use progressive disclosure:

1. Show the high-value answer first: regulatory diseases/clinical scenarios, financing, active registrations and safety warnings.
2. Keep source detail one click away with native expandable sections.
3. Use compact tables for repeated presentations because users need to scan product, concentration and sanitary registration.
4. Keep raw regulatory text in a lower detail panel for auditability.
5. Avoid decorative typography in clinical sections; use a system UI font and consistent weights.

## Evidence basis

Clinical decision support interface literature emphasizes bringing key information together, showing critical information at a glance, keeping useful detail at hand and drawing attention to safety-critical items.

Healthcare dashboard usability literature repeatedly prioritizes easy navigation, simplicity, high usability and clear descriptions. For this project that means:

- disease label visible without scrolling inside raw text;
- presentation details hidden only when the summary remains unambiguous;
- concentration, registration and source type visible in the same row;
- legal/source notes visible but not visually louder than clinical data.

## Current implementation

- INVIMA indications are summarized by detected disease/scenario.
- Presentations are shown in expandable sections, with product, human-readable concentration and registration.
- UNIRS indications are summarized separately inside the same regulatory panel.
- Full INVIMA and UNIRS text remains available in detailed panels.
- PACLITAXEL has a curated safety profile by adverse reaction system plus hypersensitivity and extravasation management.
- Desktop layout uses a two-column reading model: regulatory summary as the primary area, compact source/coverage panels on the side, and raw source text below as expandable audit sections.
- Raw INVIMA and UNIRS text should stay collapsed by default to avoid long scrolling and preserve the summary-first workflow.
- The footer reserves a visible brand area for Anaskai logo and ownership information.

## Sources reviewed

- Four principles for user interface design of computerised clinical decision support systems: https://pubmed.ncbi.nlm.nih.gov/21685612/
- Rank Ordered Design Attributes for Health Care Dashboards Including Artificial Intelligence: Usability Study: https://www.sciencedirect.com/org/science/article/pii/S1947257924000379
- Cancer Care Ontario PACLitaxel monograph: https://www.cancercareontario.ca/en/drugformulary/drugs/paclitaxel
- BC Cancer paclitaxel monograph: https://www.bccancer.bc.ca/drug-database-site/Drug%20Index/Paclitaxel_monograph.pdf
- DailyMed paclitaxel labels: https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=paclitaxel
