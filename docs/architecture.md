# Architecture Notes

## App Structure

- `src/app/page.tsx`: homepage with the featured school grid and search
- `src/app/[school]/page.tsx`: dynamic route for individual school dashboards
- `src/app/[school]/SchoolPageClient.tsx`: client-side dashboard layout
- `src/components/charts/`: trend visualizations used on school pages
- `src/data/schools/`: normalized school datasets plus the shared registry manifest

## Data Model

School datasets follow the `SchoolData` / `YearData` schema in `src/lib/types.ts`:

- admissions
- test scores
- demographics
- costs
- financial aid

Each school JSON is keyed by academic year, typically from the late 2010s through the mid-2020s.

## Shared School Registry

`src/data/schools/index.ts` is the canonical source of truth for registered schools.

It owns:

- the ordered `allSchools` array used by the homepage
- the `schoolDataMap` used by dynamic routes
- `availableSchoolSlugs`
- `searchableSchools` derived from the latest year of each dataset

Adding a new school should usually require:

1. add `src/data/schools/<slug>.json`
2. register it in `src/data/schools/index.ts`
3. add its color in `SCHOOL_COLORS`
4. add search aliases if needed

## Extraction Architecture

The preferred ingestion flow is now the `cds_pipeline` package.

It follows a render-plus-review model:

- resolve a school's local CDS PDFs
- group them by year
- render every page to PNG screenshots
- write per-year manifests for Codex subagents
- merge the resulting year JSON into the final `SchoolData` schema
- run lightweight deterministic guardrails before site wiring

Important directories:

- `cds_pipeline/`: pipeline package
- `cds_pipeline/configs/`: school-specific hints and aliases
- `.cds_pipeline/`: generated screenshot manifests and rendered pages

The screenshot prep step should be the default path for new school ingestion. Older `scripts/extract_*.py` files are legacy utilities.

## Chart Layer

The active chart barrel exports only the trend charts used by the school dashboard:

- admissions
- test scores
- costs
- financial aid
- demographics

If a comparison page or single-year chart flow is reintroduced, keep that surface separate from the active dashboard exports.

## Behavior Constraints

- Keep UI and route behavior stable when refactoring.
- Preserve school ordering from the shared registry.
- Prefer internal simplifications over visible product changes.
- Run `npm run build` after school-registration or route changes.
