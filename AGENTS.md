# College Statistics

Next.js application with a Python pipeline for publishing Common Data Set statistics.

## Project Rules

- Work directly in the main repository; do not create git worktrees.
- Never invent, estimate, interpolate, or copy college data across years.
- Published values must be backed by source evidence. Missing values are preferable to unsupported values.
- Use the existing `cds_pipeline` workflow for school data; do not add school-specific extraction systems.
- When adding or updating a school, include the latest source-backed C7 admissions factors when available.
- Prefer official institutional sources. Mirrors may be used only after verifying the institution, CDS year, and document identity.

For pipeline usage, setup, architecture, and environment variables, see `README.md` and command help:

```bash
uv run python -m cds_pipeline --help
```

Before completing pipeline or school-registration changes, run:

```bash
uv run python -m unittest discover -s tests -v
uv run python -m cds_pipeline registry --check
npm run build
```

Commit only when asked. Do not add a `Co-Authored-By: __model_name__` trailer.
