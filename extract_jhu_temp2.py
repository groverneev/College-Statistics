import pdfplumber
import re

def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return '\n'.join((page.extract_text() or '') for page in pdf.pages)

# Extract 2023-2024 PDF for Early Decision C2 section
print("=== 2023-2024 CDS - searching for C2/ED section ===")
text = extract_text('College-Data/JohnHopkinsUniversity/CDS_2023-2024_JHU_20250401.pdf')

# Search for "Number of early decision"
patterns = [
    'Number of early decision applications',
    'Number of applicants admitted under early decision',
    'C2 ',
    'Early Decision',
]

for p in patterns:
    idx = text.find(p)
    if idx != -1:
        print(f'\n--- Found: "{p}" at {idx} ---')
        print(text[max(0,idx-200):idx+500])
        print('---')

# Also look for the full C section
idx_c = text.find('\nC ')
if idx_c != -1:
    print('\n=== C SECTION START ===')
    print(text[idx_c:idx_c+2000])
