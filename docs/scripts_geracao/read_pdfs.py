import pymupdf
import os

# Read escopo PDF
doc = pymupdf.open(r'C:\Projetos\Michel\Sistema de Laudos\Sitema de Laudos.pdf')
print(f"=== Sitema de Laudos.pdf ===")
print(f"Pages: {len(doc)}")
for i, page in enumerate(doc):
    text = page.get_text()
    images = page.get_images()
    blocks = page.get_text('dict')['blocks']
    print(f"\nPage {i}: text_len={len(text.strip())}, images={len(images)}, blocks={len(blocks)}")
    if text.strip():
        print(text)
    for b in blocks[:3]:
        btype = b.get("type")
        print(f"  block type={btype}")

print("\n\n=== Laudo EEG ===")
doc2 = pymupdf.open(r'C:\Projetos\Michel\Sistema de Laudos\Laudo EEG Isaac Gomes Bueno.pdf')
print(f"Pages: {len(doc2)}")
for i, page in enumerate(doc2):
    text = page.get_text()
    images = page.get_images()
    print(f"\nPage {i}: text_len={len(text.strip())}, images={len(images)}")
    if text.strip():
        print(text)
