#!/usr/bin/env python3
"""Validate source provenance, book completeness, engine parity and committed PDFs."""
from pathlib import Path
from pypdf import PdfReader
from fontTools.ttLib import TTFont
import json,hashlib,subprocess,re
from zipfile import ZipFile
root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((root/'sources/editions-manifest.json').read_text())
lock=json.loads((root/'third_party/engine.lock.json').read_text())
assert sha(root/'static/js/engine.js')==lock['sha256']==manifest['engine']['sha256']
extension=json.loads((root/'third_party/extension.lock.json').read_text())
assert sha(root/'static'/extension['file'])==extension['sha256']
with ZipFile(root/'static'/extension['file']) as z:
    assert hashlib.sha256(z.read('engine.js')).hexdigest()==lock['sha256']
sources=json.loads((root/'sources/books.json').read_text())
pdfs=0;pages=0
for book in manifest['books']:
    source=next(b for b in sources if b['id']==book['id'])
    assert sha(root/f"sources/raw/{book['pg_id']}.html")==source['source_sha256']==book['source_sha256']
    data=json.loads((root/f"data/texts/{book['id']}.json").read_text())
    assert data==json.loads((root/f"static/books-data/{book['id']}.json").read_text())
    assert len(data['chapters'])==source['expected_chapters']
    assert all(c['paragraphs'] for c in data['chapters'])
    ids=[p['id']for c in data['chapters']for p in c['paragraphs']];assert len(ids)==len(set(ids))
    assert book['words']>10000
    license_text=(root/f"static/sources/{book['id']}-license.txt").read_text()
    assert 'FULL PROJECT GUTENBERG' in license_text
    for edition in book['editions']:
        path=root/'static'/edition['pdf'];assert sha(path)==edition['sha256']
        reader=PdfReader(path);assert len(reader.pages)==edition['pages'];assert reader.metadata.author==book['author']
        assert len(reader.outline)==book['chapters']
        text='\n'.join(('\n'.join((p.extract_text() or '').splitlines()[2:]) if i else p.extract_text() or '') for i,p in enumerate(reader.pages))
        assert '\ufffd' not in text and '\x00' not in text
        assert 'FULL PROJECT GUTENBERG' in text
        normal=lambda s:re.sub(r'\s+','',s).replace('\u00ad','')
        assert normal(license_text) in normal(text),f"Licence truncated in {path.name}"
        if edition['profile']!='original':assert edition['replaced']>0
        pdfs+=1;pages+=len(reader.pages)
    print(book['id'],len(data['chapters']),'chapters;',book['words'],'words; 5 PDFs verified')
font=TTFont(root/'static/fonts/NotoSerif-Regular.ttf');cmap=font.getBestCmap()
for ch in 'μνπτκφλρσςβζαιобдфгклмнпрствзжґіøæäö':assert ord(ch) in cmap,f'Missing font glyph {ch}'
assert pdfs==15
print(f'PASS: {pdfs} PDFs, {pages} pages; frozen sources, full licences, outlines, authors, font coverage and engine digest')
