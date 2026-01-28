#!/usr/bin/env python3
"""
UCLA CDS PDF Data Extractor

Extracts Common Data Set information from UCLA PDF files.
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
    # Remove spaces within numbers
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


def extract_ucla_year(pdf_path, year_label):
    """Extract all data from a single UCLA CDS PDF."""
    print(f"Processing {pdf_path} for year {year_label}")

    pdf = pdfplumber.open(pdf_path)
    full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Fix broken numbers
    full_text = re.sub(r'(\d)\s+,', r'\1,', full_text)

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
    men_applied = women_applied = other_applied = 0
    men_admitted = women_admitted = other_admitted = 0
    men_enrolled = women_enrolled = other_enrolled = 0

    for line in lines:
        line_lower = line.lower()

        # Handle both "freshman" (older format) and "first-time, first-year" (newer format)
        is_admissions_line = 'freshman' in line_lower or 'first-time' in line_lower or 'first-year' in line_lower

        if is_admissions_line:
            # Use word boundary checks to avoid "women" matching "men"
            has_men = re.search(r'\bmen\b', line_lower) is not None
            has_women = 'women' in line_lower

            # Applied
            if has_women and 'applied' in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 20000 < num < 100000:
                        women_applied = num
                        break
            elif has_men and 'applied' in line_lower and not has_women:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 20000 < num < 100000:
                        men_applied = num
                        break
            elif ('another gender' in line_lower or 'unknown/other' in line_lower) and 'applied' in line_lower:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 100 < num < 20000:
                        other_applied = num
                        break

            # Admitted (handles "(cid:425)ed" encoding as "admi")
            if has_women and ('admitted' in line_lower or 'admi' in line_lower):
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 2000 < num < 20000:
                        women_admitted = num
                        break
            elif has_men and ('admitted' in line_lower or 'admi' in line_lower) and not has_women:
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 2000 < num < 20000:
                        men_admitted = num
                        break
            elif ('another gender' in line_lower or 'unknown/other' in line_lower) and ('admitted' in line_lower or 'admi' in line_lower):
                nums = re.findall(r'(\d[\d,]*)', line)
                for num_str in nums:
                    num = extract_number(num_str)
                    if 50 < num < 5000:
                        other_admitted = num
                        break

            # Enrolled (full-time)
            if 'full-time' in line_lower or 'full-' in line_lower:
                if has_women and 'enrolled' in line_lower:
                    nums = re.findall(r'(\d[\d,]*)', line)
                    for num_str in nums:
                        num = extract_number(num_str)
                        if 1000 < num < 10000:
                            women_enrolled = num
                            break
                elif has_men and 'enrolled' in line_lower and not has_women:
                    nums = re.findall(r'(\d[\d,]*)', line)
                    for num_str in nums:
                        num = extract_number(num_str)
                        if 1000 < num < 10000:
                            men_enrolled = num
                            break
                elif ('another gender' in line_lower or 'unknown/other' in line_lower) and 'enrolled' in line_lower:
                    nums = re.findall(r'(\d[\d,]*)', line)
                    for num_str in nums:
                        num = extract_number(num_str)
                        if 1 < num < 1000:
                            other_enrolled = num
                            break

    # Sum up gendered data
    data["admissions"]["applied"] = men_applied + women_applied + other_applied
    data["admissions"]["admitted"] = men_admitted + women_admitted + other_admitted
    data["admissions"]["enrolled"] = men_enrolled + women_enrolled + other_enrolled

    # Calculate rates
    if data["admissions"]["applied"] > 0 and data["admissions"]["admitted"] > 0:
        data["admissions"]["acceptanceRate"] = round(
            data["admissions"]["admitted"] / data["admissions"]["applied"], 4
        )
    if data["admissions"]["admitted"] > 0 and data["admissions"]["enrolled"] > 0:
        data["admissions"]["yield"] = round(
            data["admissions"]["enrolled"] / data["admissions"]["admitted"], 4
        )

    # ===== TEST SCORES (Section C9) =====
    sat_composite_25 = sat_composite_75 = 0
    sat_rw_25 = sat_rw_75 = 0
    sat_math_25 = sat_math_75 = 0
    act_25 = act_75 = 0

    for line in lines:
        line_lower = line.lower()

        # SAT Composite
        if 'sat composite' in line_lower:
            scores = re.findall(r'\b(\d{4})\b', line)
            scores = [int(s) for s in scores if 1000 <= int(s) <= 1600]
            if len(scores) >= 2:
                sat_composite_25 = min(scores)
                sat_composite_75 = max(scores)

        # SAT Evidence-Based Reading and Writing
        if ('evidence' in line_lower and 'reading' in line_lower) or 'ebrw' in line_lower:
            scores = re.findall(r'\b(\d{3})\b', line)
            scores = [int(s) for s in scores if 500 <= int(s) <= 800]
            if len(scores) >= 2:
                sat_rw_25 = min(scores)
                sat_rw_75 = max(scores)

        # SAT Math
        if 'sat math' in line_lower and 'evidence' not in line_lower:
            scores = re.findall(r'\b(\d{3})\b', line)
            scores = [int(s) for s in scores if 500 <= int(s) <= 800]
            if len(scores) >= 2:
                sat_math_25 = min(scores)
                sat_math_75 = max(scores)

        # ACT Composite
        if 'act composite' in line_lower:
            scores = re.findall(r'\b(\d{2})\b', line)
            scores = [int(s) for s in scores if 20 <= int(s) <= 36]
            if len(scores) >= 2:
                act_25 = min(scores)
                act_75 = max(scores)

    # Build SAT data
    if sat_composite_25 > 0:
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

        # Undergraduate enrollment
        if 'undergraduate' in line_lower and ('total' in line_lower or 'degree-seeking' in line_lower):
            nums = re.findall(r'(\d[\d,]*)', line)
            for num_str in nums:
                num = extract_number(num_str)
                if 25000 < num < 50000:  # UCLA undergrad ~32k
                    undergrad = num
                    break

        # Graduate enrollment
        if 'graduate' in line_lower and 'total' in line_lower and 'undergraduate' not in line_lower:
            nums = re.findall(r'(\d[\d,]*)', line)
            for num_str in nums:
                num = extract_number(num_str)
                if 10000 < num < 20000:  # UCLA grad ~14k
                    grad = num
                    break

    data["demographics"]["enrollment"]["undergraduate"] = undergrad
    data["demographics"]["enrollment"]["graduate"] = grad
    data["demographics"]["enrollment"]["total"] = undergrad + grad

    # ===== COSTS (Section G) =====
    in_state_tuition = out_state_tuition = 0
    fees = 0
    room_board = 0

    for line in lines:
        line_lower = line.lower()

        # Tuition - UCLA is public so has in-state vs out-of-state
        if 'tuition' in line_lower:
            # Look for dollar amounts
            amounts = re.findall(r'\$\s*([\d,]+)', line)
            for amt in amounts:
                num = extract_number(amt)
                if 10000 < num < 20000:  # In-state ~$13k
                    if in_state_tuition == 0:
                        in_state_tuition = num
                elif 35000 < num < 50000:  # Out-of-state ~$43k
                    if out_state_tuition == 0:
                        out_state_tuition = num

        # Room and board
        if 'room' in line_lower and 'board' in line_lower:
            amounts = re.findall(r'\$\s*([\d,]+)', line)
            for amt in amounts:
                num = extract_number(amt)
                if 12000 < num < 25000:
                    room_board = num
                    break

    # Use out-of-state tuition for comparison with private schools
    data["costs"]["tuition"] = out_state_tuition if out_state_tuition > 0 else in_state_tuition
    data["costs"]["fees"] = fees
    data["costs"]["roomAndBoard"] = room_board
    data["costs"]["totalCOA"] = data["costs"]["tuition"] + fees + room_board

    # ===== FINANCIAL AID (Section H) =====
    for line in lines:
        line_lower = line.lower()

        # Average need-based grant
        if 'average' in line_lower and 'need-based' in line_lower and 'grant' in line_lower:
            match = re.search(r'\$\s*([\d,]+)', line)
            if match:
                num = extract_number(match.group(1))
                if 10000 < num < 50000:
                    data["financialAid"]["averageNeedBasedGrant"] = num

        # Percent need fully met
        if 'fully met' in line_lower:
            match = re.search(r'(\d+\.?\d*)\s*%', line)
            if match:
                pct = extract_float(match.group(1))
                if pct > 1:
                    pct = pct / 100
                if 0 < pct <= 1:
                    data["financialAid"]["percentNeedFullyMet"] = pct

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
    ucla_dir = Path("UCLA")

    # Map filenames to academic years
    year_map = {
        "17-18.pdf": "2017-2018",
        "18-19.pdf": "2018-2019",
        "19-20.pdf": "2019-2020",
        "20-21.pdf": "2020-2021",
        "21-22.pdf": "2021-2022",
        "22-23.pdf": "2022-2023",
        "23-24.pdf": "2023-2024",
        # "24-25.pdf": "2024-2025",  # Blank template, skipping
    }

    school_data = {
        "name": "UCLA",
        "slug": "ucla",
        "years": {}
    }

    for filename, year in sorted(year_map.items(), key=lambda x: x[1]):
        pdf_path = ucla_dir / filename
        if pdf_path.exists():
            year_data = extract_ucla_year(str(pdf_path), year)
            school_data["years"][year] = year_data
        else:
            print(f"Warning: {pdf_path} not found")

    # Output
    output_path = Path("src/data/schools/ucla.json")
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
