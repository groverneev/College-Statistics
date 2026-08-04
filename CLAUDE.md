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
- acquisition, extraction, validation, and publishing automation in `cds_pipeline/`
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

The pipeline writes `src/data/schools/<slug>.json` and regenerates the import/array portions of `index.ts` during publication. `SCHOOL_METADATA` remains hand-curated only when a custom color, aliases, or featured status is desired; new schools safely use the default color and their canonical name without it.

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

## Evidence-First CDS Workflow

The supported path for adding a college is an automated acquisition-to-publication pipeline. Do not revive the old render-every-page workflow or school-specific extraction configs.

### Add A New School

Install once:

```bash
uv sync --extra dev
ollama pull qwen3.5:9b
ollama pull gemma4:12b
```

Run the complete workflow:

```bash
uv run python -m cds_pipeline add "Pomona College" --extractor auto --publish --strict
```

No API key is required. Exact labeled CDS rows, including C7, are parsed deterministically first. Qwen 3.5 9B and Gemma 4 12B independently verify C7 only when deterministic recovery is incomplete; Gemma handles other nonstandard local layouts, and a signed-in Codex CLI is an opt-in adjudicator using saved ChatGPT authentication. `--publish` includes every independently safe, complete year, reports and excludes incomplete years, and remains blocked when no complete year survives or compiled data fails validation.

The command:

1. resolves the official institution domain through College Scorecard;
2. discovers official CDS archive links and then fills missing years from College Transitions;
3. downloads recent PDFs atomically and records URLs, hashes, year labels, and official/mirror provenance in `College-Data/<slug>/sources.json`;
4. verifies the document's CDS identity, institution match, and academic year from its contents;
5. uses native PDF text, words, and tables first;
6. extracts stable B1/B2, C1, C9, G1, and H2 rows deterministically and routes only the exact question blocks needed;
7. renders table-heavy B/H evidence, visual C7 evidence, and pages that actually require OCR;
8. sends only nonstandard or visual leftovers to local models, with Codex/OpenAI fallback when configured;
9. emits strict, source-quoted observations into `.cds_pipeline/<slug>/extractions/`;
10. derives rates and totals, excludes unsafe/incomplete years with explicit reasons, runs blocking semantic validation on the retained years, writes the school JSON, and regenerates the registry.

Document analysis and packet extraction are cached separately. Extraction cache signatures include the packet hash, extraction parser version, provider chain, and local/hosted model configuration. An unchanged rerun must report cache hits and must not repeat model inference.

School-name targets always use discovery, even when `College-Data/<slug>/` already exists. Only an explicit PDF or directory path requests local-file ingestion. The discovery `--years` selection is authoritative and must not be replaced by rescanning older files in the cache directory. Analyze PDFs serially: PyMuPDF table extraction can leak table state across documents when called concurrently in threads. Flattened native-text continuations without formal table artifacts must remain routed to their inherited CDS domain.

Staged commands for diagnosis or manual review:

```bash
uv run python -m cds_pipeline discover "Pomona College"
uv run python -m cds_pipeline add "Pomona College" --extractor auto --strict
uv run python -m cds_pipeline compile pomona
uv run python -m cds_pipeline compile pomona --publish
uv run python -m cds_pipeline benchmark .cds_pipeline/brown/packets/2024-2025 --gold tests/fixtures/brown_2024_2025_gold.json --models qwen3.5:9b gemma4:12b
uv run python -m cds_pipeline validate <json-file>
uv run python -m cds_pipeline registry --check
```

If a school uses a nonstandard archive that discovery cannot locate, pass its official page with `--archive-url`. Use `--years 0` for all available years; the default is the newest eight.

### Structured Extraction Policy

- `--extractor auto` is the supported default: deterministic table rules first, then Ollama, then Codex only when `CDS_ENABLE_CODEX_FALLBACK=1`, then OpenAI only if configured.
- `CDS_LOCAL_VISION_MODEL` defaults to `qwen3.5:9b`; `CDS_LOCAL_EXTRACTION_MODEL` defaults to `gemma4:12b`.
- The local model is called only when deterministic extraction is incomplete. Local calls are serialized by default; override with `CDS_LOCAL_EXTRACTION_JOBS` only after measuring VRAM.
- Codex runs ephemerally, read-only, approval-free, and schema-constrained. It receives an environment allowlist with project credentials and API keys removed so it uses saved ChatGPT authentication without exposing repo secrets.
- A non-null value is invalid unless its quote is on a routed page and contains the reported numeric value. Deterministic semantic validation still runs after extraction.
- Use the checked-in Brown gold fixture and `cds_pipeline benchmark` before changing default models. Model release recency alone is not a selection criterion.

### OCR Policy

OCR is a fallback, never the default for every page. `--ocr auto` selects the first configured provider:

- Ollama vision OCR: zero-key fallback using `qwen3.5:9b` (override with `CDS_LOCAL_OCR_MODEL`).
- Unlimited-OCR: run the official vLLM server and set `CDS_UNLIMITED_OCR_URL=http://127.0.0.1:8000/v1`.
- Mistral OCR 4: set `MISTRAL_API_KEY`.
- PaddleOCR-VL 1.6: use a Python 3.12 environment and install `paddlepaddle paddleocr`.

When configured, Unlimited-OCR takes priority over Ollama. The main pipeline supports Python 3.11+. Keep a local Unlimited-OCR/vLLM or Paddle environment separate rather than forcing CUDA dependencies into the application environment. If no provider is configured and routed pages need OCR, the manifest remains review-required and publication is blocked.

### Evidence and Data Rules

- Never publish a non-null extracted value without a document ID, page, and quote that matches the routed source text.
- Never estimate, interpolate, or copy values across years.
- Prefer official sources. Repository mirrors are allowed only with post-download institution/year/CDS verification and recorded provenance.
- Treat C7 admissions factors as latest-known school metadata and retain its source year/PDF.
- The compiler, not the extractor, derives acceptance rate, yield, enrollment total when components exist, and the site's displayed tuition + fees + room/board total.
- Missing required fields or document-level safety problems exclude the affected academic year. Conflicts, ambiguous years, weak institution matches, unresolved OCR, and invalid evidence may never leak values into a retained year. Publication fails when no complete verified year remains or retained data fails semantic validation.

### Validation and Verification

The deterministic validator checks admissions ordering and rate reconciliation, percentile ordering, percentage ranges, enrollment reconciliation, race/residency plausibility, negative values, and cost reconciliation. These are guardrails; they do not replace source verification.

After pipeline or school-registration changes, run:

```bash
uv run python -m unittest discover -s tests -v
uv run python -m cds_pipeline registry --check
npm run build
```

Important directories:

- `cds_pipeline/`: acquisition, document analysis, selective OCR, extraction, compilation, validation, and registry generation
- `.cds_pipeline/<slug>/`: cached evidence artifacts, packets, observations, manifests, and compiler reports
- `College-Data/<slug>/`: downloaded PDFs and source provenance
- `src/data/schools/`: publishable school JSON and generated static registry

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

## Git Commits

- Do **not** add a `Co-Authored-By: Claude ...` trailer to commit messages. Commits in this repo are authored by the repo owner only.
- Commit only when asked.
