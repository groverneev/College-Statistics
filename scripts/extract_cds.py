#!/usr/bin/env python3
"""
CDS PDF Data Extractor

Extracts Common Data Set information from college PDF files and outputs JSON.
Uses pdfplumber for table extraction and text parsing.

Usage:
    python extract_cds.py <school_name> <pdf_path> [--output <output_path>]
    python extract_cds.py brown ../College-Data/Brown/CDS_2024_2025.pdf

Install dependencies:
    pip install pdfplumber
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is required. Install with: pip install pdfplumber")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def extract_number(text: str) -> Optional[int]:
    """Extract a number from text, handling commas and whitespace."""
    if not text:
        return None
    # Remove commas and whitespace
    cleaned = re.sub(r'[,\s]', '', str(text))
    # Try to extract number
    match = re.search(r'(\d+)', cleaned)
    if match:
        return int(match.group(1))
    return None


def extract_float(text: str) -> Optional[float]:
    """Extract a float/percentage from text."""
    if not text:
        return None
    cleaned = str(text).strip()
    # Handle percentages
    if '%' in cleaned:
        cleaned = cleaned.replace('%', '')
    # Remove commas
    cleaned = cleaned.replace(',', '')
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_percentage(text: str) -> Optional[float]:
    """Extract a percentage and convert to decimal (0-1 range)."""
    val = extract_float(text)
    if val is not None:
        # If value > 1, assume it's a percentage and convert
        if val > 1:
            return val / 100
        return val
    return None


class CDSExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf = pdfplumber.open(pdf_path)
        self.text = ""
        self.tables = []
        self._load_content()

    def _load_content(self):
        """Load all text and tables from the PDF."""
        all_text = []
        for page in self.pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
            tables = page.extract_tables()
            for table in tables:
                self.tables.append(table)
        self.text = "\n".join(all_text)

    def close(self):
        self.pdf.close()

    def _find_section(self, pattern: str) -> Optional[str]:
        """Find a section of text matching a pattern."""
        match = re.search(pattern, self.text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0)
        return None

    def _search_tables_for_row(self, row_identifier: str) -> Optional[list]:
        """Search all tables for a row containing the identifier."""
        for table in self.tables:
            for row in table:
                if row and any(row_identifier.lower() in str(cell).lower() for cell in row if cell):
                    return row
        return None

    def extract_admissions(self) -> dict:
        """Extract admissions data (Section C)."""
        data = {
            "applied": 0,
            "admitted": 0,
            "enrolled": 0,
            "acceptanceRate": 0,
            "yield": 0,
        }

        # Look for C1 section - First-time, first-year students
        # Common patterns in CDS

        # Try to find total applicants
        patterns = [
            r"Total first-time.*?applicants.*?(\d[\d,]*)",
            r"Total.*?applicants.*?men.*?women.*?Total.*?(\d[\d,]*)",
            r"Number of applicants.*?(\d[\d,]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE | re.DOTALL)
            if match:
                data["applied"] = extract_number(match.group(1)) or 0
                break

        # Look for admitted students
        patterns = [
            r"Total first-time.*?admitted.*?(\d[\d,]*)",
            r"Number.*?admitted.*?(\d[\d,]*)",
            r"Admitted.*?Total.*?(\d[\d,]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE | re.DOTALL)
            if match:
                data["admitted"] = extract_number(match.group(1)) or 0
                break

        # Look for enrolled students
        patterns = [
            r"Total first-time.*?enrolled.*?(\d[\d,]*)",
            r"Number.*?enrolled.*?(\d[\d,]*)",
            r"Enrolled.*?Total.*?(\d[\d,]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE | re.DOTALL)
            if match:
                data["enrolled"] = extract_number(match.group(1)) or 0
                break

        # Search tables for admissions data
        for table in self.tables:
            if not table:
                continue
            for i, row in enumerate(table):
                if not row:
                    continue
                row_text = ' '.join(str(cell) for cell in row if cell).lower()

                # Look for applicants row
                if 'applicants' in row_text and ('total' in row_text or len([c for c in row if c and extract_number(str(c))]) >= 1):
                    for cell in row:
                        num = extract_number(str(cell))
                        if num and num > 1000:  # Likely total applicants
                            if data["applied"] == 0 or num > data["applied"]:
                                data["applied"] = num

                # Look for admitted row
                if 'admitted' in row_text:
                    for cell in row:
                        num = extract_number(str(cell))
                        if num and num > 100:
                            if data["admitted"] == 0:
                                data["admitted"] = num

                # Look for enrolled row
                if 'enrolled' in row_text and 'full' not in row_text:
                    for cell in row:
                        num = extract_number(str(cell))
                        if num and num > 100:
                            if data["enrolled"] == 0:
                                data["enrolled"] = num

        # Calculate rates
        if data["applied"] > 0 and data["admitted"] > 0:
            data["acceptanceRate"] = round(data["admitted"] / data["applied"], 4)
        if data["admitted"] > 0 and data["enrolled"] > 0:
            data["yield"] = round(data["enrolled"] / data["admitted"], 4)

        # Try to extract Early Decision/Early Action data
        ed_data = self._extract_early_decision()
        if ed_data:
            data["earlyDecision"] = ed_data

        ea_data = self._extract_early_action()
        if ea_data:
            data["earlyAction"] = ea_data

        return data

    def _extract_early_decision(self) -> Optional[dict]:
        """Extract Early Decision statistics."""
        ed_applied = None
        ed_admitted = None

        # Look for ED patterns
        patterns = [
            r"Early Decision.*?applied.*?(\d[\d,]*)",
            r"ED.*?applicants.*?(\d[\d,]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                ed_applied = extract_number(match.group(1))
                break

        patterns = [
            r"Early Decision.*?admitted.*?(\d[\d,]*)",
            r"ED.*?admitted.*?(\d[\d,]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                ed_admitted = extract_number(match.group(1))
                break

        if ed_applied and ed_admitted:
            return {"applied": ed_applied, "admitted": ed_admitted}
        return None

    def _extract_early_action(self) -> Optional[dict]:
        """Extract Early Action statistics."""
        ea_applied = None
        ea_admitted = None

        patterns = [
            r"Early Action.*?applied.*?(\d[\d,]*)",
            r"EA.*?applicants.*?(\d[\d,]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                ea_applied = extract_number(match.group(1))
                break

        patterns = [
            r"Early Action.*?admitted.*?(\d[\d,]*)",
            r"EA.*?admitted.*?(\d[\d,]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                ea_admitted = extract_number(match.group(1))
                break

        if ea_applied and ea_admitted:
            return {"applied": ea_applied, "admitted": ea_admitted}
        return None

    def extract_test_scores(self) -> dict:
        """Extract SAT/ACT score data (Section C9)."""
        data = {}

        # SAT scores
        sat_data = {
            "composite": {"p25": 0, "p50": 0, "p75": 0},
            "readingWriting": {"p25": 0, "p50": 0, "p75": 0},
            "math": {"p25": 0, "p50": 0, "p75": 0},
            "submissionRate": 0,
        }

        # Look for SAT patterns
        # Pattern: "SAT Evidence-Based Reading and Writing" followed by scores
        sat_erw_pattern = r"SAT Evidence-Based Reading.*?(\d{3})\s*[-–]\s*(\d{3})"
        match = re.search(sat_erw_pattern, self.text, re.IGNORECASE)
        if match:
            sat_data["readingWriting"]["p25"] = int(match.group(1))
            sat_data["readingWriting"]["p75"] = int(match.group(2))
            sat_data["readingWriting"]["p50"] = (sat_data["readingWriting"]["p25"] + sat_data["readingWriting"]["p75"]) // 2

        sat_math_pattern = r"SAT Math.*?(\d{3})\s*[-–]\s*(\d{3})"
        match = re.search(sat_math_pattern, self.text, re.IGNORECASE)
        if match:
            sat_data["math"]["p25"] = int(match.group(1))
            sat_data["math"]["p75"] = int(match.group(2))
            sat_data["math"]["p50"] = (sat_data["math"]["p25"] + sat_data["math"]["p75"]) // 2

        # Calculate composite
        if sat_data["readingWriting"]["p25"] > 0 and sat_data["math"]["p25"] > 0:
            sat_data["composite"]["p25"] = sat_data["readingWriting"]["p25"] + sat_data["math"]["p25"]
            sat_data["composite"]["p75"] = sat_data["readingWriting"]["p75"] + sat_data["math"]["p75"]
            sat_data["composite"]["p50"] = sat_data["readingWriting"]["p50"] + sat_data["math"]["p50"]

        # Look for SAT submission rate
        sat_submit_pattern = r"SAT.*?submitted.*?(\d+)%?"
        match = re.search(sat_submit_pattern, self.text, re.IGNORECASE)
        if match:
            sat_data["submissionRate"] = extract_percentage(match.group(1)) or 0

        # Search tables for SAT scores
        for table in self.tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(cell) for cell in row if cell).lower()

                if 'reading' in row_text and 'writing' in row_text:
                    scores = [extract_number(str(c)) for c in row if c and extract_number(str(c))]
                    scores = [s for s in scores if s and 200 <= s <= 800]
                    if len(scores) >= 2:
                        sat_data["readingWriting"]["p25"] = min(scores)
                        sat_data["readingWriting"]["p75"] = max(scores)
                        sat_data["readingWriting"]["p50"] = (min(scores) + max(scores)) // 2

                if 'math' in row_text and 'sat' in row_text:
                    scores = [extract_number(str(c)) for c in row if c and extract_number(str(c))]
                    scores = [s for s in scores if s and 200 <= s <= 800]
                    if len(scores) >= 2:
                        sat_data["math"]["p25"] = min(scores)
                        sat_data["math"]["p75"] = max(scores)
                        sat_data["math"]["p50"] = (min(scores) + max(scores)) // 2

        if sat_data["readingWriting"]["p25"] > 0 or sat_data["math"]["p25"] > 0:
            # Recalculate composite
            if sat_data["readingWriting"]["p25"] > 0 and sat_data["math"]["p25"] > 0:
                sat_data["composite"]["p25"] = sat_data["readingWriting"]["p25"] + sat_data["math"]["p25"]
                sat_data["composite"]["p75"] = sat_data["readingWriting"]["p75"] + sat_data["math"]["p75"]
                sat_data["composite"]["p50"] = sat_data["readingWriting"]["p50"] + sat_data["math"]["p50"]
            data["sat"] = sat_data

        # ACT scores
        act_data = {
            "composite": {"p25": 0, "p50": 0, "p75": 0},
            "submissionRate": 0,
        }

        act_pattern = r"ACT Composite.*?(\d{2})\s*[-–]\s*(\d{2})"
        match = re.search(act_pattern, self.text, re.IGNORECASE)
        if match:
            act_data["composite"]["p25"] = int(match.group(1))
            act_data["composite"]["p75"] = int(match.group(2))
            act_data["composite"]["p50"] = (act_data["composite"]["p25"] + act_data["composite"]["p75"]) // 2

        # Search tables for ACT
        for table in self.tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(cell) for cell in row if cell).lower()

                if 'act composite' in row_text or ('composite' in row_text and 'act' in row_text):
                    scores = [extract_number(str(c)) for c in row if c and extract_number(str(c))]
                    scores = [s for s in scores if s and 1 <= s <= 36]
                    if len(scores) >= 2:
                        act_data["composite"]["p25"] = min(scores)
                        act_data["composite"]["p75"] = max(scores)
                        act_data["composite"]["p50"] = (min(scores) + max(scores)) // 2

        if act_data["composite"]["p25"] > 0:
            data["act"] = act_data

        return data

    def extract_demographics(self) -> dict:
        """Extract enrollment and demographic data (Section B)."""
        data = {
            "enrollment": {
                "total": 0,
                "undergraduate": 0,
                "graduate": 0,
            },
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
            "byResidency": {
                "inState": 0,
                "outOfState": 0,
                "international": 0,
            },
        }

        # Look for enrollment numbers
        patterns = [
            (r"Total.*?undergraduate.*?enrollment.*?(\d[\d,]*)", "undergraduate"),
            (r"Undergraduate.*?degree-seeking.*?(\d[\d,]*)", "undergraduate"),
            (r"Total.*?graduate.*?enrollment.*?(\d[\d,]*)", "graduate"),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                data["enrollment"][field] = extract_number(match.group(1)) or 0

        # Search tables for enrollment
        for table in self.tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(cell) for cell in row if cell).lower()

                if 'undergraduate' in row_text and ('degree' in row_text or 'total' in row_text):
                    nums = [extract_number(str(c)) for c in row if extract_number(str(c))]
                    nums = [n for n in nums if n and n > 100]
                    if nums and data["enrollment"]["undergraduate"] == 0:
                        data["enrollment"]["undergraduate"] = max(nums)

        # Calculate total
        data["enrollment"]["total"] = data["enrollment"]["undergraduate"] + data["enrollment"]["graduate"]

        # Look for demographic breakdown - this is usually in Section B2
        race_mapping = {
            "nonresident": "international",
            "international": "international",
            "hispanic": "hispanicLatino",
            "latino": "hispanicLatino",
            "black": "blackAfricanAmerican",
            "african american": "blackAfricanAmerican",
            "white": "white",
            "asian": "asian",
            "american indian": "americanIndianAlaskaNative",
            "alaska native": "americanIndianAlaskaNative",
            "native hawaiian": "nativeHawaiianPacificIslander",
            "pacific islander": "nativeHawaiianPacificIslander",
            "two or more": "twoOrMoreRaces",
            "multiracial": "twoOrMoreRaces",
            "unknown": "unknown",
            "race/ethnicity unknown": "unknown",
        }

        for table in self.tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(cell) for cell in row if cell).lower()

                for keyword, field in race_mapping.items():
                    if keyword in row_text:
                        nums = [extract_number(str(c)) for c in row if extract_number(str(c))]
                        nums = [n for n in nums if n]
                        if nums:
                            # Take the largest number as the total
                            data["byRace"][field] = max(nums)
                        break

        return data

    def extract_costs(self) -> dict:
        """Extract cost data (Section G)."""
        data = {
            "tuition": 0,
            "fees": 0,
            "roomAndBoard": 0,
            "totalCOA": 0,
        }

        # Look for tuition patterns
        patterns = [
            (r"Tuition.*?\$?([\d,]+)", "tuition"),
            (r"Required fees.*?\$?([\d,]+)", "fees"),
            (r"Room and board.*?\$?([\d,]+)", "roomAndBoard"),
            (r"Room & board.*?\$?([\d,]+)", "roomAndBoard"),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                data[field] = extract_number(match.group(1)) or 0

        # Search tables for costs
        for table in self.tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(cell) for cell in row if cell).lower()

                if 'tuition' in row_text and 'fee' not in row_text:
                    nums = [extract_number(str(c)) for c in row if extract_number(str(c))]
                    nums = [n for n in nums if n and n > 1000]
                    if nums and data["tuition"] == 0:
                        data["tuition"] = max(nums)

                if ('required' in row_text and 'fee' in row_text) or row_text.strip().startswith('fees'):
                    nums = [extract_number(str(c)) for c in row if extract_number(str(c))]
                    nums = [n for n in nums if n and n > 100]
                    if nums and data["fees"] == 0:
                        data["fees"] = max(nums)

                if 'room' in row_text and 'board' in row_text:
                    nums = [extract_number(str(c)) for c in row if extract_number(str(c))]
                    nums = [n for n in nums if n and n > 1000]
                    if nums and data["roomAndBoard"] == 0:
                        data["roomAndBoard"] = max(nums)

        # Calculate total COA
        data["totalCOA"] = data["tuition"] + data["fees"] + data["roomAndBoard"]

        return data

    def extract_financial_aid(self) -> dict:
        """Extract financial aid data (Section H)."""
        data = {
            "percentReceivingAid": 0,
            "averageAidPackage": 0,
            "averageNeedBasedGrant": 0,
            "percentNeedFullyMet": 0,
        }

        # Look for financial aid patterns
        patterns = [
            (r"Percent.*?receiving.*?aid.*?(\d+\.?\d*)%?", "percentReceivingAid"),
            (r"(\d+\.?\d*)%.*?receiving.*?need-based", "percentReceivingAid"),
            (r"Average.*?financial aid.*?\$?([\d,]+)", "averageAidPackage"),
            (r"Average.*?need-based.*?grant.*?\$?([\d,]+)", "averageNeedBasedGrant"),
            (r"Percent.*?need fully met.*?(\d+\.?\d*)%?", "percentNeedFullyMet"),
            (r"(\d+\.?\d*)%.*?need fully met", "percentNeedFullyMet"),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                if field in ["percentReceivingAid", "percentNeedFullyMet"]:
                    val = extract_percentage(match.group(1))
                    if val:
                        data[field] = val
                else:
                    data[field] = extract_number(match.group(1)) or 0

        # Search tables for financial aid
        for table in self.tables:
            if not table:
                continue
            for row in table:
                if not row:
                    continue
                row_text = ' '.join(str(cell) for cell in row if cell).lower()

                if 'average' in row_text and 'grant' in row_text and 'need' in row_text:
                    nums = [extract_number(str(c)) for c in row if extract_number(str(c))]
                    nums = [n for n in nums if n and n > 1000]
                    if nums and data["averageNeedBasedGrant"] == 0:
                        data["averageNeedBasedGrant"] = max(nums)

                if 'fully met' in row_text or 'full need' in row_text:
                    for cell in row:
                        pct = extract_percentage(str(cell))
                        if pct and pct > 0:
                            data["percentNeedFullyMet"] = pct
                            break

        return data

    def extract_all(self) -> dict:
        """Extract all CDS data."""
        logger.info(f"Extracting data from: {self.pdf_path}")

        data = {
            "admissions": self.extract_admissions(),
            "testScores": self.extract_test_scores(),
            "demographics": self.extract_demographics(),
            "costs": self.extract_costs(),
            "financialAid": self.extract_financial_aid(),
        }

        return data


def extract_year_from_filename(filename: str) -> str:
    """Extract the academic year from a CDS filename."""
    # Common patterns: CDS_2024_2025.pdf, CDS_2024-2025.pdf, Brown CDS_2016-2017_Final.pdf
    patterns = [
        r"(\d{4})[-_](\d{4})",
        r"(\d{4})",
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


def process_school(school_name: str, pdf_dir: str, output_dir: str) -> dict:
    """Process all PDFs for a school and generate combined JSON."""
    school_data = {
        "name": school_name.title(),
        "slug": school_name.lower(),
        "years": {},
    }

    pdf_path = Path(pdf_dir)
    if not pdf_path.exists():
        logger.error(f"PDF directory not found: {pdf_dir}")
        return school_data

    pdf_files = list(pdf_path.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in: {pdf_dir}")
        return school_data

    for pdf_file in sorted(pdf_files):
        year = extract_year_from_filename(pdf_file.name)
        logger.info(f"Processing {pdf_file.name} (Year: {year})")

        try:
            extractor = CDSExtractor(str(pdf_file))
            year_data = extractor.extract_all()
            extractor.close()

            school_data["years"][year] = year_data
            logger.info(f"  Extracted: {year}")
        except Exception as e:
            logger.error(f"  Error processing {pdf_file.name}: {e}")

    return school_data


def main():
    parser = argparse.ArgumentParser(description="Extract CDS data from PDF files")
    parser.add_argument("school", help="School name (e.g., brown, harvard)")
    parser.add_argument("--pdf-dir", help="Directory containing PDF files (default: ./College-Data/<School>)")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--single-pdf", help="Process a single PDF file instead of directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    school_name = args.school.lower()

    if args.single_pdf:
        # Process single PDF
        year = extract_year_from_filename(args.single_pdf)
        extractor = CDSExtractor(args.single_pdf)
        year_data = extractor.extract_all()
        extractor.close()

        school_data = {
            "name": school_name.title(),
            "slug": school_name,
            "years": {year: year_data},
        }
    else:
        # Process directory
        pdf_dir = args.pdf_dir or f"./College-Data/{school_name.title()}"
        output_dir = "src/data/schools"
        school_data = process_school(school_name, pdf_dir, output_dir)

    # Output
    output_path = args.output or f"src/data/schools/{school_name}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(school_data, f, indent=2)

    logger.info(f"Output written to: {output_path}")

    # Print summary
    print(f"\n{'='*50}")
    print(f"School: {school_data['name']}")
    print(f"Years extracted: {len(school_data['years'])}")
    for year in sorted(school_data['years'].keys()):
        data = school_data['years'][year]
        print(f"\n  {year}:")
        print(f"    Admissions: {data['admissions']['applied']:,} applied, "
              f"{data['admissions']['admitted']:,} admitted ({data['admissions']['acceptanceRate']:.1%})")
        if data.get('testScores', {}).get('sat'):
            sat = data['testScores']['sat']
            print(f"    SAT: {sat['composite']['p25']}-{sat['composite']['p75']}")
        if data.get('costs', {}).get('totalCOA'):
            print(f"    Total COA: ${data['costs']['totalCOA']:,}")


if __name__ == "__main__":
    main()
