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

## Currently Available

| School | Years | Data Points |
|--------|-------|-------------|
| Brown University | 2016-2025 | 9 years |
| California Institute of Technology (Caltech) | 2016-2025 | 9 years |
| Harvard University | 2016-2025 | 9 years |
| Princeton University | 2016-2025 | 9 years |
| Stanford University | 2016-2025 | 9 years |
| University of Pennsylvania (UPenn) | 2016-2025 | 9 years |
| Yale University | 2016-2025 | 9 years |

## Pages

- **Home** (`/`) - School selector with key stats
- **School Dashboard** (`/[school]`) - Detailed charts and data for each school
- **About** (`/about`) - Information about the project and creator
- **How it Works** (`/how-it-works`) - Explanation of CDS data and how to use the dashboard
- **Contact** (`/contact`) - Contact form and social links

## Project Structure

```
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── [school]/           # Dynamic school pages
│   │   ├── about/              # About page
│   │   ├── how-it-works/       # How it Works page
│   │   ├── contact/            # Contact page
│   │   └── compare/            # School comparison page
│   ├── components/
│   │   ├── charts/             # Recharts visualizations
│   │   ├── Header.tsx          # Navigation header
│   │   └── Footer.tsx          # Site footer
│   ├── data/schools/           # JSON data files
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

All data is extracted from official Common Data Set (CDS) publications released by each institution. The CDS is a collaborative effort among data providers in higher education that provides comparable data across institutions.

## Extracting Data from PDFs

To extract data from new CDS PDFs:

```bash
# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install pdfplumber

# Extract data for a school
python scripts/extract_cds.py brown --pdf-dir ./College-Data/Brown
```

## Tech Stack

- **Framework:** [Next.js 16](https://nextjs.org/) with App Router
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **Charts:** [Recharts](https://recharts.org/)
- **Data Extraction:** Python with [pdfplumber](https://github.com/jsvine/pdfplumber)
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
