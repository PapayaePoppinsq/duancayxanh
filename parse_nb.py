import json
import os

with open('notebook.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
print(f'Total cells: {len(cells)}')

with open('notebook_extracted.txt', 'w', encoding='utf-8') as out:
    for idx, cell in enumerate(cells):
        ctype = cell.get('cell_type')
        source = ''.join(cell.get('source', []))
        out.write(f"\n{'='*60}\nCELL {idx} [{ctype.upper()}]\n{'='*60}\n")
        out.write(source + "\n")

print("Done extracting to notebook_extracted.txt")
