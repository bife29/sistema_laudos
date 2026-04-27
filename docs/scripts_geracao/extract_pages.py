import pymupdf
import os

output_dir = r'C:\Projetos\Michel\Sistema de Laudos\pages'
os.makedirs(output_dir, exist_ok=True)

doc = pymupdf.open(r'C:\Projetos\Michel\Sistema de Laudos\Sitema de Laudos.pdf')
for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(dpi=200)
    pix.save(os.path.join(output_dir, f'page_{i:02d}.png'))
    print(f'Saved page {i}')

print('Done!')
