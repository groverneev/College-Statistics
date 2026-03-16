import pdfplumber
import re

def extract_tables_from_pages(pdf_path, page_nums):
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            pg = i + 1
            if pg in page_nums:
                print(f'\n=== PAGE {pg} TABLES ===')
                tables = page.extract_tables()
                if tables:
                    for t_idx, t in enumerate(tables):
                        print(f'  Table {t_idx}:')
                        for row in t:
                            print('   ', row)
                else:
                    print('  No tables found')

                # Also try words
                print(f'\n=== PAGE {pg} WORDS ===')
                words = page.extract_words()
                print(' '.join(w['text'] for w in words[:200]))

# Check pages 12 and 13 of 2023-2024 CDS
extract_tables_from_pages(
    'College-Data/JohnHopkinsUniversity/CDS_2023-2024_JHU_20250401.pdf',
    [12, 13]
)
