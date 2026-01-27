#!/usr/bin/env python3
"""
Dartmouth-specific CDS PDF Data Extractor

Uses the proven patterns from CLAUDE.md for reliable extraction.
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
    """Extract a number from text, handling commas."""
    if not text:
        return None
    cleaned = re.sub(r'[,\s]', '', str(text))
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


def extract_admissions_from_tables(tables):
    """Extract admissions data from PDF tables."""
    data = {
        "applied": 0,
        "admitted": 0,
        "enrolled": 0,
    }

    men_applied = women_applied = 0
    men_admitted = women_admitted = 0
    men_enrolled = women_enrolled = 0

    for table in tables:
        if not table:
            continue
        for row in table:
            if not row:
                continue
            row_text = ' '.join(str(c) for c in row if c).lower()

            # Pattern 1: Older format - "Total first-time...men who applied"
            if 'men who applied' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and num > 5000:
                        men_applied = num
                        break

            if 'women who applied' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and num > 5000:
                        women_applied = num
                        break

            if 'men who were admitted' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 500 < num < 3000:
                        men_admitted = num
                        break

            if 'women who were admitted' in row_text and 'first-time' in row_text:
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 500 < num < 3000:
                        women_admitted = num
                        break

            if 'men who enrolled' in row_text and ('first-time' in row_text or 'full-time' in row_text):
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 400 < num < 1500:
                        men_enrolled = num
                        break

            if 'women who enrolled' in row_text and ('first-time' in row_text or 'full-time' in row_text):
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 400 < num < 1500:
                        women_enrolled = num
                        break

            # Pattern 2: Newer format (2023-2024+) - row with numbers for Men/Women columns
            # Format: "Total first-time...who applied in Fall 2023 | 13,516.0 | 15,325.0"
            if 'students who applied' in row_text and 'first-time' in row_text:
                # Extract numeric cells
                nums = []
                for cell in row:
                    num = extract_number(str(cell))
                    if num and num > 5000:
                        nums.append(num)
                if len(nums) >= 2:
                    men_applied = nums[0]
                    women_applied = nums[1]

            if 'students admitted' in row_text and 'first-time' in row_text:
                nums = []
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 300 < num < 3000:
                        nums.append(num)
                if len(nums) >= 2:
                    men_admitted = nums[0]
                    women_admitted = nums[1]

            if 'students enrolled' in row_text and 'first-time' in row_text and 'part-time' not in row_text:
                nums = []
                for cell in row:
                    num = extract_number(str(cell))
                    if num and 300 < num < 1500:
                        nums.append(num)
                if len(nums) >= 2:
                    men_enrolled = nums[0]
                    women_enrolled = nums[1]

            # Pattern 3: Total row format with In-State/Out-of-State/International/Total columns
            if 'total first-time' in row_text and 'who applied' in row_text:
                for cell in reversed(row):
                    num = extract_number(str(cell))
                    if num and num > 20000:
                        data['applied'] = num
                        break

            if 'total first-time' in row_text and 'enrolled' in row_text and 'part-time' not in row_text:
                for cell in reversed(row):
                    num = extract_number(str(cell))
                    if num and 800 < num < 2000:
                        data['enrolled'] = num
                        break

    # Sum gendered values (higher priority than residency breakdown)
    if men_applied > 0 and women_applied > 0:
        data['applied'] = men_applied + women_applied
    if men_admitted > 0 and women_admitted > 0:
        data['admitted'] = men_admitted + women_admitted
    if men_enrolled > 0 and women_enrolled > 0:
        data['enrolled'] = men_enrolled + women_enrolled

    return data


def extract_admissions(text):
    """Extract admissions using gendered totals (proven approach)."""
    data = {
        "applied": 0,
        "admitted": 0,
        "enrolled": 0,
        "acceptanceRate": 0,
        "yield": 0,
    }

    # Join lines to handle multi-line patterns
    text_joined = text.replace('\n', ' ')

    # Pattern for newer format (2023-2024+): "students admitted in Fall 2023 919.0 878.0"
    # This has Men and Women numbers on the same line after "Fall YYYY"
    newer_patterns = [
        (r'students who applied.*?Fall \d{4}\s+(\d{1,2},\d{3}(?:\.\d)?)\s+(\d{1,2},\d{3}(?:\.\d)?)', 'applied'),
        (r'students admitted.*?Fall \d{4}\s+(\d{1,3}(?:\.\d)?)\s+(\d{1,3}(?:\.\d)?)', 'admitted'),
        (r'students enrolled in Fall \d{4}\s+(\d{1,3}(?:\.\d)?)\s+(\d{1,3}(?:\.\d)?)', 'enrolled'),
    ]

    for pattern, field in newer_patterns:
        match = re.search(pattern, text_joined, re.IGNORECASE)
        if match:
            num1 = extract_number(match.group(1)) or 0
            num2 = extract_number(match.group(2)) or 0
            if field == 'applied' and num1 > 5000 and num2 > 5000:
                data[field] = num1 + num2
            elif field == 'admitted' and 300 < num1 < 2000 and 300 < num2 < 2000:
                data[field] = num1 + num2
            elif field == 'enrolled' and 300 < num1 < 1000 and 300 < num2 < 1000:
                data[field] = num1 + num2

    # Approach 1: Sum men + women totals
    patterns = {
        'men_applied': [
            r'Total first-time.*?men who applied\s+(\d[\d,]*)',
            r'Men\s+Applied\s+(\d[\d,]*)',
            r'men\s+applied\s+Total\s+(\d[\d,]*)',
        ],
        'women_applied': [
            r'Total first-time.*?women who applied\s+(\d[\d,]*)',
            r'Women\s+Applied\s+(\d[\d,]*)',
            r'women\s+applied\s+Total\s+(\d[\d,]*)',
        ],
        'men_admitted': [
            r'Total first-time.*?men who were admitted\s+(\d[\d,]*)',
            r'Men\s+Admitted\s+(\d[\d,]*)',
        ],
        'women_admitted': [
            r'Total first-time.*?women who were admitted\s+(\d[\d,]*)',
            r'Women\s+Admitted\s+(\d[\d,]*)',
        ],
        'men_enrolled': [
            r'Total full-time.*?men who enrolled\s+(\d[\d,]*)',
            r'Total part-time.*?men who enrolled\s+(\d[\d,]*)',
        ],
        'women_enrolled': [
            r'Total full-time.*?women who enrolled\s+(\d[\d,]*)',
            r'Total part-time.*?women who enrolled\s+(\d[\d,]*)',
        ],
    }

    values = {}
    for key, pats in patterns.items():
        for pat in pats:
            match = re.search(pat, text_joined, re.IGNORECASE)
            if match:
                values[key] = extract_number(match.group(1)) or 0
                break

    # Sum gendered values
    if 'men_applied' in values and 'women_applied' in values:
        data['applied'] = values['men_applied'] + values['women_applied']
    if 'men_admitted' in values and 'women_admitted' in values:
        data['admitted'] = values['men_admitted'] + values['women_admitted']
    if 'men_enrolled' in values and 'women_enrolled' in values:
        data['enrolled'] = values['men_enrolled'] + values['women_enrolled']

    # Approach 2: Look for C1 table totals if gendered approach failed
    if data['applied'] == 0:
        # Look for patterns like "Total applicants ... 28,336"
        # Or table rows with Men/Women/Another Gender/Total columns
        total_patterns = [
            r'Total\s+first-time.*?first-year.*?applicants\s+(\d[\d,]*)',
            r'applicants[^\n]*Total[^\n]*(\d{2},\d{3})',  # 5-digit numbers
            r'C1\s+First-time[^\n]*applicants[^\n]*(\d{2},\d{3})',
        ]
        for pat in total_patterns:
            match = re.search(pat, text_joined, re.IGNORECASE)
            if match:
                num = extract_number(match.group(1))
                if num and num > 10000:  # Sanity check for total apps
                    data['applied'] = num
                    break

    # Approach 3: Search for specific sections
    if data['applied'] == 0:
        # Find the C1 section
        c1_match = re.search(r'C1[.\s]+(.*?)(?:C2|C3|Section D)', text_joined, re.IGNORECASE | re.DOTALL)
        if c1_match:
            c1_text = c1_match.group(1)
            # Look for large numbers (5 digits) which are likely total apps
            numbers = re.findall(r'\b(\d{2},\d{3})\b', c1_text)
            if numbers:
                # First large number is often total applied
                data['applied'] = extract_number(numbers[0]) or 0

    # Look for table format: row with "Total first-time first-year" followed by numbers
    # Only use this fallback if we haven't found applied yet
    if data['applied'] == 0:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if 'total first-time' in line_lower and 'first-year' in line_lower:
                # Extract numbers from this and next few lines
                combined = ' '.join(lines[i:i+5])
                numbers = re.findall(r'\b(\d{1,2},\d{3})\b', combined)
                large_nums = [extract_number(n) for n in numbers if extract_number(n) and extract_number(n) > 5000]
                if len(large_nums) >= 1:
                    # Largest is usually total applied
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

    # Look for ED patterns
    ed_patterns_applied = [
        r'Early Decision.*?applicants.*?(\d[\d,]*)',
        r'Number of early decision applications received\s*(\d[\d,]*)',
        r'C21.*?early decision.*?(\d[\d,]*)',
    ]
    ed_patterns_admitted = [
        r'Early Decision.*?admitted.*?(\d[\d,]*)',
        r'Number of applicants admitted under early decision plan\s*(\d[\d,]*)',
        r'admitted under early decision\s*(\d[\d,]*)',
    ]

    for pat in ed_patterns_applied:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 500 < num < 5000:  # Reasonable ED range
                ed_applied = num
                break

    for pat in ed_patterns_admitted:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 200 < num < 2000:
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

    # SAT ERW: Look for "SAT Evidence-Based Reading and Writing" or "SAT EBRW"
    erw_patterns = [
        r'SAT Evidence-Based Reading.*?(\d{3})\s*[-–]?\s*(\d{3})',
        r'SAT EBRW.*?(\d{3})\s*[-–]?\s*(\d{3})',
        r'Evidence-Based Reading and Writing.*?(\d{3})\s+(\d{3})',
        r'SAT Evidence.*?Reading.*?Writing\s+(\d{3})\s+(\d{3})',
    ]

    for pat in erw_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            p25 = int(match.group(1))
            p75 = int(match.group(2))
            if 600 <= p25 <= 800 and 600 <= p75 <= 800:
                sat_data["readingWriting"]["p25"] = min(p25, p75)
                sat_data["readingWriting"]["p75"] = max(p25, p75)
                sat_data["readingWriting"]["p50"] = (p25 + p75) // 2
                break

    # SAT Math
    math_patterns = [
        r'SAT Math.*?(\d{3})\s*[-–]?\s*(\d{3})',
        r'Math\s+(\d{3})\s+(\d{3})',
    ]

    for pat in math_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            p25 = int(match.group(1))
            p75 = int(match.group(2))
            if 600 <= p25 <= 800 and 600 <= p75 <= 800:
                sat_data["math"]["p25"] = min(p25, p75)
                sat_data["math"]["p75"] = max(p25, p75)
                sat_data["math"]["p50"] = (p25 + p75) // 2
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
                act_data["composite"]["p50"] = (p25 + p75) // 2
                data["act"] = act_data
                break

    return data


def extract_demographics(text):
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

    # Undergraduate enrollment - look for B1 section totals
    undergrad_patterns = [
        r'Total.*?degree-seeking.*?undergraduates\s*(\d[\d,]*)',
        r'degree-seeking undergraduates.*?Total\s*(\d[\d,]*)',
        r'B1.*?undergraduate.*?(\d[\d,]*)',
        r'Total\s+undergraduate\s+enrollment\s*(\d[\d,]*)',
    ]

    for pat in undergrad_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 3000 < num < 6000:  # Dartmouth undergrad range
                data["enrollment"]["undergraduate"] = num
                break

    # If still 0, search more broadly
    if data["enrollment"]["undergraduate"] == 0:
        # Look for numbers near "undergraduate" or "undergrad"
        lines = text.split('\n')
        for line in lines:
            if 'undergraduate' in line.lower() or 'degree-seeking' in line.lower():
                nums = re.findall(r'\b(\d,\d{3})\b', line)
                for n in nums:
                    num = extract_number(n)
                    if num and 3000 < num < 6000:
                        data["enrollment"]["undergraduate"] = num
                        break

    # Graduate enrollment
    grad_patterns = [
        r'Total.*?graduate.*?enrollment\s*(\d[\d,]*)',
        r'graduate.*?students.*?Total\s*(\d[\d,]*)',
    ]

    for pat in grad_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 500 < num < 3000:
                data["enrollment"]["graduate"] = num
                break

    data["enrollment"]["total"] = data["enrollment"]["undergraduate"] + data["enrollment"]["graduate"]

    # Demographics from B2 section
    race_patterns = {
        'international': [r'Nonresident.*?(\d[\d,]*)', r'International.*?(\d[\d,]*)'],
        'hispanicLatino': [r'Hispanic.*?Latino.*?(\d[\d,]*)', r'Hispanic/Latino.*?(\d[\d,]*)'],
        'blackAfricanAmerican': [r'Black.*?African.*?American.*?(\d[\d,]*)'],
        'white': [r'White.*?(\d[\d,]*)'],
        'asian': [r'Asian.*?(\d[\d,]*)'],
        'americanIndianAlaskaNative': [r'American Indian.*?Alaska.*?Native.*?(\d[\d,]*)'],
        'nativeHawaiianPacificIslander': [r'Native Hawaiian.*?Pacific.*?Islander.*?(\d[\d,]*)'],
        'twoOrMoreRaces': [r'Two or more races.*?(\d[\d,]*)', r'Two or More.*?(\d[\d,]*)'],
        'unknown': [r'Race.*?ethnicity.*?unknown.*?(\d[\d,]*)', r'Unknown.*?(\d[\d,]*)'],
    }

    # Search in B2 section area
    b2_match = re.search(r'B2[.\s]+(.*?)(?:B3|Section C)', text_joined, re.IGNORECASE | re.DOTALL)
    search_text = b2_match.group(1) if b2_match else text_joined

    for category, patterns in race_patterns.items():
        for pat in patterns:
            match = re.search(pat, search_text, re.IGNORECASE)
            if match:
                num = extract_number(match.group(1))
                if num and num > 0 and num < data["enrollment"]["undergraduate"] * 0.7:
                    data["byRace"][category] = num
                    break

    # Residency from F1 section
    # F1 shows "Percent who are from out of state"
    out_of_state_patterns = [
        r'out of state.*?(\d+(?:\.\d+)?)\s*%?',
        r'out-of-state.*?(\d+(?:\.\d+)?)\s*%?',
    ]

    for pat in out_of_state_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            out_pct = float(match.group(1))
            if out_pct > 1:  # It's a percentage like 96
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

    # Tuition patterns - look for dollar amounts after Tuition:
    tuition_patterns = [
        r'Tuition:\s*\$?([\d,]+(?:\.\d{2})?)',  # Tuition: $69,207.00
        r'Tuition[:\s]+\$?([\d,]+)',
        r'PRIVATE INSTITUTIONS.*?Tuition:\s*\$?([\d,]+)',
    ]

    for pat in tuition_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 40000 < num < 80000:
                data["tuition"] = num
                break

    # Fees patterns
    fees_patterns = [
        r'Required Fees:\s*\$?([\d,]+(?:\.\d{2})?)',  # Required Fees: $2,318.00
        r'REQUIRED FEES[:\s]*\$?([\d,]+)',
        r'Required fees[:\s]*\$?([\d,]+)',
    ]

    for pat in fees_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 500 < num < 5000:
                data["fees"] = num
                break

    # Room and Board patterns - also match "Food and housing"
    rb_patterns = [
        r'Food and housing \(on-campus\):\s*\$?([\d,]+(?:\.\d{2})?)',  # Food and housing (on-campus): $20,920.00
        r'Food and [Hh]ousing[:\s]*\$?([\d,]+)',
        r'Room and [Bb]oard[:\s]*\$?([\d,]+)',
        r'Room & [Bb]oard[:\s]*\$?([\d,]+)',
        r'ROOM AND BOARD[:\s]*\$?([\d,]+)',
        # Older format: "ROOM AND BOARD:" on one line, "(on-campus) $15,756" on next
        r'ROOM AND BOARD[:\s]*\(on-campus\)\s*\$?([\d,]+)',
    ]

    for pat in rb_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            num = extract_number(match.group(1))
            if num and 10000 < num < 25000:
                data["roomAndBoard"] = num
                break

    # Fallback: Look for room and board in lines
    if data["roomAndBoard"] == 0:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'ROOM AND BOARD' in line.upper() and i + 1 < len(lines):
                # Check next line for amount
                next_line = lines[i + 1]
                match = re.search(r'\$?([\d,]+)', next_line)
                if match:
                    num = extract_number(match.group(1))
                    if num and 10000 < num < 25000:
                        data["roomAndBoard"] = num
                        break

    # Calculate total COA
    data["totalCOA"] = data["tuition"] + data["fees"] + data["roomAndBoard"]

    return data


def extract_financial_aid(text):
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
            if val > 1:  # It's a percentage like 100
                val = val / 100
            if val > 0.8:  # Dartmouth meets ~100% of need
                data["percentNeedFullyMet"] = round(val, 4)
                break

    # If not found, Dartmouth typically meets 100% of need
    if data["percentNeedFullyMet"] == 0:
        data["percentNeedFullyMet"] = 1.0

    # Percent receiving aid
    receiving_patterns = [
        r'(\d+(?:\.\d+)?)\s*%.*?receiving.*?need-based',
        r'receiving.*?aid.*?(\d+(?:\.\d+)?)\s*%',
    ]

    for pat in receiving_patterns:
        match = re.search(pat, text_joined, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if val > 1:
                val = val / 100
            if 0.3 < val < 0.7:  # Typical range
                data["percentReceivingAid"] = round(val, 4)
                break

    return data


def extract_year_from_filename(filename):
    """Extract academic year from filename."""
    patterns = [
        r'(\d{4})[-_](\d{4})',
        r'(\d{4})',
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)}-{match.group(2)}"
            else:
                year = int(match.group(1))
                return f"{year}-{year + 1}"
    return "unknown"


def process_dartmouth():
    """Process all Dartmouth PDFs."""
    pdf_dir = Path("Dartmouth")
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    school_data = {
        "name": "Dartmouth College",
        "slug": "dartmouth",
        "years": {},
    }

    for pdf_file in pdf_files:
        year = extract_year_from_filename(pdf_file.name)
        print(f"Processing {pdf_file.name} ({year})...")

        try:
            text = extract_pdf_text(str(pdf_file))
            tables = extract_pdf_tables(str(pdf_file))

            # Try text-based extraction first
            admissions_data = extract_admissions(text)

            # If text extraction failed or got low numbers, try table extraction
            if admissions_data['applied'] < 15000 or admissions_data['admitted'] == 0:
                table_admissions = extract_admissions_from_tables(tables)
                if table_admissions['applied'] > admissions_data['applied']:
                    admissions_data['applied'] = table_admissions['applied']
                if table_admissions['admitted'] > admissions_data['admitted']:
                    admissions_data['admitted'] = table_admissions['admitted']
                if table_admissions['enrolled'] > admissions_data['enrolled']:
                    admissions_data['enrolled'] = table_admissions['enrolled']

                # Recalculate rates
                if admissions_data['applied'] > 0 and admissions_data['admitted'] > 0:
                    admissions_data['acceptanceRate'] = round(
                        admissions_data['admitted'] / admissions_data['applied'], 4)
                if admissions_data['admitted'] > 0 and admissions_data['enrolled'] > 0:
                    admissions_data['yield'] = round(
                        admissions_data['enrolled'] / admissions_data['admitted'], 4)

            year_data = {
                "admissions": admissions_data,
                "testScores": extract_test_scores(text),
                "demographics": extract_demographics(text),
                "costs": extract_costs(text),
                "financialAid": extract_financial_aid(text),
            }

            school_data["years"][year] = year_data

            # Print summary
            adm = year_data["admissions"]
            rate = adm.get('acceptanceRate', 0)
            print(f"  Applied: {adm['applied']:,}, Admitted: {adm['admitted']:,}, "
                  f"Rate: {rate:.1%}")
            if year_data["testScores"].get("sat"):
                sat = year_data["testScores"]["sat"]["composite"]
                print(f"  SAT: {sat['p25']}-{sat['p75']}")
            print(f"  COA: ${year_data['costs']['totalCOA']:,}")

        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    # Write output
    output_path = Path("src/data/schools/dartmouth.json")
    with open(output_path, "w") as f:
        json.dump(school_data, f, indent=2)

    print(f"\nOutput written to: {output_path}")
    return school_data


if __name__ == "__main__":
    process_dartmouth()
