# PDF Extraction Pipeline

This repo now uses a vision-first CDS extraction pipeline under `cds_pipeline/`.

The goal is to turn Common Data Set PDFs into structured school JSON by:

- rendering PDF pages into screenshots
- using an OpenAI vision model to find relevant CDS sections
- extracting only schema-allowed fields from those section pages
- normalizing into the site schema
- validating the result
- emitting review artifacts instead of silently guessing

## Default Recommendation

Use the pipeline directly:

```bash
python -m cds_pipeline extract <school-or-path>
```

Examples:

```bash
python -m cds_pipeline classify tufts
python -m cds_pipeline extract tufts
python -m cds_pipeline review .cds_pipeline/tufts/candidate.json
python -m cds_pipeline export .cds_pipeline/tufts/candidate.json
```

The current pipeline requires:

- `OPENAI_API_KEY`
- optionally `OPENAI_MODEL`

These can be supplied via environment variables or a repo-local `.env.local` file.

## Pipeline Stages

### 1. Classify

Each PDF is treated as a `vision_pdf`.

The classifier currently records:

- `document_type = vision_pdf`
- page count
- extractor chain

The extractor chain is currently just:

- `VisionLLMExtractor`

### 2. Render And Section Classify

The vision extractor renders PDF pages to PNG screenshots using PyMuPDF.

It then sends pages to OpenAI vision in small batches and asks which CDS sections are present on each page from this fixed set:

- `B1`
- `B2`
- `C1`
- `C9`
- `F1`
- `G1`
- `H2`

The model must return strict JSON only.

### 3. Section Extraction

For each detected section page, the pipeline sends that page back to OpenAI vision with:

- a section-specific prompt
- a strict allowlist of field paths for that section

Examples:

- `C1` can return only admissions counts
- `G1` can return only costs fields
- `H2` can return only financial-aid fields

The extractor writes raw payload keys such as:

- `vision_sections`
- `vision_field_candidates`
- `vision_missing_sections`
- `vision_notes`

### 4. Normalize

The normalizer converts the vision field candidates into the existing school JSON schema:

- admissions
- test scores
- demographics
- costs
- financial aid

It keeps the highest-confidence candidate per field, records provenance in `field_meta`, and derives secondary values such as:

- `acceptanceRate`
- `yield`
- `totalCOA`
- total enrollment
- residency counts derived from out-of-state percentage when needed

### 5. Validate

The validator checks:

- admissions rate reconciliation
- yield reconciliation
- enrollment totals
- race totals vs undergraduate enrollment
- residency totals vs undergraduate enrollment
- `totalCOA == tuition + fees + roomAndBoard`

### 6. Review

The pipeline writes artifacts to:

```text
.cds_pipeline/<school-slug>/
```

Artifacts:

- `candidate.json`
- `review.json`
- `review.md`

Review output includes:

- sections found
- sections not found
- low-confidence fields
- validation issues
- extractor notes

## School Configs

School-specific rules belong in:

```text
cds_pipeline/configs/<slug>.json
```

Supported config categories today:

- `school_name`
- `source_hints`
- `vision.enabled`
- `vision.model`
- `vision.render_dpi`
- `vision.classify_batch_size`
- `vision.max_pages_per_section`
- `vision.section_targets`
- `vision.section_aliases`
- `vision.page_range_hints`

Typical use cases:

- narrow the pages searched for a section
- add school-specific section aliases
- reduce or increase batch size
- disable vision temporarily for debugging

## Current Constraints

- The pipeline is vision-first only; legacy text, OCR, and table extractors are no longer part of the active flow.
- Structured outputs depend on OpenAI returning schema-valid JSON.
- Long school archives can still take time because every PDF page must be rendered and classified, even though classification is now batched.
- Validation and review are still required; the model output is not trusted blindly.
