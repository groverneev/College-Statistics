# College Statistics

A data visualization dashboard for comparing colleges using Common Data Set (CDS) metrics. View historical trends for admissions, test scores, costs, financial aid, demographics, and latest-known admissions-factor metadata from CDS section C7.

**Live Site:** [collegestatistics.org](https://collegestatistics.org)

![Next.js](https://img.shields.io/badge/Next.js-16-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-38bdf8)

## Features

- **Admissions Trends** - Applications, acceptance rates, yield rates, early decision statistics
- **Test Score Trends** - SAT/ACT middle 50% ranges over time
- **Cost of Attendance** - Tuition, fees, room & board breakdown
- **Financial Aid** - Average grants, percent receiving aid, net price
- **Demographics** - Enrollment trends and racial/ethnic composition over time
- **Admissions Factors** - Latest CDS C7 matrix showing how schools classify academic and nonacademic admissions factors
- **Trends** - Data-driven stories and analyses (e.g. UC application volume comparisons)
- **Saved Schools** - Sign in with Google to save schools to a personal list, categorized as Reach / Target / Safety / Undecided. Logged-in users see their saved list as a quick-link chip row near the top of the homepage.
- **Notes** - Logged-in users can write a private, freeform note about any school (one note per school). Notes appear on the school dashboard and as a subtle indicator on school cards. Only the author can see their notes.

## Pages

- **Home** (`/`) - Dark landing page: an animated hero chart of real acceptance-rate trends with search, an auto-scrolling carousel of all school cards, and explore cards linking to Browse Schools / UC Explorer / Trends. Logged-in users also get a quick-link row of their saved schools.
- **Browse Schools** (`/schools`) - Full school grid with a save button on each card (available to everyone)
- **School Dashboard** (`/[school]`) - Detailed charts, tables, school-level admissions-factor metadata, a "Save to My List" button, and a private notes panel for logged-in users
- **Trends** (`/trends`) - Data-driven stories with charts and analysis
- **About** (`/about`) - Information about the project and creator
- **How it Works** (`/how-it-works`) - Explanation of CDS data and how to use the dashboard
- **Contact** (`/contact`) - Contact form and social links

## Project Structure

```text
College-Statistics/
|-- src/
|   |-- app/
|   |   |-- page.tsx
|   |   |-- schools/                 # Browse-all-schools page
|   |   |-- [school]/
|   |   |   `-- SchoolPageClient.tsx
|   |   |-- api/
|   |   |   |-- auth/[...nextauth]/   # NextAuth handler
|   |   |   |-- my-schools/           # Saved-schools CRUD (GET/POST, PATCH/DELETE)
|   |   |   `-- my-notes/             # Per-school notes (GET/POST upsert, DELETE)
|   |   `-- trends/
|   |-- components/
|   |   |-- charts/
|   |   |-- trends/
|   |   |-- Header.tsx                # Nav + sign in / avatar
|   |   |-- SaveSchoolButton.tsx      # Bookmark + category popover
|   |   |-- SavedSchoolsContext.tsx   # Client cache of the user's saved list
|   |-- NotesContext.tsx          # Client cache of the user's per-school notes
|   |   `-- SessionWrapper.tsx        # NextAuth SessionProvider
|   |-- data/
|   |   |-- schools/
|   |   |   |-- brown.json
|   |   |   |-- harvard.json
|   |   |   `-- ...
|   |   `-- trends/
|   |-- lib/
|   |   |-- auth.ts                   # NextAuth options (Google, JWT)
|   |   |-- prisma.ts                 # Prisma client singleton
|   |   `-- savedSchools.ts           # Cached server fetch + session helper
|   `-- utils/
|-- cds_pipeline/                     # CDS discovery, extraction, validation, and publishing
|-- prisma/
|   `-- schema.prisma                 # User, Account, SavedSchool, SchoolNote
|-- College-Data/
|   |-- Brown/
|   |-- Harvard/
|   `-- ...
|-- .venv/
|-- tailwind.config.ts
|-- next.config.ts
`-- package.json
```

## Development Docs

- Workflow, extraction, and architecture guidance: `CLAUDE.md`

## CDS Workflow

Install the pipeline once:

```bash
python -m pip install -e ".[dev]"
```

The default workflow is local and needs no API key. Install Ollama, then pull the two GPU models once:

```bash
ollama pull qwen3.5:9b
ollama pull gemma4:12b
```

Then acquire, extract, validate, add, and register a new college with one command:

```bash
python -m cds_pipeline add "Pomona College" --extractor auto --publish --strict
```

The command resolves the institution through College Scorecard, searches its official CDS archive, uses the College Transitions repository only as a fallback, downloads recent PDFs with provenance and hashes, and verifies the institution/year from the document itself. Stable C1, B1/B2, C9, G1, and H2 tables are extracted deterministically. Qwen 3.5 9B and Gemma 4 12B must independently agree on the latest visual C7 matrix; Gemma also handles nonstandard local layouts. Only routed table pages or pages needing OCR are rendered. Every published value is revalidated against the manifest's document, year, page, and source quote, and publication is blocked for missing evidence, conflicts, incomplete required fields, unresolved OCR, or failed semantic checks.

`--extractor auto` uses Ollama first. A signed-in Codex CLI can become the no-API-key adjudicator for unresolved packets using saved ChatGPT authentication, but it is opt-in because it launches an agent on document content: install the CLI, run `codex login`, and set `CDS_ENABLE_CODEX_FALLBACK=1`. The subprocess receives an allowlisted environment with project secrets removed. A direct OpenAI API remains optional through `--extractor openai` plus `OPENAI_API_KEY`; it is not required for the local workflow.

Useful staged commands:

```bash
python -m cds_pipeline discover "Pomona College"
python -m cds_pipeline add "Pomona College" --extractor auto --strict
python -m cds_pipeline compile pomona
python -m cds_pipeline compile pomona --publish
python -m cds_pipeline benchmark .cds_pipeline/brown/packets/2024-2025 --gold tests/fixtures/brown_2024_2025_gold.json --models qwen3.5:9b gemma4:12b
python -m cds_pipeline registry --check
python -m unittest discover -s tests -v
```

Override the role-based local defaults with `CDS_LOCAL_VISION_MODEL`, `CDS_LOCAL_EXTRACTION_MODEL`, `CDS_OLLAMA_CONTEXT`, or `--model`. Local GPU extraction is serialized by default to avoid model/context thrashing; set `CDS_LOCAL_EXTRACTION_JOBS` only after measuring available VRAM.

Generated evidence and extraction packets live in `.cds_pipeline/<slug>/`. Downloaded source records live in `College-Data/<slug>/sources.json`. `src/data/schools/index.ts` is generated from the school JSON files during publication, so adding imports by hand is no longer part of the workflow.

### OCR choices

Most CDS PDFs already contain usable text, so no OCR service is needed for them. For scanned or broken pages, `--ocr auto` uses the first configured provider:

- **Ollama vision OCR** (zero-key default): uses `qwen3.5:9b`; override with `CDS_LOCAL_OCR_MODEL`.
- **Unlimited-OCR** (recommended for a local NVIDIA GPU): run the official vLLM server and set `CDS_UNLIMITED_OCR_URL=http://127.0.0.1:8000/v1`.
- **Mistral OCR 4**: set `MISTRAL_API_KEY`.
- **PaddleOCR-VL 1.6**: use Python 3.12 and install `paddlepaddle paddleocr`.

To run Unlimited-OCR with Docker and an NVIDIA GPU:

```bash
docker run --rm --gpus all --ipc=host -p 8000:8000 \
  vllm/vllm-openai:unlimited-ocr baidu/Unlimited-OCR \
  --trust-remote-code \
  --logits_processors vllm.model_executor.models.unlimited_ocr:NGramPerReqLogitsProcessor \
  --no-enable-prefix-caching --mm-processor-cache-gb 0
```

When an Unlimited-OCR endpoint is configured it takes priority; otherwise the installed Ollama vision model provides an end-to-end local fallback. The main pipeline can stay on Python 3.11+; the heavyweight specialist OCR server is isolated from it.

## Data Sources

Most data is extracted from official Common Data Set (CDS) publications released by each institution.

## Tech Stack

- **Framework:** [Next.js 16](https://nextjs.org/) with App Router
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **Charts:** [Recharts](https://recharts.org/)
- **Auth:** [NextAuth.js](https://next-auth.js.org/) with Google OAuth (JWT sessions)
- **Database:** [Supabase](https://supabase.com/) Postgres via [Prisma](https://www.prisma.io/) (stores users and saved schools)
- **Data Preparation:** Python with PyMuPDF native extraction, selective OCR adapters, evidence-backed structured extraction, and blocking semantic validation
- **Contact Form:** [Formspree](https://formspree.io/)

## Environment Variables

Login and saved schools require the following in `.env.local` (and in your hosting provider's settings for production):

```bash
# Supabase Postgres
DATABASE_URL=     # pooler connection string (port 6543, append ?pgbouncer=true)
DIRECT_URL=       # direct connection string (port 5432) — used only by Prisma migrations

# NextAuth
NEXTAUTH_URL=     # e.g. http://localhost:3000 in dev
NEXTAUTH_SECRET=  # any random secret string

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

The database schema lives in `prisma/schema.prisma`. After changing it, run `npx prisma generate`. Apply schema changes to Supabase via the SQL editor (the local network may block the direct migration port).

## Contributing

Contributions are welcome! Areas where help is needed:

- Adding data for more schools
- Improving PDF extraction accuracy
- UI/UX improvements

## License

MIT

## Acknowledgments

- Common Data Set Initiative for standardized college data
- Individual institutions for publishing their CDS reports

## Contact

- **Website:** [neevgrover.com](https://neevgrover.com)
- **Blog:** [techunpacked.substack.com](https://techunpacked.substack.com)
- **Twitter:** [@groverneev01](https://x.com/groverneev01)
- **GitHub:** [groverneev](https://github.com/groverneev)
