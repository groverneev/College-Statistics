# College Comparisons - Project Documentation

> **WORKTREE:** Always work directly in the main repository (`/Users/neevgrover/Documents/Programming/College-Statistics`). Do NOT create git worktrees. Do not use `git worktree add`. Make all edits in place on the current branch.

> **WARNING:** Do NOT attempt to read PDF files directly using the Read tool. The PDF files in this project (e.g., `College-Data/Brown/*.pdf`) are large and will overload the context window. Always use the Python extraction script (`scripts/extract_cds.py`) to extract data from PDFs instead.

> **Data:** You should be able to extract the data from the CDS pdfs. However, if data is missing or you are having extraction problems, you can either insert the actual numbers from your own knowledge if you have the correct numbers from your training data, or you can search up any missing info if needed. If pdf files for certain years are missing, you can use search to get the correct numbers. The most important thing is that you can't make up any data. The best strategy might be to use a research agent to get the most accurate numbers without errors. If there are any discrepencies between data, you must figure out the issue.

> **NOTE:** When completing significant tasks (adding features, fixing bugs, adding new schools, changing data schema, etc.), update this `CLAUDE.md` file and `README.md` if necessary to keep documentation current.

> **Excel Workbooks:** Vanderbilt uses CDS Excel files rather than PDFs. Use `scripts/extract_vanderbilt_excel.py` for Vanderbilt instead of the PDF extractor.

## Overview

A Next.js website to visualize and compare Common Data Set (CDS) metrics across colleges. The repo includes many schools with multi-year historical data, generally covering the late 2010s through the mid-2020s. Some schools use custom extraction scripts or mixed PDF/web/Excel source pipelines, so always inspect the existing script and JSON for the school you are modifying before making changes.

```md
**Live Features:**
- Admissions trends
- SAT/ACT score trends
- Cost of attendance
- Financial aid
- Student demographics
- Trends stories (`/trends`)

---

## Tech Stack

- **Framework:** Next.js 16.1.4 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **Charts:** Recharts
- **Data Extraction:** Python with pdfplumber, openpyxl, and xlrd
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

Each school typically has:
- source files in `College-Data/<School>/`
- an extraction script in `scripts/` (generic or school-specific)
- an output dataset in `src/data/schools/<slug>.json`

Before editing school data, check whether the school already uses a dedicated extractor or any web-backed/manual overrides.

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

### Python Scripts

#### PDF extractor: `scripts/extract_cds.py`

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

#### Vanderbilt Excel extractor: `scripts/extract_vanderbilt_excel.py`

**Setup:**
```bash
pip install openpyxl xlrd
```

**Usage:**
```bash
python scripts/extract_vanderbilt_excel.py
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

### Fast Data Retrieval Strategy (Works Well in Practice)

Use this when you need accurate numbers quickly, especially to fix one section (like demographics) without re-extracting everything.

1. **Start from official institutional CDS pages only**
   - Prefer the school's CDS archive/index page (e.g., `.../CDS/index.html`) and year-specific PDFs from the same domain.
   - Avoid tertiary summary sites for raw counts.

2. **Extract only the blocking fields first**
   - For demographic fixes, focus on:
     - `B2` for `byRace` and undergraduate totals
     - `F1` for out-of-state % (to compute `inState` / `outOfState`)
   - This is much faster than full-schema extraction when only one chart is wrong.

3. **Use deterministic math for derived fields**
   - Residency:
     - `domestic = undergraduate - international`
     - `outOfState = round(domestic * outPct / 100)`
     - `inState = domestic - outOfState`
   - Keep one rounding rule for all years in the same school.

4. **Patch all affected years in one pass**
   - Update all years for that school (`2016-2017` through latest) in one edit to prevent mixed-quality time series.

5. **Run strict consistency checks immediately after patching**
   - For each year:
     - `undergraduate + graduate == total`
     - `sum(byRace) == undergraduate`
     - `sum(byResidency) == undergraduate`
   - If any check fails, fix before touching any other dataset.

6. **Watch for obvious anomaly signals**
   - Large one-year jumps in a category with no matching enrollment shift
   - Flat/linear-looking fabricated patterns
   - Residencies that imply impossible domestic/international splits

This workflow optimized for both speed and correctness when repairing existing school JSON files.

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
3. **Home page:** `src/app/page.tsx` - Add import AND add to `schools` array (both steps required)
4. **School page:** `src/app/[school]/page.tsx` - Add import AND add to `schoolDataMap` (both steps required)
5. **How it works:** `src/app/how-it-works/page.tsx` - Change university count number
6. **Data helpers:** `src/utils/dataHelpers.ts` - Add to `getAvailableSchools()` array
7. **Documentation:** `CLAUDE.md` and `README.md` - Update only if the workflow or user-facing behavior changed

> **ORDERING:** The `schools` array in `src/app/page.tsx` must always be kept in **alphabetical order by school name**. When adding a new school, insert it in the correct alphabetical position, not at the end.

> **CRITICAL:** For `page.tsx` and `[school]/page.tsx`, you must make TWO edits each:
> - Add the `import <school>Data from "@/data/schools/<school>.json"` line with the other imports
> - Add `<school>Data as SchoolData` to the `schools` array (in `page.tsx`) or `schoolDataMap` (in `[school]/page.tsx`)
> After editing, always read the file back to confirm both the import and array entry are present before moving on.

### Checklist:
- [ ] Create `src/data/schools/<school>.json` with complete data
- [ ] Add school color to `src/lib/types.ts` `SCHOOL_COLORS`
- [ ] `src/app/page.tsx`: add import line + add to `schools` array — **verify both are present**
- [ ] `src/app/[school]/page.tsx`: add import line + add to `schoolDataMap` — **verify both are present**
- [ ] `src/app/how-it-works/page.tsx`: increment university count
- [ ] `src/utils/dataHelpers.ts`: add to `getAvailableSchools()` array
- [ ] `src/components/SearchBar.tsx`: add entry to `SCHOOL_ALIASES` with the school's slug as the key and an array of common aliases/abbreviations (e.g. `["MIT", "Massachusetts Institute of Technology"]`)
- [ ] `CLAUDE.md`/`README.md`: update only if the documented workflow or behavior changed
- [ ] Run `npm run build` to verify the school appears on the home page

---

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
- **Impact:** None; Ignore the warning

### Static Export Requirements
- `generateStaticParams()` required for dynamic routes
- Located in `src/app/[school]/page.tsx`

---

## Adding a Trends Story

The `/trends` page is a scalable, static "blog" for data-driven analyses. Each story lives at `/trends/<slug>`.

### To add a new story:

1. **Register it** in `src/data/trends/index.ts` — add one entry to the `trends` array:
   ```ts
   {
     slug: "my-new-story",
     title: "...",
     subtitle: "...",
     date: "2026-03-15",   // ISO date
     tags: ["Tag1", "Tag2"],
     preview: "1-2 sentence summary shown on the index card.",
   }
   ```

2. **Add data** in `src/data/trends/my-new-story/data.ts` — typed arrays for each chart, plus any narrative strings.

3. **Build the story component** at `src/components/trends/stories/MyNewStory.tsx` — a `"use client"` component using Recharts, matching existing story patterns.

4. **Wire the route** in `src/app/trends/[slug]/page.tsx` — add a `slug === "my-new-story"` branch that renders your story component.

No other files need to change. `generateStaticParams()` auto-picks up the new slug.

---

## Commands Reference

```bash
# Development
npm run dev

# Build
npm run build

# List available PDFs
find . -name "*.pdf" | head -20
```

---
