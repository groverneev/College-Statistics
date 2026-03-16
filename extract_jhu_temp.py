import pdfplumber
import re

def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return '\n'.join((page.extract_text() or '') for page in pdf.pages)

# Extract 2023-2024 PDF for Early Decision and H2
print("=== 2023-2024 CDS ===")
text = extract_text('College-Data/JohnHopkinsUniversity/CDS_2023-2024_JHU_20250401.pdf')

# Search for early decision data
idx = text.lower().find('early decision')
if idx != -1:
    print('=== EARLY DECISION CONTEXT ===')
    print(text[max(0,idx-100):idx+2000])
else:
    print('early decision not found')

# Search for H2
idx2 = text.lower().find('h2 ')
if idx2 != -1:
    print('\n=== H2 SECTION ===')
    print(text[max(0,idx2-100):idx2+3000])

# Also extract 2021-2022 for reference H2 parsing
print("\n\n=== 2021-2022 CDS H2 SECTION ===")
text2 = extract_text('College-Data/JohnHopkinsUniversity/CDS_2021-2022.pdf')
idx3 = text2.lower().find('h2 ')
if idx3 != -1:
    print(text2[max(0,idx3-100):idx3+3000])
