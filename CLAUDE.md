# College Comparisons - Project Documentation

> **WARNING:** Do NOT attempt to read PDF files directly using the Read tool. The PDF files in this project (e.g., `College-Data/Brown/*.pdf`) are large and will overload the context window. Always use the Python extraction script (`scripts/extract_cds.py`) to extract data from PDFs instead.

> **CRITICAL: NEVER MAKE UP DATA.** All data must be extracted from the actual PDF files. If you cannot extract a specific field after multiple attempts, STOP and tell the user which fields are missing. Do not use placeholder values, estimates, or round numbers. Signs of made-up data include: round numbers (e.g., $50,000 instead of $50,547), flat/identical values across years, or values that don't match PDF content. When in doubt, leave the field empty or ask the user for guidance. But make sure to try your best before giving up. However, if you believe that you have good internal numbers (ie. you know the correct value of something from your training data), then you are free to put it in the website.

> **NOTE:** When completing significant tasks (adding features, fixing bugs, adding new schools, changing data schema, etc.), update this `CLAUDE.md` file and `README.md` if necessary to keep documentation current.

## Overview

A Next.js website to visualize and compare Common Data Set (CDS) metrics across colleges. Currently featuring **Brown University**, **California Institute of Technology (Caltech)**, **Columbia University**, **Cornell University**, **Dartmouth College**, **Harvard University**, **Massachusetts Institute of Technology (MIT)**, **Northwestern University**, **Princeton University**, **Stanford University**, **UCLA**, **University of Pennsylvania (UPenn)**, and **Yale University**, each with 7-9 years of historical data (2016-2017 through 2024-2025).

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
│   │       ├── caltech.json            # Caltech data (9 years)
│   │       ├── columbia.json           # Columbia University data (9 years)
│   │       ├── cornell.json            # Cornell University data (8 years)
│   │       ├── dartmouth.json          # Dartmouth College data (9 years)
│   │       ├── harvard.json            # Harvard University data (9 years)
│   │       ├── mit.json                # MIT data (9 years)
│   │       ├── northwestern.json       # Northwestern University data (9 years)
│   │       ├── princeton.json          # Princeton University data (9 years)
│   │       ├── stanford.json           # Stanford University data (9 years)
│   │       ├── ucla.json               # UCLA data (8 years)
│   │       ├── upenn.json              # UPenn data (9 years)
│   │       └── yale.json               # Yale University data (9 years)
│   ├── lib/
│   │   └── types.ts                    # TypeScript interfaces
│   └── utils/
│       └── dataHelpers.ts              # Formatting utilities
├── scripts/
│   └── extract_cds.py                  # PDF data extraction script
├── College-Data/                       # Source CDS PDFs organized by school
│   ├── Brown/
│   ├── Caltech/
│   ├── Columbia/
│   ├── Cornell/
│   ├── Dartmouth/
│   ├── Harvard/
│   ├── MIT/
│   ├── Northwestern/
│   ├── Princeton/
│   ├── Stanford/
│   ├── UCLA/
│   ├── UPenn/
│   └── Yale/
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
python scripts/extract_cds.py brown --pdf-dir ./College-Data/Brown
```

### Extraction Techniques That Work Well

#### 1. Admissions Data (Section C1)
**Technique:** Search for gendered totals and sum them.
```python
patterns = [
    (r'Total first-time.*?men who applied\s+(\d[\d,]*)', 'men_applied'),
    (r'Total first-time.*?women who applied\s+(\d[\d,]*)', 'women_applied'),
    (r'Total first-time.*?men who were admitted\s+(\d[\d,]*)', 'men_admitted'),
    (r'Total first-time.*?women who were admitted\s+(\d[\d,]*)', 'women_admitted'),
    (r'Total full-time.*?men who enrolled\s+(\d[\d,]*)', 'men_enrolled'),
    (r'Total full-time.*?women who enrolled\s+(\d[\d,]*)', 'women_enrolled'),
]
# Sum men + women for totals
```
**Why it works:** CDS always reports by gender, and this format is consistent across schools/years.

#### 2. Financial Aid (Section H2, rows J and K)
**Technique:** Search for H2 J/K rows with dollar amounts.
```python
# Look for lines with two dollar amounts after H2 j or k
for line in lines:
    if 'H2 j' in line or 'H2 k' in line:
        amounts = re.findall(r'\$?([\d]{2},[\d]{3})', line)
        # First amount is typically avg aid package (J) or avg grant (K)
```
**Why it works:** H2 section has standardized row labels (J = avg package, K = avg need-based grant).

#### 3. Demographics (Section B2)
**Technique:** Search for racial/ethnic category names followed by numbers.
```python
# B2 section lists categories with enrollment numbers
# Format: "Category name    firstYear   totalUndergrad   totalUndergrad"
categories = ['Nonresident', 'Hispanic', 'Black', 'White', 'Asian',
              'American Indian', 'Native Hawaiian', 'Two or more']
```
**Why it works:** B2 has consistent category names across all CDS reports.

#### 4. Costs (Section G1)
**Technique:** Search for labeled cost rows.
```python
tuition = re.search(r'Tuition:\s*\$?([\d,]+)', text)
fees = re.search(r'REQUIRED FEES:\s*\$?([\d,]+)', text)
room_board = re.search(r'Room and Board.*?\$?([\d,]+)', text)
```
**Why it works:** G1 uses consistent labels. Note: Some schools (Yale) have $0 fees as they bundle into tuition.

#### 5. SAT/ACT Scores (Section C9)
**Technique:** Search for score labels with 3-4 digit numbers.
```python
sat_composite = re.search(r'SAT Composite\s+(\d{4})\s+(\d{4})', text)  # 25th, 75th
sat_math = re.search(r'SAT Math\s+(\d{3})\s+(\d{3})', text)
act_composite = re.search(r'ACT Composite\s+(\d{2})\s+(\d{2})', text)
```

#### 6. Residency / byResidency (Section F1)
**Technique:** Search for "out of state" percentage, then calculate from totals.
```python
# F1 shows "Percent who are from out of state (exclude international)"
# Format varies: "58% 58%" or "58.00 58.00" (without % sign)
match = re.search(r'out of state.*?(\d+(?:\.\d+)?)\s*%?\s+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
out_pct = float(match.group(2))  # Second number is undergrad percentage

# Calculate actual numbers:
# - International comes from B2 "Nonresident aliens"
# - "Out of state" excludes international students
domestic = total_undergrad - international
out_of_state = int(domestic * out_pct / 100)
in_state = domestic - out_of_state
```
**Why it works:** F1 reports percentages; combine with B2 international count to calculate raw numbers.
**Note:** Newer PDFs may have encoding issues - search for "outofstate" (no spaces) as fallback.

### Common Extraction Issues

1. **Encoding problems in newer PDFs:** Some PDFs use `(cid:XX)` encoding. Try older PDFs first as they often have cleaner text.

2. **Multi-line values:** Costs and other fields sometimes span multiple lines. Search across line boundaries:
   ```python
   text = full_text.replace('\n', ' ')  # Join lines before searching
   ```

3. **Format variations:** Old format uses "freshman", new format uses "first-year". Handle both:
   ```python
   pattern = r'Total first-time.*?(?:freshman|first-year).*?applied'
   ```

4. **Missing data:** If a field consistently fails to extract, check if:
   - The school reports it differently (e.g., Yale has no separate fees)
   - The PDF format changed (compare old vs new PDFs)
   - The data genuinely doesn't exist for that year

### Data Quality Verification

After extraction, verify data quality by checking:
- **No round numbers:** Real data like `$53,071` not `$53,000`
- **Year-over-year variation:** Demographics and costs should change each year
- **Reasonable ranges:** Acceptance rates, SAT scores, costs should be in expected ranges
- **Internal consistency:** Sum of demographic categories ≈ total enrollment

### Advanced Extraction Patterns (Learned from Dartmouth)

#### 7. Newer CDS Format (2023-2024+)
Starting around 2023-2024, some schools use a different format for admissions:
```python
# Old format: "Total first-time...men who applied 11,384"
# New format: "students who applied in Fall 2023 13,516.0 15,325.0"
#             (Men and Women on same line after "Fall YYYY")

newer_patterns = [
    (r'students who applied.*?Fall \d{4}\s+(\d{1,2},\d{3}(?:\.\d)?)\s+(\d{1,2},\d{3}(?:\.\d)?)', 'applied'),
    (r'students admitted.*?Fall \d{4}\s+(\d{1,3}(?:\.\d)?)\s+(\d{1,3}(?:\.\d)?)', 'admitted'),
    (r'students enrolled in Fall \d{4}\s+(\d{1,3}(?:\.\d)?)\s+(\d{1,3}(?:\.\d)?)', 'enrolled'),
]
# Sum both numbers to get total
```

#### 8. Room and Board Variations
Terminology varies between schools and years:
```python
# Patterns to try (in order of preference):
rb_patterns = [
    r'Food and housing \(on-campus\):\s*\$?([\d,]+)',  # Newer format
    r'ROOM AND BOARD[:\s]*\(on-campus\)\s*\$?([\d,]+)',  # With (on-campus)
    r'Room and [Bb]oard[:\s]*\$?([\d,]+)',  # Standard format
]

# Fallback for multi-line format (older PDFs):
# Line 1: "G1 ROOM AND BOARD:"
# Line 2: "(on-campus) $15,756"
if data["roomAndBoard"] == 0:
    for i, line in enumerate(lines):
        if 'ROOM AND BOARD' in line.upper() and i + 1 < len(lines):
            match = re.search(r'\$?([\d,]+)', lines[i + 1])
            if match:
                data["roomAndBoard"] = extract_number(match.group(1))
```

#### 9. Pattern Priority and Guards
**Critical:** Later patterns can overwrite earlier successful matches. Always guard fallback patterns:
```python
# WRONG - this always runs and may overwrite good data:
for i, line in enumerate(lines):
    if 'total first-time' in line.lower():
        data['applied'] = max(large_nums)  # Overwrites!

# CORRECT - only use fallback if primary extraction failed:
if data['applied'] == 0:
    for i, line in enumerate(lines):
        if 'total first-time' in line.lower():
            data['applied'] = max(large_nums)
```

#### 10. pdfplumber Table Parsing Issues
Sometimes pdfplumber splits tables incorrectly, separating headers from data:
```python
# Table 0: ['13,516.0', '15,325.0', '']  # Data only
# Table 1: ['919.0', '878.0', '']        # Data only
# Table 5: ['Total first-time...who applied', '416', ...]  # Headers with different data

# Solution: Use text extraction as primary method when table parsing is unreliable
text = page.extract_text()
# Then use regex on text
```

#### 11. Test-Optional Era (2020+)
Many schools went test-optional during COVID and have remained so. SAT/ACT scores may be:
- Missing entirely from the PDF
- Present but with 0% submission rates
- Only reported for the subset who submitted

**Don't assume missing SAT data is an extraction error** - verify against the school's testing policy.

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
  columbia: "#1D4F91", // Columbia University blue
  harvard: "#A51C30",
  yale: "#00356B",
  // ... more schools
};
```

---

## Adding a New School

When adding a new school to the website, update the following files:

### Required Files to Update:
1. **Create data file:** `src/data/schools/<school>.json` - Extract data using a custom script
2. **Add school color:** `src/lib/types.ts` - Add entry to `SCHOOL_COLORS`
3. **Home page:** `src/app/page.tsx` - Add import and add to `schools` array
4. **School page:** `src/app/[school]/page.tsx` - Add import and add to `schoolDataMap`
5. **How it works:** `src/app/how-it-works/page.tsx` - Change university count
6. **Data helpers:** `src/utils/dataHelpers.ts` - Add to `getAvailableSchools()` array
7. **Documentation:** `CLAUDE.md` - Update overview, project structure, Available PDF Data section, and Key Files Reference

### Checklist:
- [ ] Create extraction script in `scripts/extract_<school>.py`
- [ ] Run extraction and verify data quality
- [ ] Add school color (find official brand color)
- [ ] Update all 4 page/component files listed above
- [ ] Run `npm run build` to verify no errors
- [ ] Update `CLAUDE.md` documentation

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
- Extract data for more Colleges

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
| `src/data/schools/caltech.json` | Caltech data (9 years) |
| `src/data/schools/columbia.json` | Columbia University data (9 years) |
| `src/data/schools/cornell.json` | Cornell University data (8 years) |
| `src/data/schools/dartmouth.json` | Dartmouth College data (9 years) |
| `src/data/schools/harvard.json` | Harvard University data (9 years) |
| `src/data/schools/mit.json` | MIT data (9 years) |
| `src/data/schools/northwestern.json` | Northwestern University data (9 years) |
| `src/data/schools/princeton.json` | Princeton University data (9 years) |
| `src/data/schools/stanford.json` | Stanford University data (9 years) |
| `src/data/schools/ucla.json` | UCLA data (8 years) |
| `src/data/schools/upenn.json` | UPenn data (9 years) |
| `src/data/schools/yale.json` | Yale University data (9 years) |
| `scripts/extract_cds.py` | PDF extraction script |
| `scripts/extract_cornell.py` | Cornell-specific extraction script |
| `scripts/extract_northwestern.py` | Northwestern-specific extraction script |
| `scripts/extract_ucla.py` | UCLA-specific extraction script |
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
python scripts/extract_cds.py brown --pdf-dir ./College-Data/Brown

# List available PDFs
find . -name "*.pdf" | head -20
```

---
