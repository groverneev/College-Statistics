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
- **Saved Schools** - Sign in with Google to save schools to a personal list, categorized as Reach / Target / Safety / Undecided. Logged-in users see their saved list (grouped by category) on the homepage instead of the featured grid.

## Pages

- **Home** (`/`) - For logged-out visitors: featured school grid with key stats. For logged-in users: their saved schools grouped by Reach / Target / Safety / Undecided.
- **Browse Schools** (`/schools`) - Full school grid with a save button on each card (available to everyone)
- **School Dashboard** (`/[school]`) - Detailed charts, tables, school-level admissions-factor metadata, and a "Save to My List" button
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
|   |   |   `-- my-schools/           # Saved-schools CRUD (GET/POST, PATCH/DELETE)
|   |   `-- trends/
|   |-- components/
|   |   |-- charts/
|   |   |-- trends/
|   |   |-- Header.tsx                # Nav + sign in / avatar
|   |   |-- SaveSchoolButton.tsx      # Bookmark + category popover
|   |   |-- SavedSchoolsContext.tsx   # Client cache of the user's saved list
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
|-- prisma/
|   `-- schema.prisma                 # User, Account, SavedSchool
|-- scripts/
|   |-- extract_cds.py
|   `-- extract_*.py
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

## Data Sources

Most data is extracted from official Common Data Set (CDS) publications released by each institution.

## Tech Stack

- **Framework:** [Next.js 16](https://nextjs.org/) with App Router
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **Charts:** [Recharts](https://recharts.org/)
- **Auth:** [NextAuth.js](https://next-auth.js.org/) with Google OAuth (JWT sessions)
- **Database:** [Supabase](https://supabase.com/) Postgres via [Prisma](https://www.prisma.io/) (stores users and saved schools)
- **Data Extraction:** Python with [PyMuPDF](https://pymupdf.readthedocs.io/) plus Codex-assisted screenshot review
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
