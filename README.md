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

## Pages

- **Home** (`/`) - School selector with key stats
- **School Dashboard** (`/[school]`) - Detailed charts, tables, and school-level admissions-factor metadata
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
|   |   |-- [school]/
|   |   |   `-- SchoolPageClient.tsx
|   |   `-- trends/
|   |-- components/
|   |   |-- charts/
|   |   `-- trends/
|   |-- data/
|   |   |-- schools/
|   |   |   |-- brown.json
|   |   |   |-- harvard.json
|   |   |   `-- ...
|   |   `-- trends/
|   |-- lib/
|   `-- utils/
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
- **Data Extraction:** Python with [PyMuPDF](https://pymupdf.readthedocs.io/) plus Codex-assisted screenshot review
- **Contact Form:** [Formspree](https://formspree.io/)

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
