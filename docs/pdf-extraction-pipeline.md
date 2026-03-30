# PDF Extraction Pipeline

This repo now has a local-first CDS extraction pipeline under `cds_pipeline/`.

The goal is to replace one-off `extract_*.py` scripts with a single command flow that:

- classifies each PDF before extraction
- uses the right extractor for that document type
- normalizes into the site schema
- validates the output
- emits review artifacts instead of silently guessing

## Default Recommendation

Use the new pipeline first:

```bash
python -m cds_pipeline extract <school-or-path>
```

Examples:

```bash
python -m cds_pipeline classify uwmadison
python -m cds_pipeline extract uwmadison
python -m cds_pipeline review .cds_pipeline/uwmadison/candidate.json
python -m cds_pipeline export .cds_pipeline/uwmadison/candidate.json
```

No paid service is required for this workflow.

## Pipeline Stages

### 1. Classify

The classifier labels each PDF as one of:

- `acroform`
- `native_text`
- `layout_sensitive`
- `scanned`

This determines the extractor cascade for that file.

### 2. Extract

The local extractor stack is:

- `AcroFormExtractor`
  - uses `pypdf` form fields first
- `NativeTextExtractor`
  - uses `PyMuPDF` block-aware extraction, with `pypdf` fallback
- `StructuredLayoutExtractor`
  - uses `Docling` for structure-aware conversion
- `OcrFallbackExtractor`
  - uses rendered-page OCR only when needed

### 3. Normalize

The normalizer maps extractor output into the existing school JSON schema:

- admissions
- test scores
- demographics
- costs
- financial aid

Each extracted field records provenance and confidence.

### 4. Validate

The validator checks:

- admissions rate reconciliation
- yield reconciliation
- enrollment totals
- race totals vs undergraduate enrollment
- residency totals vs undergraduate enrollment
- `totalCOA == tuition + fees + roomAndBoard`

### 5. Review

The pipeline writes artifacts to:

```text
.cds_pipeline/<school-slug>/
```

Artifacts:

- `candidate.json`
- `review.json`
- `review.md`

Use these when a school still needs manual follow-up.

## School Configs

School-specific rules belong in:

```text
cds_pipeline/configs/<slug>.json
```

Keep these small. Prefer config over new parser scripts.

Supported config categories today:

- `school_name`
- `source_hints`
- `form_aliases`
- `text_patterns`

Typical use cases:

- map school-specific AcroForm field names
- add alternate text patterns
- hint a preferred extractor for a messy source family

## When To Use Older Scripts

Treat the older `scripts/extract_*.py` files as legacy helpers.

They are still useful for:

- comparing behavior while migrating a school
- checking old parser assumptions
- temporary one-off recovery work

They should not be the default path for new school onboarding.

## Paid Services

Not recommended for v1.

If the local pipeline still leaves too many low-confidence PDFs, add one optional fallback behind a feature flag. If you go that route, prefer one provider only:

- Azure Document Intelligence
- Google Document AI

Do not make a paid provider the default operating path unless the local-first flow proves insufficient.
