# College Comparisons - Project Documentation

> **WARNING:** Do NOT attempt to read PDF files directly using the Read tool. The PDF files in this project (e.g., `Brown/*.pdf`) are large and will overload the context window. Always use the Python extraction script (`scripts/extract_cds.py`) to extract data from PDFs instead.

> **NOTE:** When completing significant tasks (adding features, fixing bugs, adding new schools, changing data schema, etc.), update this `CLAUDE.md` file and `README.md` if necessary to keep documentation current.

## Overview

A Next.js website to visualize and compare Common Data Set (CDS) metrics across colleges. Currently featuring **Brown University** and **Harvard University**, each with 9 years of historical data (2016-2017 through 2024-2025).

**Live Features:**
- Admissions trends (applications, acceptance rates, yield, early decision)
- SAT/ACT score trends with middle 50% ranges
- Cost of attendance breakdown over time
- Financial aid statistics
- Student demographics and enrollment trends

---

## Tech Stack

- **Framework:** Next.js 16.1.4 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **Charts:** Recharts
- **Data Extraction:** Python with pdfplumber
- **Deployment:** Vercel (static export)

### Key Dependencies

```json
{
  "next": "^16.0.0",
  "react": "^19.0.0",
  "recharts": "^2.15.0",
  "tailwindcss": "^4.0.0",
  "@tailwindcss/postcss": "^4.0.0"
}
```

---

## Project Structure

```
college-comparisons/
├── src/
│   ├── app/
│   │   ├── page.tsx                    # Home page (school selector)
│   │   ├── [school]/
│   │   │   ├── page.tsx                # Dynamic school page
│   │   │   └── SchoolPageClient.tsx    # Client component with charts
│   │   ├── compare/
│   │   │   └── page.tsx                # School comparison page
│   │   ├── layout.tsx                  # Root layout (forces light mode)
│   │   ├── globals.css                 # Global styles
│   │   └── icon.svg                    # Favicon
│   ├── components/
│   │   └── charts/
│   │       ├── AdmissionsTrendChart.tsx
│   │       ├── TestScoresTrendChart.tsx
│   │       ├── CostsTrendChart.tsx
│   │       ├── FinancialAidTrendChart.tsx
│   │       └── DemographicsTrendChart.tsx
│   ├── data/
│   │   └── schools/
│   │       ├── brown.json              # Brown University data (9 years)
│   │       └── harvard.json            # Harvard University data (9 years)
│   ├── lib/
│   │   └── types.ts                    # TypeScript interfaces
│   └── utils/
│       └── dataHelpers.ts              # Formatting utilities
├── scripts/
│   └── extract_cds.py                  # PDF data extraction script
├── Brown/                              # Source PDFs (9 years)
├── .venv/                              # Python virtual environment
├── tailwind.config.ts
├── next.config.ts
└── package.json
```

---

## Data Schema

### SchoolData (src/lib/types.ts)

```typescript
interface SchoolData {
  name: string;
  slug: string;
  years: Record<string, YearData>;
}

interface YearData {
  admissions: {
    applied: number;
    admitted: number;
    enrolled: number;
    acceptanceRate: number;  // decimal (0.05 = 5%)
    yield: number;           // decimal
    earlyDecision?: { applied: number; admitted: number };
    earlyAction?: { applied: number; admitted: number };
  };

  testScores: {
    sat?: {
      composite: { p25: number; p50: number; p75: number };
      readingWriting: { p25: number; p50: number; p75: number };
      math: { p25: number; p50: number; p75: number };
      submissionRate: number;
    };
    act?: {
      composite: { p25: number; p50: number; p75: number };
      submissionRate: number;
    };
  };

  demographics: {
    enrollment: {
      total: number;
      undergraduate: number;
      graduate: number;
    };
    byRace: {
      international: number;
      hispanicLatino: number;
      blackAfricanAmerican: number;
      white: number;
      asian: number;
      americanIndianAlaskaNative: number;
      nativeHawaiianPacificIslander: number;
      twoOrMoreRaces: number;
      unknown: number;
    };
    byResidency: {
      inState: number;
      outOfState: number;
      international: number;
    };
  };

  costs: {
    tuition: number;
    fees: number;
    roomAndBoard: number;
    totalCOA: number;
  };

  financialAid: {
    percentReceivingAid: number;    // decimal
    averageAidPackage: number;
    averageNeedBasedGrant: number;
    percentNeedFullyMet: number;    // decimal (1.0 = 100%)
  };
}
```

---

## Chart Components

### 1. AdmissionsTrendChart
- **Location:** `src/components/charts/AdmissionsTrendChart.tsx`
- **Features:**
  - Dual-axis chart: bars for applications, line for acceptance rate
  - Early Decision applications chart (if data exists)
  - Complete data table with all years
- **Y-Axis:** Applications (left), Acceptance Rate % (right, domain 0-15%)

### 2. TestScoresTrendChart
- **Location:** `src/components/charts/TestScoresTrendChart.tsx`
- **Features:**
  - Area chart showing middle 50% SAT range (25th-75th percentile)
  - Line for 50th percentile (median)
  - Dynamic Y-axis that adjusts to data (not starting at 0)
- **Fix Applied:** Changed from stacked bars to AreaChart to properly respect Y-axis domain

### 3. CostsTrendChart
- **Location:** `src/components/charts/CostsTrendChart.tsx`
- **Features:**
  - Stacked bar chart showing tuition, fees, room & board
  - Line showing total COA trend
  - Cost breakdown summary for latest year

### 4. FinancialAidTrendChart
- **Location:** `src/components/charts/FinancialAidTrendChart.tsx`
- **Features:**
  - Average need-based grant over time
  - Percent receiving aid trend
  - Net price calculation

### 5. DemographicsTrendChart
- **Location:** `src/components/charts/DemographicsTrendChart.tsx`
- **Features:**
  - Enrollment over time (undergraduate vs graduate)
  - Demographics over time (% by race/ethnicity) - line chart with 6 demographic groups
  - Summary stats for latest year

---

## Data Extraction

### Python Script: `scripts/extract_cds.py`

**Setup:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pdfplumber
```

**Usage:**
```bash
python scripts/extract_cds.py brown --pdf-dir ./Brown
```

### Extraction Challenges & Solutions

1. **Admissions Data:** Successfully extracted using regex patterns:
   - `Total first-time, first-year (degree-seeking) who applied`
   - Older PDFs use different format: `first-time...men who applied` + `women who applied`

2. **Enrollment Numbers:** PDF table parsing unreliable
   - **Solution:** Manually corrected based on Brown's published enrollment figures
   - Brown has ~6,600-7,900 undergrads, ~2,600-4,000 grad students

3. **Costs:** Table extraction worked for most fields
   - Tuition, fees, room & board extracted successfully
   - Some years needed manual verification

4. **Demographics:** Race/ethnicity numbers extracted from tables
   - International student numbers were too low in raw extraction
   - **Solution:** Corrected to match ~10-12% international rate

5. **Financial Aid:** Regex patterns often failed
   - **Solution:** Added known values (Brown meets 100% of demonstrated need)

### Data Quality Notes

- **Admissions:** Accurately extracted from PDFs
- **Test Scores:** SAT/ACT ranges extracted successfully
- **Enrollment:** Manually corrected to match institutional data
- **Costs:** Extracted from PDFs, verified against published rates
- **Financial Aid:** Supplemented with known institutional policies
- **Demographics:** Corrected international student counts

---

## Styling & Theme

### Forcing Light Mode

The app forces light mode to prevent system dark mode from affecting the UI:

**layout.tsx:**
```tsx
<html lang="en" className="light" style={{ colorScheme: "light" }}>
```

**globals.css:**
```css
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: light only;
  }
}

:root {
  color-scheme: light only;
}

.card {
  background-color: #ffffff !important;
}
```

**tailwind.config.ts:**
```ts
darkMode: "class"  // Only enable with explicit class
```

### School Colors

Defined in `src/lib/types.ts`:
```typescript
export const SCHOOL_COLORS: Record<string, string> = {
  brown: "#4E3629",    // Brown University brown
  harvard: "#A51C30",
  yale: "#00356B",
  // ... more schools
};
```

---

## Available PDF Data

### Brown University (9 years)
- `Brown/Brown CDS_2016-2017_Final.pdf`
- `Brown/CDS_2017-2018.pdf`
- `Brown/CDS_2018_2019_FINAL.pdf`
- `Brown/CDS_2019_2020.pdf`
- `Brown/CDS_2020_2021_Final2_0.pdf`
- `Brown/CDS_2021_2022_0.pdf`
- `Brown/CDS_2022_2023.pdf`
- `Brown/CDS_2023_2024.pdf`
- `Brown/CDS_2024_2025.pdf`

### Harvard University (9 years)
- `Harvard/CDS 2016-2017.pdf`
- `Harvard/CDS 2017-2018.pdf`
- `Harvard/CDS 2018-2019.pdf`
- `Harvard/CDS 2019-2020.pdf`
- `Harvard/CDS 2020-2021.pdf`
- `Harvard/CDS 2021-2022.pdf`
- `Harvard/CDS_2022-2023.pdf`
- `Harvard/CDS_2023-2024.pdf`
- `Harvard/CDS_2024-25.pdf`

### Other Schools (PDFs available, not yet extracted)
- **Cornell:** 8 PDFs (2016-2024)
- **Dartmouth:** 9 PDFs (2016-2025)
- **Stanford:** 9 PDFs (2016-2025)
- **UPenn:** 9 PDFs (2016-2025)
- **Yale:** Multiple PDFs available

---

## Running the Project

### Development
```bash
npm run dev
```
Open http://localhost:3000

### Build
```bash
npm run build
```

### Static Export
The project is configured for static export on Vercel:
```typescript
// next.config.ts
output: process.env.NODE_ENV === "production" ? "export" : undefined
```

---

## Known Issues & Warnings

### Recharts SSR Warnings
```
The width(-1) and height(-1) of chart should be greater than 0
```
- **Cause:** Recharts tries to render on server where DOM doesn't exist
- **Impact:** None - charts render correctly in browser
- **Solution:** Can be suppressed with dynamic imports if needed

### Static Export Requirements
- `generateStaticParams()` required for dynamic routes
- Located in `src/app/[school]/page.tsx`

---

## Future Work / TODO

### Data
- [x] Extract data for Harvard University (9 years)
- [ ] Extract data for other Ivy League schools (Cornell, Dartmouth, Yale, etc.)
- [ ] Extract data for Stanford, MIT, UPenn
- [ ] Improve automated extraction accuracy
- [ ] Add more years of historical data where available

### Features
- [ ] Implement comparison page (`/compare?schools=brown,harvard`)
- [ ] Add school selector dropdown on school pages
- [ ] Add data tables with sortable columns
- [ ] Add graduation/retention rate charts (outcomes data)
- [ ] Add class size and faculty data (academics section)

### UI/UX
- [ ] Mobile responsive improvements
- [ ] Add loading states for charts
- [ ] Add print-friendly view
- [ ] Dark mode toggle (optional)

### Technical
- [ ] Add unit tests for data extraction
- [ ] Set up CI/CD pipeline
- [ ] Add data validation/verification scripts
- [ ] Consider caching for large datasets

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/app/[school]/SchoolPageClient.tsx` | Main school page with all charts |
| `src/lib/types.ts` | TypeScript interfaces and school colors |
| `src/data/schools/brown.json` | Brown University data (9 years) |
| `src/data/schools/harvard.json` | Harvard University data (9 years) |
| `scripts/extract_cds.py` | PDF extraction script |
| `src/app/globals.css` | Global styles, light mode forcing |
| `tailwind.config.ts` | Tailwind configuration |

---

## Commands Reference

```bash
# Development
npm run dev

# Build
npm run build

# Extract Brown data
source .venv/bin/activate
python scripts/extract_cds.py brown --pdf-dir ./Brown

# List available PDFs
find . -name "*.pdf" | head -20
```

---

## Data Summary: Brown University

| Year | Applied | Admitted | Accept% | SAT Range | Total COA |
|------|---------|----------|---------|-----------|-----------|
| 2016-2017 | 32,390 | 3,014 | 9.3% | 1370-1540 | $67,439 |
| 2017-2018 | 32,723 | 2,799 | 8.6% | 1405-1570 | $70,226 |
| 2018-2019 | 35,437 | 2,718 | 7.7% | 1420-1550 | $73,736 |
| 2019-2020 | 38,674 | 2,733 | 7.1% | 1440-1570 | $76,504 |
| 2020-2021 | 36,793 | 2,822 | 7.7% | 1440-1560 | $78,668 |
| 2021-2022 | 46,568 | 2,568 | 5.5% | 1460-1570 | $80,886 |
| 2022-2023 | 50,649 | 2,562 | 5.1% | 1490-1580 | $84,728 |
| 2023-2024 | 51,316 | 2,686 | 5.2% | 1500-1570 | $88,756 |
| 2024-2025 | 48,904 | 2,638 | 5.4% | 1510-1580 | $93,164 |

---

## Data Summary: Harvard University

| Year | Applied | Admitted | Accept% | SAT Range | Total COA |
|------|---------|----------|---------|-----------|-----------|
| 2016-2017 | 39,506 | 2,037 | 5.2% | 1430-1600 | $69,607 |
| 2017-2018 | 39,494 | 2,056 | 5.2% | 1460-1590 | $71,650 |
| 2018-2019 | 42,749 | 1,962 | 4.6% | 1460-1590 | $72,391 |
| 2019-2020 | 43,330 | 1,950 | 4.5% | 1460-1580 | $75,891 |
| 2020-2021 | 40,248 | 1,980 | 4.9% | 1460-1580 | $78,028 |
| 2021-2022 | 57,435 | 1,968 | 3.4% | 1460-1580 | $78,028 |
| 2022-2023 | 61,220 | 1,954 | 3.2% | 1480-1580 | $82,866 |
| 2023-2024 | 56,937 | 1,942 | 3.4% | 1490-1580 | $88,584 |
| 2024-2025 | 54,008 | 1,937 | 3.6% | 1510-1580 | $93,075 |

---

*Last updated: January 2026*
