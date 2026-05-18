# PACLITAXEL workflow

## Purpose

PACLITAXEL is the reference workflow for adding the next hemato-oncology medications. Every new medication should follow the same sequence unless a source is unavailable or legally restricted.

## Source order

1. Manual oncology document.
2. INVIMA registrations and details.
3. UNIRS.
4. POS Populi / UPC.
5. Scientific safety immersion.
6. Frontend verification.
7. Documentation and commit.

## Medication queue

The processing queue must avoid duplicates.

The durable queue lives in:

```text
docs/MEDICATION_QUEUE.md
```

Recommended order:

1. Extract medication names from the manual oncology document.
2. Normalize names for deduplication:
   - uppercase;
   - remove accents;
   - trim extra spaces;
   - remove presentation-only fragments when the active ingredient is clear.
3. Process manual-document medications first.
4. Extract active ingredients from UNIRS.
5. Add only UNIRS medications not already processed or queued from the manual document.

This avoids processing `PACLITAXEL`, `NAB-PACLITAXEL`, branded products or concentration variants as separate primary workflows unless they require distinct regulatory handling.

After PACLITAXEL, the first started medication is `ACETATO DE GOSERELINA / GOSERELINA`. It currently has manual and UNIRS evidence, but still requires INVIMA, POS Populi and scientific safety curation before it can be considered complete.

## PACLITAXEL steps

### 1. Import manual profile

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py import-manual "C:\Users\Oncología\Downloads\MEDICAMENTOS ONCOLOGIA .txt" --query PACLITAXEL
```

Expected result:

- one manual profile in `manual_drug_profiles`;
- adverse reactions, extravasation and indication text captured;
- manual source does not replace INVIMA.

### 2. Import INVIMA results

INVIMA search may require CAPTCHA. Do not bypass it.

Allowed flow:

1. Search manually in INVIMA.
2. Resolve CAPTCHA manually.
3. Save HTML or export a permitted request.
4. Import locally.

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py import-invima-results "C:\ruta\resultado_invima.html" --only-vigente --fetch-details
```

If results already exist but details are incomplete:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py fetch-details-from-db PACLITAXEL --only-vigente
```

Expected PACLITAXEL result:

- 91 INVIMA registrations total;
- 18 active details with indication text.

### 3. Confirm UNIRS

UNIRS is imported from the local XLSX dataset and used as complementary evidence, not as INVIMA authorization.

Expected PACLITAXEL result:

- 8 UNIRS rows;
- frontend summary extracts disease/scenario labels instead of showing only raw paragraphs.

### 4. Confirm POS Populi / UPC

POS Populi is used for financing/coverage information.

Expected PACLITAXEL result:

- 2 local POS Populi matches;
- financing shown as UPC-funded when present in source.

### 5. Build consolidated report

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py report PACLITAXEL --only-vigente
```

Expected report:

```text
completion.is_complete_for_current_sources = true
completion.missing_sources = []
```

### 6. Add scientific safety profile

Safety data must be curated per medication and stored separately from regulatory indications.

For PACLITAXEL this currently lives in:

```text
src/invima_tool/clinical_profiles.py
```

Minimum required sections:

- adverse reactions by system;
- hypersensitivity / anaphylaxis;
- extravasation / infiltration;
- source list.

Do not present scientific safety data as INVIMA indication.

### 7. Verify API

Start or restart API:

```powershell
.\.INVIMA\Scripts\python.exe run_api.py
```

Check:

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/drugs/PACLITAXEL/report?only_vigente=true
```

Expected API report includes:

- `manual_profile`;
- `invima`;
- `unirs`;
- `pospopuli`;
- `clinical_safety`;
- `source_policy`.

### 8. Verify frontend

Start frontend:

```powershell
cd app
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Required visual checks:

- regulatory summary shows detected INVIMA diseases/scenarios;
- expandable rows visibly indicate that they can be opened;
- concentrations are readable;
- UNIRS is summarized by detected pathology/scenario;
- full source text remains available in lower detail panels;
- safety profile appears only when curated.

### 9. Run validation

```powershell
.\.INVIMA\Scripts\python.exe -m unittest discover -s tests -v
cd app
npm run lint
npm run build
```

### 10. Commit and push

Before commit:

```powershell
git status --short
```

Commit only code, docs and tests intended for the public repository. Do not commit:

- `.INVIMA/`;
- `data/`;
- `Datos brutos/`;
- `app/dist/`;
- raw external downloads unless audited.

## Acceptance checklist for each new medication

- Manual profile imported or explicitly unavailable.
- INVIMA active details imported or missing source documented.
- UNIRS rows checked and summarized.
- POS Populi checked.
- Scientific safety profile curated or explicitly pending.
- API report shape valid.
- Frontend readable and source-separable.
- Tests and frontend build pass.
- Documentation updated.
