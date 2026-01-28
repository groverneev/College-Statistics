#!/usr/bin/env python3
"""
Cornell CDS PDF Data Extractor

Extracts Common Data Set information from Cornell PDF files.
Handles multiple format variations across different years.
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
    """Extract a number from text, handling commas and spaces in numbers."""
    if not text:
        return 0
    # Remove spaces within numbers (handles "35 ,672" -> "35672")
    cleaned = re.sub(r'(\d)\s+(\d)', r'\1\2', str(text))
    cleaned = re.sub(r'[,\s]', '', cleaned)
    match = re.search(r'(\d+)', cleaned)
    if match:
        return int(match.group(1))
    return 0


def extract_float(text):
    """Extract a float from text."""
    if not text:
        return 0.0
    cleaned = str(text).replace(',', '').replace('%', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_cornell_year(pdf_path, year_label):
    """Extract all data from a single Cornell CDS PDF."""
    print(f"Processing {pdf_path} for year {year_label}")

    pdf = pdfplumber.open(pdf_path)

    # Collect text from each page separately to handle different formats
    page_texts = [page.extract_text() or "" for page in pdf.pages]

    # For joining, only apply minimal cleaning
    full_text = "\n".join(page_texts)

    # Fix broken numbers in older PDFs where extraction splits them oddly:
    # "7 1,164" -> "71,164" (single digit, space, then digit+comma pattern)
    # "35 ,672" -> "35,672" (space before comma)
    # "3 5,672" -> "35,672" (space within number)
    # But DON'T merge year patterns like "2023 33,674" or "Fall 2023 33,674.0"
    full_text = re.sub(r'(\d)\s+,', r'\1,', full_text)  # Fix space before comma
    # Fix single/double digit followed by space then digit+comma (not 4-digit year)
    full_text = re.sub(r'(?<!\d)(\d{1,2}) (\d,\d{3})', r'\1\2', full_text)

    lines = full_text.split('\n')

    data = {
        "admissions": {
            "applied": 0,
            "admitted": 0,
            "enrolled": 0,
            "acceptanceRate": 0,
            "yield": 0,
        },
        "testScores": {},
        "demographics": {
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
        },
        "costs": {"tuition": 0, "fees": 0, "roomAndBoard": 0, "totalCOA": 0},
        "financialAid": {
            "percentReceivingAid": 0,
            "averageAidPackage": 0,
            "averageNeedBasedGrant": 0,
            "percentNeedFullyMet": 0,
        },
    }

    # ===== ADMISSIONS (Section C1) =====
    men_applied = women_applied = 0
    men_admitted = women_admitted = 0
    men_enrolled = women_enrolled = 0
    total_applied = total_admitted = total_enrolled = 0

    for line in lines:
        line_lower = line.lower()

        # Format 1: "Total first-time, first-year (degree-seeking) who applied 71,164"
        if 'degree-seeking' in line_lower and 'who applied' in line_lower:
            nums = re.findall(r'(\d[\d,]*)', line)
            for num_str in nums:
                num = extract_number(num_str)
                if 30000 < num < 100000:  # Cornell gets 40k-75k apps
                    total_applied = num
                    break

        if 'degree-seeking' in line_lower and 'who were admitted' in line_lower:
            nums = re.findall(r'(\d[\d,]*)', line)
            for num_str in nums:
                num = extract_number(num_str)
                if 3000 < num < 15000:  # Cornell admits 4k-6k
                    total_admitted = num
                    break

        if 'degree-seeking' in line_lower and 'enrolled' in line_lower and 'full-time' not in line_lower and 'part-time' not in line_lower:
            nums = re.findall(r'(\d[\d,]*)', line)
            for num_str in nums:
                num = extract_number(num_str)
                if 2000 < num < 6000:  # Cornell enrolls 3k-4k
                    total_enrolled = num
                    break

        # Format 2: "Total first-time, first-year students who applied in Fall 2023 33,674.0 34,172.0"
        if 'students who applied in fall' in line_lower:
            nums = re.findall(r'([\d,]+\.?\d*)', line)
            nums = [extract_number(n) for n in nums if extract_number(n) > 10000]
            if len(nums) >= 2:
                men_applied = nums[0]
                women_applied = nums[1]

        if 'students admitted in fall' in line_lower:
            nums = re.findall(r'([\d,]+\.?\d*)', line)
            nums = [extract_number(n) for n in nums if 1000 < extract_number(n) < 10000]
            if len(nums) >= 2:
                men_admitted = nums[0]
                women_admitted = nums[1]

        if 'students enrolled in fall' in line_lower and 'full-time' not in line_lower and 'part-time' not in line_lower:
            nums = re.findall(r'([\d,]+\.?\d*)', line)
            nums = [extract_number(n) for n in nums if 500 < extract_number(n) < 5000]
            if len(nums) >= 2:
                men_enrolled = nums[0]
                women_enrolled = nums[1]

        # Format 3: Original format "men who applied" / "women who applied"
        if ('first-time' in line_lower or 'first-year' in line_lower or 'freshman' in line_lower):
            if 'men who applied' in line_lower and 'women' not in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 15000 < num < 50000:  # Men apps typically 15k-40k
                        men_applied = num
                        break
            elif 'women who applied' in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 15000 < num < 50000:
                        women_applied = num
                        break

            # Admitted
            if 'men who were admitted' in line_lower and 'women' not in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 1000 < num < 10000:
                        men_admitted = num
                        break
            elif 'women who were admitted' in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 1000 < num < 10000:
                        women_admitted = num
                        break

            # Enrolled
            if 'men who enrolled' in line_lower and 'women' not in line_lower and 'part-time' not in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 500 < num < 5000:
                        men_enrolled = num
                        break
            elif 'women who enrolled' in line_lower and 'part-time' not in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 500 < num < 5000:
                        women_enrolled = num
                        break

    # Use totals if found, otherwise sum gendered data
    if total_applied > 0:
        data["admissions"]["applied"] = total_applied
    elif men_applied > 0 or women_applied > 0:
        data["admissions"]["applied"] = men_applied + women_applied

    if total_admitted > 0:
        data["admissions"]["admitted"] = total_admitted
    elif men_admitted > 0 or women_admitted > 0:
        data["admissions"]["admitted"] = men_admitted + women_admitted

    if total_enrolled > 0:
        data["admissions"]["enrolled"] = total_enrolled
    elif men_enrolled > 0 or women_enrolled > 0:
        data["admissions"]["enrolled"] = men_enrolled + women_enrolled

    # Calculate rates
    if data["admissions"]["applied"] > 0 and data["admissions"]["admitted"] > 0:
        data["admissions"]["acceptanceRate"] = round(
            data["admissions"]["admitted"] / data["admissions"]["applied"], 4
        )
    if data["admissions"]["admitted"] > 0 and data["admissions"]["enrolled"] > 0:
        data["admissions"]["yield"] = round(
            data["admissions"]["enrolled"] / data["admissions"]["admitted"], 4
        )

    # Early Decision
    ed_applied = ed_admitted = 0
    for line in lines:
        line_lower = line.lower()
        if 'early decision' in line_lower:
            # Look for pattern like "Number of early decision applications received: 9555"
            if 'application' in line_lower and ('received' in line_lower or 'submitted' in line_lower):
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 3000 < num < 15000:  # ED apps typically 5k-10k
                        ed_applied = num
                        break
            elif 'admitted' in line_lower and 'plan' in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 500 < num < 5000:  # ED admits typically 1k-2.5k
                        ed_admitted = num
                        break

    if ed_applied > 0 and ed_admitted > 0:
        data["admissions"]["earlyDecision"] = {"applied": ed_applied, "admitted": ed_admitted}

    # ===== TEST SCORES (Section C9) =====
    sat_composite_25 = sat_composite_75 = 0
    sat_rw_25 = sat_rw_75 = 0
    sat_math_25 = sat_math_75 = 0
    act_25 = act_75 = 0

    for line in lines:
        line_lower = line.lower()

        # SAT Composite - look for direct composite score (1200-1600 range)
        # Avoid matching range labels like "(400 - 1600)"
        if 'sat composite' in line_lower and 'evidence' not in line_lower:
            # Find scores between 1200-1560 (realistic composite scores, avoid 1600 max label)
            scores = re.findall(r'\b(\d{4})\b', line)
            scores = [int(s) for s in scores if 1200 <= int(s) <= 1560]
            if len(scores) >= 2:
                sat_composite_25 = min(scores)
                sat_composite_75 = max(scores)

        # SAT Evidence-Based Reading and Writing (new SAT format)
        if ('evidence-based' in line_lower or 'ebrw' in line_lower or
            ('reading' in line_lower and 'writing' in line_lower)) and 'sat' in line_lower:
            scores = re.findall(r'\b(\d{3})\b', line)
            scores = [int(s) for s in scores if 600 <= int(s) <= 800]  # Realistic EBRW range
            if len(scores) >= 2:
                sat_rw_25 = min(scores)
                sat_rw_75 = max(scores)

        # Handle split line: "and Writing 690 760" (continuation from previous line)
        if line_lower.strip().startswith('and writing') and sat_rw_25 == 0:
            scores = re.findall(r'\b(\d{3})\b', line)
            scores = [int(s) for s in scores if 600 <= int(s) <= 800]
            if len(scores) >= 2:
                sat_rw_25 = min(scores)
                sat_rw_75 = max(scores)

        # SAT Critical Reading (old SAT format, pre-2016)
        if 'critical reading' in line_lower and 'sat' in line_lower:
            scores = re.findall(r'\b(\d{3})\b', line)
            scores = [int(s) for s in scores if 600 <= int(s) <= 800]
            if len(scores) >= 2 and sat_rw_25 == 0:  # Only use if no new format found
                sat_rw_25 = min(scores)
                sat_rw_75 = max(scores)

        # SAT Math
        if 'math' in line_lower and 'sat' in line_lower and 'evidence' not in line_lower:
            scores = re.findall(r'\b(\d{3})\b', line)
            scores = [int(s) for s in scores if 600 <= int(s) <= 800]  # Realistic Math range
            if len(scores) >= 2:
                sat_math_25 = min(scores)
                sat_math_75 = max(scores)

        # ACT Composite
        if 'act composite' in line_lower or ('composite' in line_lower and 'act' in line_lower):
            scores = re.findall(r'\b(\d{2})\b', line)
            scores = [int(s) for s in scores if 25 <= int(s) <= 36]  # Realistic ACT range for Cornell
            if len(scores) >= 2:
                act_25 = min(scores)
                act_75 = max(scores)

    # Build SAT data - prefer direct composite, fall back to calculated
    if sat_composite_25 > 0:
        # Use direct composite scores
        data["testScores"]["sat"] = {
            "composite": {
                "p25": sat_composite_25,
                "p50": (sat_composite_25 + sat_composite_75) // 2,
                "p75": sat_composite_75,
            },
            "readingWriting": {
                "p25": sat_rw_25,
                "p50": (sat_rw_25 + sat_rw_75) // 2 if sat_rw_25 > 0 else 0,
                "p75": sat_rw_75,
            },
            "math": {
                "p25": sat_math_25,
                "p50": (sat_math_25 + sat_math_75) // 2 if sat_math_25 > 0 else 0,
                "p75": sat_math_75,
            },
            "submissionRate": 0,
        }
    elif sat_rw_25 > 0 and sat_math_25 > 0:
        # Calculate composite from components
        data["testScores"]["sat"] = {
            "composite": {
                "p25": sat_rw_25 + sat_math_25,
                "p50": (sat_rw_25 + sat_math_25 + sat_rw_75 + sat_math_75) // 2,
                "p75": sat_rw_75 + sat_math_75,
            },
            "readingWriting": {
                "p25": sat_rw_25,
                "p50": (sat_rw_25 + sat_rw_75) // 2,
                "p75": sat_rw_75,
            },
            "math": {
                "p25": sat_math_25,
                "p50": (sat_math_25 + sat_math_75) // 2,
                "p75": sat_math_75,
            },
            "submissionRate": 0,
        }

    if act_25 > 0:
        data["testScores"]["act"] = {
            "composite": {
                "p25": act_25,
                "p50": (act_25 + act_75) // 2,
                "p75": act_75,
            },
            "submissionRate": 0,
        }

    # ===== DEMOGRAPHICS (Section B) =====
    undergrad = 0
    grad = 0

    for line in lines:
        line_lower = line.lower()

        # Total undergraduate enrollment
        if ('total undergraduate' in line_lower or
            ('undergraduate' in line_lower and 'degree-seeking' in line_lower and 'total' in line_lower) or
            'total of all undergraduate degree-seeking' in line_lower):
            nums = re.findall(r'(\d[\d,]*)', line)
            for num_str in nums:
                num = extract_number(num_str)
                if 10000 < num < 20000:  # Cornell undergrad ~15k
                    undergrad = num
                    break

        # Graduate enrollment
        if 'total graduate' in line_lower or 'total of all graduate' in line_lower:
            nums = re.findall(r'(\d[\d,]*)', line)
            for num_str in nums:
                num = extract_number(num_str)
                if 5000 < num < 15000:  # Cornell grad ~8-10k
                    grad = num
                    break

    data["demographics"]["enrollment"]["undergraduate"] = undergrad
    data["demographics"]["enrollment"]["graduate"] = grad
    data["demographics"]["enrollment"]["total"] = undergrad + grad

    # Demographics by race (Section B2)
    race_keywords = {
        'nonresident alien': 'international',
        'international': 'international',
        'hispanic': 'hispanicLatino',
        'latino': 'hispanicLatino',
        'black': 'blackAfricanAmerican',
        'african american': 'blackAfricanAmerican',
        'white': 'white',
        'asian': 'asian',
        'american indian': 'americanIndianAlaskaNative',
        'alaska native': 'americanIndianAlaskaNative',
        'native hawaiian': 'nativeHawaiianPacificIslander',
        'pacific islander': 'nativeHawaiianPacificIslander',
        'two or more': 'twoOrMoreRaces',
        'multiracial': 'twoOrMoreRaces',
        'race/ethnicity unknown': 'unknown',
        'unknown': 'unknown',
    }

    # Look for B2 table data
    in_b2 = False
    for line in lines:
        if 'B2' in line and ('ethnic' in line.lower() or 'race' in line.lower()):
            in_b2 = True
            continue
        if in_b2 and ('B3' in line or 'B4' in line):
            in_b2 = False
            continue

        if in_b2:
            line_lower = line.lower()
            for keyword, field in race_keywords.items():
                if keyword in line_lower:
                    nums = re.findall(r'\b(\d[\d,]*)\b', line)
                    for num_str in nums:
                        num = extract_number(num_str)
                        if 50 < num < 15000:  # Reasonable demographic count
                            if data["demographics"]["byRace"][field] == 0:
                                data["demographics"]["byRace"][field] = num
                            break
                    break

    # ===== COSTS (Section G) =====
    for line in lines:
        line_lower = line.lower()

        # Tuition
        if 'tuition' in line_lower and ('$' in line or any(c.isdigit() for c in line)):
            match = re.search(r'\$?\s*([\d,]+)', line)
            if match:
                num = extract_number(match.group(1))
                if 40000 < num < 80000:  # Reasonable tuition
                    data["costs"]["tuition"] = num

        # Required fees
        if 'required' in line_lower and 'fee' in line_lower:
            match = re.search(r'\$?\s*([\d,]+)', line)
            if match:
                num = extract_number(match.group(1))
                if 100 < num < 5000:  # Reasonable fees
                    data["costs"]["fees"] = num

        # Room and board
        if 'room' in line_lower and 'board' in line_lower:
            match = re.search(r'\$?\s*([\d,]+)', line)
            if match:
                num = extract_number(match.group(1))
                if 10000 < num < 25000:  # Reasonable R&B
                    data["costs"]["roomAndBoard"] = num

        # Food and housing (alternate naming)
        if 'food and housing' in line_lower:
            match = re.search(r'\$?\s*([\d,]+)', line)
            if match:
                num = extract_number(match.group(1))
                if 10000 < num < 25000:
                    data["costs"]["roomAndBoard"] = num

    data["costs"]["totalCOA"] = (
        data["costs"]["tuition"] +
        data["costs"]["fees"] +
        data["costs"]["roomAndBoard"]
    )

    # ===== FINANCIAL AID (Section H) =====
    for line in lines:
        line_lower = line.lower()

        # Average need-based grant (H2 k row)
        if ('average' in line_lower and 'need-based' in line_lower and 'grant' in line_lower) or \
           ('h2' in line_lower and 'k' in line_lower):
            match = re.search(r'\$\s*([\d,]+)', line)
            if match:
                num = extract_number(match.group(1))
                if 30000 < num < 80000:  # Reasonable grant
                    data["financialAid"]["averageNeedBasedGrant"] = num

        # Percent need fully met
        if 'need fully met' in line_lower or ('fully met' in line_lower and 'percent' in line_lower):
            match = re.search(r'(\d+\.?\d*)\s*%?', line)
            if match:
                pct = extract_float(match.group(1))
                if pct > 1:
                    pct = pct / 100
                if 0 < pct <= 1:
                    data["financialAid"]["percentNeedFullyMet"] = pct

        # Percent receiving need-based aid
        if 'receiving' in line_lower and 'need-based' in line_lower:
            match = re.search(r'(\d+\.?\d*)\s*%', line)
            if match:
                pct = extract_float(match.group(1))
                if pct > 1:
                    pct = pct / 100
                if 0 < pct <= 1:
                    data["financialAid"]["percentReceivingAid"] = pct

    pdf.close()

    print(f"  Applied: {data['admissions']['applied']:,}, Admitted: {data['admissions']['admitted']:,}, "
          f"Rate: {data['admissions']['acceptanceRate']:.1%}")
    if data['testScores'].get('sat'):
        sat = data['testScores']['sat']
        print(f"  SAT: {sat['composite']['p25']}-{sat['composite']['p75']}")
    if data['costs']['totalCOA'] > 0:
        print(f"  Total COA: ${data['costs']['totalCOA']:,}")

    return data


def main():
    cornell_dir = Path("Cornell")

    # Map filenames to academic years
    # NOTE: 2024-2025 PDF is a blank template with no data
    year_map = {
        "16-17.pdf": "2016-2017",
        "CDS_2017-2018-v5.pdf": "2017-2018",
        "CDS_2018-2019_v6.pdf": "2018-2019",
        "CDS_2019-2020_FINAL.pdf": "2019-2020",
        "CDS_2020-2021_FINAL.pdf": "2020-2021",
        "CDS_2021-2022_V5.pdf": "2021-2022",
        "CDS_2022-2023_Cornell-University-v5.pdf": "2022-2023",
        "CDS_UNL2_2023_2024-v11.pdf": "2023-2024",
        # "CDS-2024-2025.pdf": "2024-2025",  # Blank template, skipping
    }

    school_data = {
        "name": "Cornell University",
        "slug": "cornell",
        "years": {}
    }

    for filename, year in sorted(year_map.items(), key=lambda x: x[1]):
        pdf_path = cornell_dir / filename
        if pdf_path.exists():
            year_data = extract_cornell_year(str(pdf_path), year)
            school_data["years"][year] = year_data
        else:
            print(f"Warning: {pdf_path} not found")

    # Output
    output_path = Path("src/data/schools/cornell.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(school_data, f, indent=2)

    print(f"\nOutput written to: {output_path}")
    print(f"Years extracted: {len(school_data['years'])}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for year in sorted(school_data["years"].keys()):
        d = school_data["years"][year]
        adm = d["admissions"]
        print(f"{year}: {adm['applied']:,} applied, {adm['admitted']:,} admitted ({adm['acceptanceRate']:.1%})")


if __name__ == "__main__":
    main()
