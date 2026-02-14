#!/usr/bin/env python3
"""
Northwestern-specific CDS PDF Data Extractor

Uses targeted patterns for Northwestern University CDS PDFs.
"""

import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is required. Install with: pip install pdfplumber")
    sys.exit(1)


def extract_number(text):
    """Extract a number from text, handling commas and decimals."""
    if not text:
        return None
    cleaned = re.sub(r'[,\s]', '', str(text))
    # Handle .0 decimals from newer PDFs
    cleaned = re.sub(r'\.0$', '', cleaned)
    match = re.search(r'(\d+)', cleaned)
    return int(match.group(1)) if match else None


def extract_pdf_text(pdf_path):
    """Extract all text from PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        text_parts = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n".join(text_parts)


def extract_pdf_tables(pdf_path):
    """Extract all tables from PDF."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            tables.extend(page_tables)
    return tables


def extract_admissions(text, tables):
    """Extract admissions data from Section C."""
    data = {
        "applied": 0,
        "admitted": 0,
        "enrolled": 0,
        "acceptanceRate": 0,
        "yield": 0,
    }

    text_joined = text.replace('\n', ' ')

    men_applied = women_applied = 0
    men_admitted = women_admitted = 0
    men_enrolled = women_enrolled = 0

    # Pattern 1: Older format - gendered totals in text
    gender_patterns = {
        'men_applied': [
            r'Total first-time.*?men who applied\s+(\d[\d,]*)',
            r'first-time.*?first-year.*?men who applied\s+(\d[\d,]*)',
        ],
        'women_applied': [
            r'Total first-time.*?women who applied\s+(\d[\d,]*)',
            r'first-time.*?first-year.*?women who applied\s+(\d[\d,]*)',
        ],
        'men_admitted': [
            r'Total first-time.*?men who were admitted\s+(\d[\d,]*)',
            r'first-time.*?first-year.*?men who were admitted\s+(\d[\d,]*)',
        ],
        'women_admitted': [
            r'Total first-time.*?women who were admitted\s+(\d[\d,]*)',
            r'first-time.*?first-year.*?women who were admitted\s+(\d[\d,]*)',
        ],
        'men_enrolled': [
            r'Total full-time.*?men who enrolled\s+(\d[\d,]*)',
            r'full-time.*?first-year.*?men who enrolled\s+(\d[\d,]*)',
        ],
        'women_enrolled': [
            r'Total full-time.*?women who enrolled\s+(\d[\d,]*)',
            r'full-time.*?first-year.*?women who enrolled\s+(\d[\d,]*)',
        ],
    }

    values = {}
    for key, pats in gender_patterns.items():
        for pat in pats:
            match = re.search(pat, text_joined, re.IGNORECASE)
            if match:
                values[key] = extract_number(match.group(1)) or 0
                break

    if 'men_applied' in values and 'women_applied' in values:
        men_applied = values['men_applied']
        women_applied = values['women_applied']
    if 'men_admitted' in values and 'women_admitted' in values:
        men_admitted = values['men_admitted']
        women_admitted = values['women_admitted']
    if 'men_enrolled' in values and 'women_enrolled' in values:
        men_enrolled = values['men_enrolled']
        women_enrolled = values['women_enrolled']

    # Pattern 2: Table-based extraction
    for table in tables:
        if not table:
            continue
        for row in table:
            if not row:
                continue
            row_text = ' '.join(str(c) for c in row if c).lower()

            # Look for gendered rows in tables
            if 'men who applied' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and num > 5000:
                        if men_applied == 0:
                            men_applied = num
                        break

            if 'women who applied' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and num > 5000:
                        if women_applied == 0:
                            women_applied = num
                        break

            if 'men who were admitted' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 500 < num < 5000:
                        if men_admitted == 0:
                            men_admitted = num
                        break

            if 'women who were admitted' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 500 < num < 5000:
                        if women_admitted == 0:
                            women_admitted = num
                        break

            if 'men who enrolled' in row_text and ('first-time' in row_text or 'full-time' in row_text):
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 500 < num < 2000:
                        if men_enrolled == 0:
                            men_enrolled = num
                        break

            if 'women who enrolled' in row_text and ('first-time' in row_text or 'full-time' in row_text):
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 500 < num < 2000:
                        if women_enrolled == 0:
                            women_enrolled = num
                        break

            # Pattern 3: Newer format - "students who applied in Fall YYYY"
            if 'students who applied' in row_text and ('first-time' in row_text or 'fall' in row_text):
                nums = []
                for cell in row:
                    num = extract_number(str(cell))
                    if num and num > 5000:
                        nums.append(num)
                if len(nums) >= 2 and men_applied == 0:
                    men_applied = nums[0]
                    women_applied = nums[1]

            if 'students admitted' in row_text and ('first-time' in row_text or 'fall' in row_text):
                nums = []
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 300 < num < 5000:
                        nums.append(num)
                if len(nums) >= 2 and men_admitted == 0:
                    men_admitted = nums[0]
                    women_admitted = nums[1]

            if 'students enrolled' in row_text and 'part-time' not in row_text and ('first-time' in row_text or 'fall' in row_text):
                nums = []
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 300 < num < 2000:
                        nums.append(num)
                if len(nums) >= 2 and men_enrolled == 0:
                    men_enrolled = nums[0]
                    women_enrolled = nums[1]

    # Sum gendered values
    if men_applied > 0 and women_applied > 0:
        data['applied'] = men_applied + women_applied
    if men_admitted > 0 and women_admitted > 0:
        data['admitted'] = men_admitted + women_admitted
    if men_enrolled > 0 and women_enrolled > 0:
        data['enrolled'] = men_enrolled + women_enrolled

    # Fallback: look for total lines if gendered approach failed
    if data['applied'] == 0:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if 'total first-time' in line_lower and ('applied' in line_lower or 'applicant' in line_lower):
                combined = ' '.join(lines[i:i+3])
                numbers = re.findall(r'\b(\d{2},\d{3})\b', combined)
                large_nums = [extract_number(n) for n in numbers if extract_number(n) and extract_number(n) > 20000]
                if large_nums:
                    data['applied'] = max(large_nums)
                    break

    # Calculate rates
    if data['applied'] > 0 and data['admitted'] > 0:
        data['acceptanceRate'] = round(data['admitted'] / data['applied'], 4)
    if data['admitted'] > 0 and data['enrolled'] > 0:
        data['yield'] = round(data['enrolled'] / data['admitted'], 4)

    # Early Decision
    ed_applied = None
    ed_admitted = None

    ed_patterns_applied = [
        r'Number of early decision applications received\s*(\d[\d,]*)',
        r'early decision.*?applications received\s*(\d[\d,]*)',
        r'Early Decision.*?applicants.*?(\d[\d,]*)',
        r'ED.*?applications.*?(\d[\d,]*)',
    ]
    ed_patterns_admitted = [
        r'Number of applicants admitted under early decision plan\s*(\d[\d,]*)',
        r'applicants admitted under early decision\s*(\d[\d,]*)',
        r'Early Decision.*?admitted.*?(\d[\d,]*)',
    ]

    for pat in ed_patterns_applied:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 1000 < num < 8000:
                ed_applied = num
                break

    for pat in ed_patterns_admitted:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 300 < num < 3000:
                ed_admitted = num
                break

    # Also search tables for ED
    if not ed_applied:
        for table in tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(c) for c in row if c).lower()
                if 'early decision' in row_text and 'received' in row_text:
                    for cell in row:
                        num = extract_number(str(cell))
                        if num and 1000 < num < 8000:
                            ed_applied = num
                            break
                if 'admitted under early decision' in row_text:
                    for cell in row:
                        num = extract_number(str(cell))
                        if num and 300 < num < 3000:
                            ed_admitted = num
                            break

    if ed_applied and ed_admitted:
        data['earlyDecision'] = {'applied': ed_applied, 'admitted': ed_admitted}

    return data


def extract_test_scores(text):
    """Extract SAT/ACT scores from Section C9."""
    data = {}
    text_joined = text.replace('\n', ' ')

    sat_data = {
        "composite": {"p25": 0, "p50": 0, "p75": 0},
        "readingWriting": {"p25": 0, "p50": 0, "p75": 0},
        "math": {"p25": 0, "p50": 0, "p75": 0},
        "submissionRate": 0,
    }

    # SAT ERW
    erw_patterns = [
        r'SAT Evidence-Based Reading.*?(\d{3})\s*[-–]?\s*(\d{3})',
        r'SAT EBRW.*?(\d{3})\s*[-–]?\s*(\d{3})',
        r'Evidence-Based Reading and Writing.*?(\d{3})\s+(\d{3})',
    ]

    for pat in erw_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            p25 = int(match.group(1))
            p75 = int(match.group(2))
            if 600 <= p25 <= 800 and 600 <= p75 <= 800:
                sat_data["readingWriting"]["p25"] = min(p25, p75)
                sat_data["readingWriting"]["p75"] = max(p25, p75)
                sat_data["readingWriting"]["p50"] = (min(p25, p75) + max(p25, p75)) // 2
                break

    # SAT Math
    math_patterns = [
        r'SAT Math.*?(\d{3})\s*[-–]?\s*(\d{3})',
    ]

    for pat in math_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            p25 = int(match.group(1))
            p75 = int(match.group(2))
            if 600 <= p25 <= 800 and 600 <= p75 <= 800:
                sat_data["math"]["p25"] = min(p25, p75)
                sat_data["math"]["p75"] = max(p25, p75)
                sat_data["math"]["p50"] = (min(p25, p75) + max(p25, p75)) // 2
                break

    # Calculate composite
    if sat_data["readingWriting"]["p25"] > 0 and sat_data["math"]["p25"] > 0:
        sat_data["composite"]["p25"] = sat_data["readingWriting"]["p25"] + sat_data["math"]["p25"]
        sat_data["composite"]["p75"] = sat_data["readingWriting"]["p75"] + sat_data["math"]["p75"]
        sat_data["composite"]["p50"] = sat_data["readingWriting"]["p50"] + sat_data["math"]["p50"]
        data["sat"] = sat_data

    # ACT Composite
    act_data = {
        "composite": {"p25": 0, "p50": 0, "p75": 0},
        "submissionRate": 0,
    }

    act_patterns = [
        r'ACT Composite.*?(\d{2})\s*[-–]?\s*(\d{2})',
        r'ACT Composite\s+(\d{2})\s+(\d{2})',
    ]

    for pat in act_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            p25 = int(match.group(1))
            p75 = int(match.group(2))
            if 25 <= p25 <= 36 and 25 <= p75 <= 36:
                act_data["composite"]["p25"] = min(p25, p75)
                act_data["composite"]["p75"] = max(p25, p75)
                act_data["composite"]["p50"] = (min(p25, p75) + max(p25, p75)) // 2
                data["act"] = act_data
                break

    return data


def extract_demographics(text, tables):
    """Extract enrollment and demographic data from Section B."""
    data = {
        "enrollment": {"total": 0, "undergraduate": 0, "graduate": 0},
        "byRace": {
            "international": 0,
            "hispanicLatino": 0,
            "blackAfricanAmerican": 0,
            "white": 0,
            "asian": 0,
            "americanIndianAlaskaNative": 0,
            "nativeHawaiianPacificIslander": 0,
            "twoOrMoreRaces": 0,
            "unknown": 0,
        },
        "byResidency": {"inState": 0, "outOfState": 0, "international": 0},
    }

    text_joined = text.replace('\n', ' ')
    lines = text.split('\n')

    # Undergraduate enrollment - Northwestern has ~8000-8700 undergrads
    undergrad_patterns = [
        r'Total.*?degree-seeking.*?undergraduates\s*(\d[\d,]*)',
        r'degree-seeking undergraduates.*?Total\s*(\d[\d,]*)',
        r'Total\s+undergraduate\s+enrollment\s*(\d[\d,]*)',
    ]

    for pat in undergrad_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 7000 < num < 10000:
                data["enrollment"]["undergraduate"] = num
                break

    # Also search tables
    if data["enrollment"]["undergraduate"] == 0:
        for table in tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(c) for c in row if c).lower()
                if ('degree-seeking' in row_text or 'undergraduate' in row_text) and 'total' in row_text:
                    for cell in row:
                        num = extract_number(str(cell))
                        if num and 7000 < num < 10000:
                            data["enrollment"]["undergraduate"] = num
                            break

    # Also try looking for B1 section numbers
    if data["enrollment"]["undergraduate"] == 0:
        for line in lines:
            if 'undergraduate' in line.lower() and 'degree-seeking' in line.lower():
                nums = re.findall(r'\b(\d,\d{3})\b', line)
                for n in nums:
                    num = extract_number(n)
                    if num and 7000 < num < 10000:
                        data["enrollment"]["undergraduate"] = num
                        break

    # Graduate enrollment - Northwestern has ~12000-14000 grad students
    grad_patterns = [
        r'Total.*?graduate.*?enrollment\s*(\d[\d,]*)',
        r'Total.*?graduate.*?professional.*?(\d[\d,]*)',
    ]

    for pat in grad_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 8000 < num < 16000:
                data["enrollment"]["graduate"] = num
                break

    data["enrollment"]["total"] = data["enrollment"]["undergraduate"] + data["enrollment"]["graduate"]

    # Demographics from B2 section - search tables
    race_keywords = {
        'international': ['nonresident', 'international'],
        'hispanicLatino': ['hispanic', 'latino'],
        'blackAfricanAmerican': ['black', 'african american'],
        'white': ['white'],
        'asian': ['asian'],
        'americanIndianAlaskaNative': ['american indian', 'alaska native'],
        'nativeHawaiianPacificIslander': ['native hawaiian', 'pacific islander'],
        'twoOrMoreRaces': ['two or more'],
        'unknown': ['unknown', 'race/ethnicity unknown'],
    }

    for table in tables:
        if not table:
            continue
        for row in table:
            if not row:
                continue
            row_text = ' '.join(str(c) for c in row if c).lower()

            for category, keywords in race_keywords.items():
                for keyword in keywords:
                    if keyword in row_text:
                        # Get numbers from the row
                        nums = []
                        for cell in row:
                            num = extract_number(str(cell))
                            if num and num > 0:
                                nums.append(num)
                        # For undergrad demographics, look for reasonable numbers
                        reasonable = [n for n in nums if 1 <= n <= 5000]
                        if reasonable and data["byRace"][category] == 0:
                            # Take the number that seems like undergrad total
                            # Usually it's the 2nd or 3rd column
                            data["byRace"][category] = max(reasonable)
                        break

    # Residency from F1 section
    out_patterns = [
        r'out of state.*?(\d+(?:\.\d+)?)\s*%',
        r'out-of-state.*?(\d+(?:\.\d+)?)\s*%',
        r'outofstate.*?(\d+(?:\.\d+)?)',
    ]

    for pat in out_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            out_pct = float(match.group(1))
            if out_pct > 1:
                out_pct = out_pct / 100

            undergrad = data["enrollment"]["undergraduate"]
            international = data["byRace"]["international"]

            if undergrad > 0:
                domestic = undergrad - international
                out_of_state = int(domestic * out_pct)
                in_state = domestic - out_of_state

                data["byResidency"]["outOfState"] = out_of_state
                data["byResidency"]["inState"] = in_state
                data["byResidency"]["international"] = international
                break

    return data


def extract_costs(text):
    """Extract cost data from Section G."""
    data = {"tuition": 0, "fees": 0, "roomAndBoard": 0, "totalCOA": 0}

    text_joined = text.replace('\n', ' ')
    lines = text.split('\n')

    # Tuition - Northwestern tuition ranges from ~$50K to $70K
    tuition_patterns = [
        r'Tuition:\s*\$?([\d,]+(?:\.\d{2})?)',
        r'PRIVATE INSTITUTIONS.*?Tuition[:\s]+\$?([\d,]+)',
        r'Tuition[:\s]+\$?([\d,]+)',
    ]

    for pat in tuition_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 45000 < num < 80000:
                data["tuition"] = num
                break

    # Fees
    fees_patterns = [
        r'Required Fees:\s*\$?([\d,]+(?:\.\d{2})?)',
        r'REQUIRED FEES[:\s]*\$?([\d,]+)',
        r'Required fees[:\s]*\$?([\d,]+)',
    ]

    for pat in fees_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 100 < num < 5000:
                data["fees"] = num
                break

    # Room and Board
    rb_patterns = [
        r'Food and housing \(on-campus\):\s*\$?([\d,]+(?:\.\d{2})?)',
        r'Food and [Hh]ousing[:\s]*\$?([\d,]+)',
        r'Room and [Bb]oard.*?\$?([\d,]+)',
        r'ROOM AND BOARD[:\s]*\(on-campus\)\s*\$?([\d,]+)',
        r'ROOM AND BOARD[:\s]*\$?([\d,]+)',
    ]

    for pat in rb_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 13000 < num < 25000:
                data["roomAndBoard"] = num
                break

    # Fallback for multi-line room and board
    if data["roomAndBoard"] == 0:
        for i, line in enumerate(lines):
            if 'ROOM AND BOARD' in line.upper() and i + 1 < len(lines):
                match = re.search(r'\$?([\d,]+)', lines[i + 1])
                if match:
                    num = extract_number(match.group(1))
                    if num and 13000 < num < 25000:
                        data["roomAndBoard"] = num
                        break

    data["totalCOA"] = data["tuition"] + data["fees"] + data["roomAndBoard"]

    return data


def extract_financial_aid(text, tables):
    """Extract financial aid data from Section H."""
    data = {
        "percentReceivingAid": 0,
        "averageAidPackage": 0,
        "averageNeedBasedGrant": 0,
        "percentNeedFullyMet": 0,
    }

    text_joined = text.replace('\n', ' ')

    # Average need-based grant (H2 K)
    grant_patterns = [
        r'H2\s*k.*?\$?([\d,]+)',
        r'average need-based.*?grant.*?\$?([\d,]+)',
        r'Average.*?need-based.*?scholarship.*?grant.*?\$?([\d,]+)',
    ]

    for pat in grant_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 30000 < num < 80000:
                data["averageNeedBasedGrant"] = num
                break

    # Search tables for H2 section
    if data["averageNeedBasedGrant"] == 0:
        for table in tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(c) for c in row if c).lower()
                if ('average' in row_text and 'grant' in row_text and 'need' in row_text) or 'h2' in row_text:
                    for cell in row:
                        num = extract_number(str(cell))
                        if num and 30000 < num < 80000:
                            data["averageNeedBasedGrant"] = num
                            break

    # Average aid package (H2 J)
    aid_patterns = [
        r'H2\s*j.*?\$?([\d,]+)',
        r'average.*?financial aid.*?package.*?\$?([\d,]+)',
    ]

    for pat in aid_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 30000 < num < 80000:
                data["averageAidPackage"] = num
                break

    # Percent need fully met
    fully_met_patterns = [
        r'fully met.*?(\d+(?:\.\d+)?)\s*%',
        r'need fully met.*?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*%.*?fully met',
    ]

    for pat in fully_met_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if val > 1:
                val = val / 100
            if 0.5 < val <= 1.0:
                data["percentNeedFullyMet"] = round(val, 4)
                break

    # Percent receiving aid
    receiving_patterns = [
        r'(\d+(?:\.\d+)?)\s*%.*?receiving.*?need-based',
        r'receiving.*?aid.*?(\d+(?:\.\d+)?)\s*%',
        r'H2\s*a.*?(\d+(?:\.\d+)?)\s*%',
    ]

    for pat in receiving_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if val > 1:
                val = val / 100
            if 0.3 < val < 0.7:
                data["percentReceivingAid"] = round(val, 4)
                break

    return data


def extract_year_from_filename(filename):
    """Extract academic year from filename."""
    patterns = [
        r'(\d{4})[-_](\d{4})',
        r'(\d{4})[-_](\d{2})\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            year1 = match.group(1)
            year2 = match.group(2)
            if len(year2) == 2:
                year2 = year1[:2] + year2
            return f"{year1}-{year2}"
    return "unknown"


def process_northwestern():
    """Process all Northwestern PDFs."""
    pdf_dir = Path("College-Data/Northwestern")
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    school_data = {
        "name": "Northwestern University",
        "slug": "northwestern",
        "years": {},
    }

    for pdf_file in pdf_files:
        year = extract_year_from_filename(pdf_file.name)
        print(f"\nProcessing {pdf_file.name} ({year})...")

        try:
            text = extract_pdf_text(str(pdf_file))
            tables = extract_pdf_tables(str(pdf_file))

            year_data = {
                "admissions": extract_admissions(text, tables),
                "testScores": extract_test_scores(text),
                "demographics": extract_demographics(text, tables),
                "costs": extract_costs(text),
                "financialAid": extract_financial_aid(text, tables),
            }

            school_data["years"][year] = year_data

            # Print summary
            adm = year_data["admissions"]
            rate = adm.get('acceptanceRate', 0)
            print(f"  Applied: {adm['applied']:,}, Admitted: {adm['admitted']:,}, "
                  f"Rate: {rate:.1%}, Enrolled: {adm['enrolled']:,}")
            if adm.get('earlyDecision'):
                ed = adm['earlyDecision']
                print(f"  ED: {ed['applied']:,} applied, {ed['admitted']:,} admitted")
            if year_data["testScores"].get("sat"):
                sat = year_data["testScores"]["sat"]["composite"]
                print(f"  SAT: {sat['p25']}-{sat['p75']}")
            if year_data["testScores"].get("act"):
                act = year_data["testScores"]["act"]["composite"]
                print(f"  ACT: {act['p25']}-{act['p75']}")
            dem = year_data["demographics"]["enrollment"]
            print(f"  Enrollment: {dem['undergraduate']:,} undergrad, {dem['graduate']:,} grad")
            print(f"  COA: ${year_data['costs']['totalCOA']:,}")
            print(f"  Avg Grant: ${year_data['financialAid']['averageNeedBasedGrant']:,}")

        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    # Write output
    output_path = Path("src/data/schools/northwestern.json")
    with open(output_path, "w") as f:
        json.dump(school_data, f, indent=2)

    print(f"\nOutput written to: {output_path}")
    return school_data


if __name__ == "__main__":
    process_northwestern()
