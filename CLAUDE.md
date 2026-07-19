# College Statistics - Working Guide

> **WORKTREE:** Work directly in the main repository. Do not create git worktrees.

> **PDF HANDLING:** Do not read PDFs directly with the Read tool. Use the screenshot prep command or shell-based helpers instead.

> **DATA RULE:** Never invent data. If extraction is incomplete, verify against official institutional sources and keep definitions consistent within a school's time series. Feel free to use web searches if local PDFs are incomplete or ambiguous.

> **SOURCE DISCOVERY:** When official school CDS links are stale or hard to find, check the College Transitions Common Data Set Repository first as a discovery index, then download and verify the actual linked CDS file before using it in the dataset.

> **DEPENDENCIES:** If extra local tooling is needed, tell the user exactly what to install instead of assuming it is available or trying to work around missing packages silently.

> **PATCH SIZE:** Prefer smaller, staged edits over sweeping all-at-once patches. Large multi-file changes may get rejected by the editing tool, so break them into focused chunks when implementing bigger features.

## Repo Purpose

This is a Next.js site for exploring Common Data Set trends across colleges.

The repo contains:

- local source files in `College-Data/<School>/`
- screenshot prep and validation helpers in `cds_pipeline/`
- normalized datasets in `src/data/schools/`

## App Structure

- `src/app/page.tsx`: dark Linear-style homepage, built as a funnel to /schools, /uc, and /trends — hero search + `HeroTrendChart` (real acceptance-rate lines in a floating window), `SchoolCarousel` (auto-scrolling marquee of the same `SchoolCard` boxes used on /schools), and `ExploreTiles` dark cards. The full sortable catalog lives at `/schools`, not on the homepage. `Header` renders a translucent dark variant on `/` only; dark-surface utilities (`.hero-dark`, `.explore-card`, `.chip-dark`, `.marquee-track`) live in `globals.css`.
- `src/app/[school]/page.tsx`: dynamic route for individual school dashboards
- `src/app/[school]/SchoolPageClient.tsx`: client-side dashboard layout
- `src/components/charts/`: trend visualizations used on school pages
- `src/data/schools/`: normalized school datasets plus the shared registry manifest

## Data Model

School datasets follow the `SchoolData` / `YearData` schema in `src/lib/types.ts`:

- optional school-level `profile` metadata
- admissions
- test scores
- demographics
- costs
- financial aid

Each school JSON is keyed by academic year, typically from the late 2010s through the mid-2020s.

School-level metadata should be used for information that is not primarily a yearly trend series. The current example is `profile.admissionsFactors`, which stores the latest available CDS C7 admissions-factor matrix plus source metadata.

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
3. add its metadata there as needed (`SCHOOL_METADATA` color, aliases, featured flag)

## Accounts & Saved Schools

The site has optional Google login backed by a Supabase Postgres database (via Prisma). Logged-in users can save schools to a personal list, categorized as Reach / Target / Safety / Undecided, and can write a private freeform note about any school (one note per school, independent of whether it is saved).

### Key files

- `src/lib/auth.ts`: NextAuth options. Google provider, **JWT session strategy** (the user id is carried in the encrypted cookie via the `jwt`/`session` callbacks — no DB lookup per request). `PrismaAdapter` persists `User` + `Account` rows on sign-in.
- `src/lib/prisma.ts`: Prisma client singleton.
- `src/lib/savedSchools.ts`: `getSession` (React-cached `getServerSession`) and `getSavedSchoolsForUser` (per-user `unstable_cache`, tagged `saved-schools-<userId>`).
- `src/lib/notes.ts`: `getNotesForUser` (per-user `unstable_cache`, tagged `school-notes-<userId>`). Reuses `getSession` from `savedSchools.ts`.
- `src/app/api/auth/[...nextauth]/route.ts`: NextAuth handler.
- `src/app/api/my-schools/`: saved-schools CRUD. `GET`/`POST` on the collection, `PATCH`/`DELETE` on `[slug]`. All require a session and validate `schoolSlug` against `availableSchoolSlugs` and `category` against the `Category` enum. Mutations call `revalidateTag` to purge the user's cache.
- `src/app/api/my-notes/`: per-school notes. `GET` (list) / `POST` (upsert by `userId + schoolSlug`) on the collection, `DELETE` on `[slug]`. Session-gated, slug-validated against `availableSchoolSlugs`, note body validated (non-empty, max 5000 chars). `shared.ts` re-exports the auth/slug helpers from `my-schools/shared`. Mutations `revalidateTag` the user's notes cache.
- `src/components/SavedSchoolsContext.tsx`: client-side cache of the user's list. **Initialized directly from server-seeded data** (`useState(initialSavedSchools)`) so SSR renders the list with no flash. Mutations are optimistic (update local state first, sync in the background).
- `src/components/NotesContext.tsx`: client-side cache of the user's notes, same server-seeded + optimistic pattern as `SavedSchoolsContext`. Exposes `getNote` / `hasNote` / `saveNote` / `deleteNote`.
- `src/components/SaveSchoolButton.tsx`: bookmark icon (cards) and full button (school page) with the category popover. Reads/writes through the context — never fetches per-button.
- `src/components/SchoolNotes.tsx`: notes panel on the school dashboard (view / empty / editor states). Logged-out clicks call `promptSignIn` from `SavedSchoolsContext`.
- `src/components/CardNoteIndicator.tsx`: subtle "Note" chip + one-line preview on school cards; renders nothing when the school has no note.
- `src/components/Header.tsx`: nav with Browse Schools link + sign in / avatar.

### Data flow (important)

- The **root layout** (`src/app/layout.tsx`) is the single place that resolves auth: it calls `getSession()` and, when logged in, `getSavedSchoolsForUser()` + `getNotesForUser()` (in parallel), then seeds `SessionWrapper`, `SavedSchoolsProvider`, and `NotesProvider`. Because the layout reads the session cookie, all routes are server-rendered (`ƒ`), not static. With JWT sessions this is cheap (no DB round trip for auth).
- Do **not** reintroduce per-component `fetch("/api/my-schools")` or `fetch("/api/my-notes")` for reads. The providers already hold the data; components should use `useSavedSchools()` / `useNotes()`.

### Schema

`prisma/schema.prisma` defines `User`, `Account`, `SavedSchool`, and `SchoolNote` only. `Session` and `VerificationToken` were intentionally removed because the JWT strategy does not use them — do not re-add them unless switching to database sessions or a passwordless/email provider. `SchoolNote` is keyed `@@unique([userId, schoolSlug])` (one note per user per school) with `onDelete: Cascade` from `User`.

### Database changes

The local network may block the Prisma migration port (5432). Generate SQL with `npx prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script` (or a targeted diff) and run it in the Supabase SQL editor. Always run `npx prisma generate` after editing the schema. The dev server locks the Prisma engine on Windows — stop it before regenerating. Hand-written/targeted migration SQL is kept under `prisma/migrations_manual/` (e.g. `add_school_note.sql`) for pasting into the Supabase SQL editor.

> **Migration ordering:** the root layout calls the per-user data loaders on every logged-in page load, so a new table must exist in Supabase **before** the code that reads it goes live — otherwise logged-in page loads error. Run the SQL first, then deploy/restart.

### Required environment variables

`DATABASE_URL` (pooler, `?pgbouncer=true`), `DIRECT_URL` (direct, migrations only), `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`. See `README.md` for details.

## Codex-First CDS Workflow

This repo uses a Codex-first screenshot workflow for school ingestion.

The repo-side automation is intentionally narrow:

- resolve a school's local CDS PDFs
- group them by year
- render every PDF page to PNG screenshots
- write per-year manifests for Codex subagents
- run lightweight deterministic guardrails on the resulting JSON

Codex then reads those screenshots and produces the structured year JSON used for the website.

### Default Command

The Python pipeline is managed with [uv](https://docs.astral.sh/uv/). Run `uv sync` once to set up the environment, then use:

```bash
uv run python -m cds_pipeline prepare <school-or-path>
```

`uv run python -m cds_pipeline extract <school-or-path>` remains as a backward-compatible alias for the same render-only prep step.

### Workspace Output

The prep step writes artifacts to:

```text
.cds_pipeline/<school-slug>/
```

For each year it creates:

- `pages/`: rendered PNG screenshots in page order
- `manifest.json`: the year handoff packet for a Codex subagent

It also writes:

- `school_manifest.json`: summary of all year manifests for the school

Each year manifest includes:

- `school_slug`
- `school_name`
- `year`
- `source_pdfs`
- `page_count`
- `screenshot_paths`
- `screenshots`
- `subagent_prompt`
- `output_contract`

### Codex Handoff Model

Recommended operator flow:

1. Add new CDS PDFs to `College-Data/<School>/`.
   - If the school's official archive is incomplete or broken, use the College Transitions Common Data Set Repository as a discovery aid for missing CDS files:
     `https://www.collegetransitions.com/dataverse/common-data-set-repository/`
2. Run `uv run python -m cds_pipeline prepare <school-or-path>`.
3. Inspect `.cds_pipeline/<slug>/school_manifest.json` and the per-year manifests.
4. Give one year's manifest and screenshots to one Codex subagent.
5. Have that subagent return strict JSON with `year`, `data`, and `notes`.
6. Merge the per-year outputs into `src/data/schools/<slug>.json`.
7. Run guardrails and site wiring checks before finishing.

### What Codex Should Extract

Per year, the subagent should build the existing `YearData` schema:

- admissions
- test scores
- demographics
- costs
- financial aid

The subagent may derive obvious schema values when the visible source values support them directly:

- acceptance rate
- yield
- total enrollment
- total cost of attendance

If an optional field is not visible, omit it. If a required field cannot be recovered safely, note that explicitly instead of guessing.

For each school, Codex should also proactively check the latest available CDS for section `C7` and populate school-level `profile.admissionsFactors` metadata when it can be recovered safely. Treat this as a latest-known school attribute, not a year-by-year time series, and store the source year / source PDF alongside the factor matrix.

## Add A New School

Use this checklist:

1. Run `uv run python -m cds_pipeline prepare <school-or-path>`.
2. Use the per-year manifests and screenshots for Codex extraction.
3. Finalize `src/data/schools/<slug>.json` with complete, source-backed data.
4. Proactively extract the latest CDS `C7` admissions-factor matrix into `profile.admissionsFactors` when available.
5. Register the school in `src/data/schools/index.ts`.
6. Add the school color in `src/lib/types.ts`.
7. Add aliases in `src/components/SearchBar.tsx` if the school needs abbreviation support.
8. Update any user-facing hardcoded copy only if it is not already derived from the registry.
9. Update `README.md` only if the public-facing behavior or documented coverage changed.
10. Run `npm run build`.

## Data Quality Checks

Before finishing school data work:

- confirm values are source-backed
- check for suspiciously flat or overly round trends
- verify race/residency totals reconcile with undergraduate enrollment
- verify costs and admissions values look consistent year over year

## Validation

The lightweight validator is deterministic only. It checks:

- `acceptanceRate == admitted / applied`
- `yield == enrolled / admitted`
- `total enrollment == undergraduate + graduate`
- race totals are plausible against undergraduate enrollment
- residency totals are plausible against undergraduate enrollment
- `totalCOA == tuition + fees + roomAndBoard`

These checks are guardrails, not a second extraction pipeline.

Use official web-backed/manual overrides only when:

- the local CDS is missing the value
- the screenshots do not show the needed field clearly
- the PDF is too ambiguous to verify safely from the screenshots alone
- the official institutional web source clearly states the needed value

## Verification Checklist

Run these after significant changes:

- `npm run build`
- verify the homepage still renders the expected schools
- verify at least one direct school route works
- verify search still finds schools and aliases

For each updated year:

- `undergraduate + graduate == total`
- `sum(byRace)` is plausible against undergraduate enrollment
- `sum(byResidency)` is plausible against undergraduate enrollment
- costs look plausible and vary year over year
- acceptance rate and yield reconcile with applied/admitted/enrolled counts

## Architecture Notes

The screenshot prep step is the only supported path for new school ingestion.

Important directories:

- `cds_pipeline/`: screenshot prep and validation package
- `cds_pipeline/configs/`: school-specific hints and aliases
- `.cds_pipeline/`: generated screenshot manifests and rendered pages
- `src/data/schools/index.ts`: canonical school registry plus app-facing metadata (colors, aliases, featured schools)

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
- When working on a school dataset, proactively look for latest CDS `C7` admissions-factor data and add `profile.admissionsFactors` if it is source-backed.
- Run `npm run build` after school-registration or route changes.
- Always update `CLAUDE.md` and `README.md` after changing workflow or architecture guidance.
