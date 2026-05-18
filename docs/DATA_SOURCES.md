# Sources and traceability

## Purpose

This document describes how `INVIMA-HematoOncologia` separates official regulatory data, complementary coverage data, local clinical notes and scientific safety references.

## Central rule

Not all sources have the same authority.

An indication is shown as an **INVIMA indication** only when it comes from an INVIMA source. Other sources may complement, contrast or enrich the medication profile, but they do not replace regulatory authority.

## Source hierarchy

1. **INVIMA**: primary source for sanitary registration, regulatory status and indication by product or presentation.
2. **POS Populi**: source for UPC coverage or financing information.
3. **UNIRS**: complementary source for enabled or referenced indications.
4. **Local oncology profile**: curated local source for mechanism, adverse reactions, extravasation and summarized clinical notes.
5. **Scientific literature and official drug monographs**: source for mechanism, toxicity, hypersensitivity, anaphylaxis and management when curated for a specific medication.

## INVIMA access limits

The public INVIMA search flow may include CAPTCHA or other access controls. This project does not implement CAPTCHA bypass, evasion tooling or circumvention of access controls.

Allowed local workflow:

1. manual search by the user;
2. manual CAPTCHA resolution when required;
3. local import of a saved page or a permitted technical export;
4. structured storage in SQLite;
5. source and limitation display in the report.

## Local data excluded from the repository

The repository does not publish by default:

- `data/`;
- `Datos brutos/`;
- SQLite databases;
- downloaded HTML;
- third-party spreadsheets;
- browser exports or session artifacts.

These files may be used locally, but they require review before redistribution.
