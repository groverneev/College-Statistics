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
