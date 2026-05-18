# Medication processing queue

## Purpose

This file tracks the medication queue after the PACLITAXEL reference workflow. The order is manual-document first, then UNIRS-only medications that are not already represented by the manual queue.

The queue is not a clinical authorization list. A medication is considered complete only when its source checklist is satisfied and the source evidence remains visible in the report.

## Status labels

- `Complete current local scope`: all currently available local source classes are present and validated.
- `Started`: at least one source has been imported and the consolidated report can be generated.
- `Pending source import`: medication is in queue, but local source evidence is not yet imported.
- `Pending scientific safety`: regulatory/manual data may exist, but adverse reactions, hypersensitivity/anaphylaxis and extravasation/toxicity have not been curated from scientific sources.

## Current processed medications

| Medication | Manual | INVIMA registrations/details | UNIRS | POS Populi | Scientific safety | Status |
| --- | --- | --- | --- | --- | --- | --- |
| PACLITAXEL | Imported | Imported: 91 registrations, 18 active details | Imported: 8 rows | Imported: 2 rows | Curated | Complete current local scope |
| ACETATO DE GOSERELINA / GOSERELINA | Imported | Pending post-CAPTCHA HTML/source import | Imported: 2 rows | Pending | Pending | Started |

## GOSERELINA notes

Local report command:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py report "ACETATO DE GOSERELINA" --only-vigente
```

Current evidence:

- Manual oncology profile imported from `MEDICAMENTOS ONCOLOGIA .txt`.
- UNIRS has 2 local rows for `GOSERELINA`:
  - `[GOSERELINA] 10,8mg/1U`, implant.
  - `[GOSERELINA] 3,6mg/1U`, implant.
- UNIRS indication text: prevention of early menopause during chemotherapy for early-stage hormone-receptor-negative breast cancer.
- Missing local evidence: INVIMA registrations/details, POS Populi coverage, curated scientific safety profile.

Implementation detail:

- The report layer expands common salt/prefix names, so `ACETATO DE GOSERELINA` can match local rows stored as `GOSERELINA`.
- This alias match does not create regulatory evidence. INVIMA indications must still come from imported INVIMA detail pages.

## Manual-document primary queue

The following canonical queue is derived from the manual oncology document and excludes obvious brands, presentation-only entries, duplicated concentration rows and section noise.

1. ACETATO DE GOSERELINA / GOSERELINA
2. ACIDO ZOLEDRONICO / ZOLEDRONICO
3. ATEZOLIZUMAB
4. AVELUMAB
5. AXITINIB
6. AZACITIDINA
7. BEVACIZUMAB
8. BENDAMUSTINA
9. BLEOMICINA
10. BRENTUXIMAB
11. BORTEZOMIB
12. CABAZITAXEL
13. CAPECITABINA
14. CARBOPLATINO
15. CARFILZOMIB
16. CETUXIMAB
17. CICLOFOSFAMIDA
18. CISPLATINO
19. CITARABINA
20. DARATUMUMAB
21. DACARBAZINA
22. DACTINOMICINA
23. DENOSUMAB
24. DOCETAXEL
25. DOXORUBICINA
26. DURVALUMAB
27. ERIBULINA
28. ENFORTUMAB
29. ETOPOSIDO
30. EVEROLIMUS
31. FLUOROURACILO
32. GEMCITABINA
33. INMUNOGLOBULINA G HUMANA
34. IFOSFAMIDA
35. IPILIMUMAB
36. IRINOTECAN
37. LANREOTIDE
38. LENALIDOMIDA
39. LUSPATERCEPT
40. LEUPROLIDE
41. METOTREXATO
42. MITOMICINA
43. NIVOLUMAB
44. OLAPARIB
45. OBINUTUZUMAB
46. OSIMERTINIB
47. OXALIPLATINO
48. PACLITAXEL
49. PANITUMUMAB
50. PEMBROLIZUMAB
51. PEMETREXED
52. PERTUZUMAB
53. POMALIDOMIDA
54. RAMUCIRUMAB
55. RITUXIMAB
56. ROMIPLOSTIM
57. TRASTUZUMAB
58. TIROTROPINA
59. VENETOCLAX
60. VINCRISTINA
61. VINBLASTINA

## Excluded or deferred headings

These headings appeared in the manual extraction but are not primary medication workflows until they are mapped deliberately:

- brand/presentation entries: `ZOLADEX`, `TECENTRIQ`, `ONUREG`, `MEGAFIVE`, `FLUOROPLEX`, `CAREBIN`, `SOMATULINE`;
- concentration-only rows and repeated product names;
- operational headings such as `MONITORIZAR` or `MANEJO`.

## Acceptance checklist per medication

1. Manual profile imported and section split checked.
2. INVIMA registrations imported from manually obtained source, without CAPTCHA bypass.
3. INVIMA details/indications imported for active presentations.
4. UNIRS rows checked and summarized separately from INVIMA authorization.
5. POS Populi coverage checked.
6. Scientific safety profile curated from reliable sources.
7. API report generated with missing sources explicit.
8. Frontend reviewed for readability and source separation.
9. Tests pass.
10. Documentation updated.
