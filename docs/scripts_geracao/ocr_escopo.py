import easyocr
import os

reader = easyocr.Reader(['pt'], gpu=False)

pages_dir = r'C:\Projetos\Michel\Sistema de Laudos\pages'
output_file = r'C:\Projetos\Michel\Sistema de Laudos\escopo_texto.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    for i in range(48):
        img_path = os.path.join(pages_dir, f'page_{i:02d}.png')
        if not os.path.exists(img_path):
            continue
        print(f'Processing page {i}...')
        results = reader.readtext(img_path, detail=0, paragraph=True)
        f.write(f'\n===== PAGE {i} =====\n')
        for text in results:
            f.write(text + '\n')
        print(f'  Page {i} done - {len(results)} paragraphs')

print('All done! Output saved to escopo_texto.txt')
