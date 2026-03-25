# College Statistics

A data visualization dashboard for comparing colleges using Common Data Set (CDS) metrics. View historical trends for admissions, test scores, costs, financial aid, and demographics.

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
- **Trends** - Data-driven stories and analyses (e.g. UC application volume comparisons)

## Currently Available Schools

| School | Years | Data Points |
|--------|-------|-------------|
| Boston University | 2016-2025 | 9 years |
| Brown University | 2016-2025 | 9 years |
| California Institute of Technology (Caltech) | 2016-2025 | 9 years |
| Carnegie Mellon University (CMU) | 2016-2025 | 9 years |
| Columbia University | 2016-2025 | 9 years |
| Cornell University | 2017-2025 | 8 years |
| Dartmouth College | 2016-2025 | 9 years |
| Duke University | 2016-2025 | 9 years |
| Emory University | 2017-2025 | 8 years |
| Georgia Institute of Technology | 2016-2026 | 10 years |
| Harvard University | 2016-2025 | 9 years |
| Johns Hopkins University | 2016-2025 | 9 years |
| Massachusetts Institute of Technology (MIT) | 2016-2025 | 9 years |
| Northeastern University | 2016-2025 | 9 years |
| New York University (NYU) | 2017-2025 | 8 years |
| Northwestern University | 2016-2025 | 9 years |
| Princeton University | 2016-2025 | 9 years |
| Rice University | 2016-2025 | 9 years |
| Purdue University | 2016-2026 | 10 years |
| Stanford University | 2016-2025 | 9 years |
| UCLA | 2017-2025 | 8 years |
| University of California, Berkeley (UC Berkeley) | 2016-2025 | 9 years |
| University of California, Irvine (UCI) | 2016-2025 | 9 years |
| University of Chicago (UChicago) | 2021-2025 | 4 years |
| University of Michigan Ann Arbor | 2016-2025 | 9 years |
| University of Pennsylvania (UPenn) | 2016-2025 | 9 years |
| University of Southern California (USC) | 2016-2025 | 9 years |
| The University of Texas at Austin | 2016-2025 | 9 years |
| University of Virginia | 2019-2025 | 6 years |
| Vanderbilt University | 2016-2025 | 9 years |
| Yale University | 2016-2025 | 9 years |

## Pages

- **Home** (`/`) - School selector with key stats
- **School Dashboard** (`/[school]`) - Detailed charts and data for each school
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

## Data Sources

Most data is extracted from official Common Data Set (CDS) publications released by each institution. The CDS is a collaborative effort among data providers in higher education that provides comparable data across institutions. Some schools in this repo use PDF sources, Northeastern publishes year-by-year CDS data as webpages, Rice uses a dedicated parser for its official 2016-2025 CDS PDF archive, USC uses its official CDS archive pages plus linked PDFs, UChicago uses a dedicated PDF parser for its official 2021-2025 CDS archive, UCI uses a dedicated PDF parser for its CDS archive with web-backed cost overrides for 2018-2019 through 2020-2021, Johns Hopkins uses a dedicated parser for its local 2021-2025 CDS PDFs plus a mixed-source web backfill for older missing years, Michigan uses a dedicated parser for its 2016-2025 CDS PDFs, UVA currently uses a mixed official-source dataset built from local 2022-2025 CDS PDFs plus UVA's official 2020-2022 CDS webpages and a web-sourced 2019-2020 backfill, Vanderbilt uses CDS Excel workbooks, and Purdue uses a mixed Excel/PDF archive across 2016-2026.

## Tech Stack

- **Framework:** [Next.js 16](https://nextjs.org/) with App Router
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **Charts:** [Recharts](https://recharts.org/)
- **Data Extraction:** Python with [pdfplumber](https://github.com/jsvine/pdfplumber), [openpyxl](https://openpyxl.readthedocs.io/), and [xlrd](https://xlrd.readthedocs.io/)
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
