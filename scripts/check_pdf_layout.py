#!/usr/bin/env python3
"""Optional visual-QA helper; requires PyMuPDF. Scan every committed edition."""
from pathlib import Path
import pymupdf,json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'sources/editions-manifest.json').read_text())
issues=[];pages=0
for book in manifest['books']:
 for edition in book['editions']:
  path=root/'static'/edition['pdf']
  with pymupdf.open(path) as doc:
   for i,page in enumerate(doc):
    pages+=1
    for b in page.get_text('blocks'):
     x0,y0,x1,y1,text,*_=b
     if text.strip() and (x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1):issues.append([path.name,i+1,'outside page',text[:80]])
    if '\ufffd' in page.get_text():issues.append([path.name,i+1,'replacement glyph'])
print(json.dumps(dict(pages=pages,issues=issues),indent=2))
raise SystemExit(bool(issues))
