import pdfplumber
import re

def extract_pages(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            pages.append((i+1, text))
    return pages

# Extract 2023-2024 PDF - check pages around ED section
print("=== 2023-2024 CDS - ED section by page ===")
pages = extract_pages('College-Data/JohnHopkinsUniversity/CDS_2023-2024_JHU_20250401.pdf')

for pg_num, text in pages:
    if 'early decision applications received' in text.lower() or 'applicants admitted under early decision' in text.lower():
        print(f'\n--- PAGE {pg_num} ---')
        print(text)
        print('---')
