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

## Currently Available

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
| Harvard University | 2016-2025 | 9 years |
| Johns Hopkins University | 2016-2025 | 9 years |
| Massachusetts Institute of Technology (MIT) | 2016-2025 | 9 years |
| Northeastern University | 2016-2025 | 9 years |
| New York University (NYU) | 2017-2025 | 8 years |
| Northwestern University | 2016-2025 | 9 years |
| Princeton University | 2016-2025 | 9 years |
| Purdue University | 2016-2026 | 10 years |
| Stanford University | 2016-2025 | 9 years |
| UCLA | 2017-2025 | 8 years |
| University of California, Berkeley (UC Berkeley) | 2016-2025 | 9 years |
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

```
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── [school]/           # Dynamic school pages
│   │   ├── trends/             # Trends index + story pages
│   │   ├── about/              # About page
│   │   ├── how-it-works/       # How it Works page
│   │   ├── contact/            # Contact page
│   ├── components/
│   │   ├── charts/             # Recharts visualizations
│   │   ├── trends/             # Trends story components
│   │   ├── Header.tsx          # Navigation header
│   │   └── Footer.tsx          # Site footer
│   ├── data/
│   │   ├── schools/            # CDS JSON data files
│   │   └── trends/             # Trends story data files
│   └── lib/types.ts            # TypeScript interfaces
├── scripts/
│   └── extract_cds.py          # PDF data extraction
└── College-Data/               # Source CDS PDFs by school
    ├── Brown/
    ├── Caltech/
    ├── Columbia/
    └── ...
```

## Data Sources

Most data is extracted from official Common Data Set (CDS) publications released by each institution. The CDS is a collaborative effort among data providers in higher education that provides comparable data across institutions. Some schools in this repo use PDF sources, Northeastern publishes year-by-year CDS data as webpages, USC uses its official CDS archive pages plus linked PDFs, UChicago uses a dedicated PDF parser for its official 2021-2025 CDS archive, Johns Hopkins uses a dedicated parser for its local 2021-2025 CDS PDFs plus a mixed-source web backfill for older missing years, Michigan uses a dedicated parser for its 2016-2025 CDS PDFs, UVA currently uses a mixed official-source dataset built from local 2022-2025 CDS PDFs plus UVA's official 2020-2022 CDS webpages and a web-sourced 2019-2020 backfill, Vanderbilt uses CDS Excel workbooks, and Purdue uses a mixed Excel/PDF archive across 2016-2026.

## Extracting Data

To extract data from new CDS PDFs:

```bash
# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install pdfplumber

# Extract data for a school
python scripts/extract_cds.py brown --pdf-dir ./College-Data/Brown
```

To extract Vanderbilt from its CDS Excel workbooks:

```bash
python scripts/extract_vanderbilt_excel.py
```

To extract Purdue from its mixed CDS archive:

```bash
python scripts/extract_purdue.py
```

To extract UT Austin, including the missing 2022-2023 Box-hosted CDS year:

```bash
python scripts/extract_utexasaustin.py
```

To extract Boston University from its BU-specific PDF naming and layout:

```bash
python scripts/extract_bostonuniversity.py
```

To extract USC from its official CDS archive pages and linked PDFs:

```bash
python scripts/extract_usc.py
```

To extract UChicago from its official CDS PDFs:

```bash
python scripts/extract_uchicago.py
```

To extract Johns Hopkins from its CDS PDFs and older web backfills:

```bash
python scripts/extract_johnshopkins.py
```

To extract Emory from its local CDS PDFs plus archived official older-year PDFs:

```bash
python scripts/extract_emory.py
```

To extract the University of Michigan Ann Arbor from its CDS PDFs:

```bash
python scripts/extract_umich.py
```

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
- Building the comparison feature
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
