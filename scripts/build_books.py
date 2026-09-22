#!/usr/bin/env python3
"""Build complete, licensed reading editions from frozen HTML. No network access.

Run from any directory. Text is extracted once; one pinned JS engine handles
both browser and PDF substitutions. Source hashes and output hashes are recorded.
"""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
from xml.sax.saxutils import escape
import hashlib, json, re, subprocess, shutil

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'static/fonts'
BOOKS = json.loads((ROOT / 'sources/books.json').read_text())
PROFILES = [('original','Original'),('greek','Modern Greek'),('russian','Russian Cyrillic'),('ukrainian','Ukrainian'),('nordic','Nordic letters')]
PG_NOTICE = ('This eBook is for the use of anyone anywhere in the United States and most other parts of the world at no cost and with almost no restrictions whatsoever. '
             'You may copy it, give it away or re-use it under the terms of the Project Gutenberg License included with this eBook or online at www.gutenberg.org. '
             'If you are not located in the United States, you will have to check the laws of the country where you are located before using this eBook.')

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p, data): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def clean(s): return re.sub(r'\s+',' ',s).strip()

def runs_for(p, remove_notes=False):
    runs=[]
    def walk(n, em=False):
        if isinstance(n,NavigableString):
            t=re.sub(r'\s+',' ',str(n))
            if remove_notes:t=re.sub(r'\[\d+\]','',t)
            if not t:return
            if runs and runs[-1]['em']==em:runs[-1]['text']+=t
            else:runs.append(dict(text=t,em=em))
        elif isinstance(n,Tag):
            if n.name=='br':
                if runs:runs[-1]['text']+='\n'
            elif n.name not in ['img','script','style']:
                for c in n.children:walk(c,em or n.name in ['i','em'])
    walk(p)
    if runs:runs[0]['text']=runs[0]['text'].lstrip();runs[-1]['text']=runs[-1]['text'].rstrip()
    return [r for r in runs if r['text']]

def extract(book):
    source=ROOT/f"sources/raw/{book['pg_id']}.html"
    if digest(source)!=book['source_sha256']:raise ValueError('Frozen source digest mismatch: '+book['id'])
    soup=BeautifulSoup(source.read_bytes(),'html.parser')
    footer=soup.select_one('#pg-footer')
    if not footer or 'FULL PROJECT GUTENBERG' not in footer.get_text():raise ValueError('Missing full licence')
    licence='\n'.join(line.rstrip() for line in footer.get_text('\n',strip=True).splitlines())
    (ROOT/f"static/sources/{book['id']}-license.txt").write_text(licence+'\n')
    chapters=[]
    if book['pg_id']==22367:
        for h in soup.find_all('h2'):
            if h.get_text(strip=True) not in ['I.','II.','III.']:continue
            ps=[]
            for n in h.next_siblings:
                if isinstance(n,Tag) and (n.name=='h2' or n.get('id')=='pg-footer'):break
                if isinstance(n,Tag) and n.name=='p':ps.append(n)
            chapters.append((clean(h.get_text(' ')),ps))
    else:
        for d in soup.select('div.chapter'):
            h=d.find('h2')
            if h and re.match(r'CHAP(?:TER|ITRE)\s',clean(h.get_text(' '))):
                title=clean(h.get_text(' '))
                if book['language']=='fr':title=re.sub(r'\[\d+\]','',title)
                chapters.append((title,[p for p in d.find_all('p') if 'footnote' not in p.get('class',[]) and not p.find('img')]))
    if len(chapters)!=book['expected_chapters']:raise ValueError(f"Chapter count: {book['id']}: {len(chapters)}")
    output=[]
    for i,(title,ps) in enumerate(chapters,1):
        paragraphs=[]
        for j,p in enumerate(ps,1):
            runs=runs_for(p,book['language']=='fr')
            if not runs:continue
            paragraphs.append(dict(id=f'c{i}p{j}',runs=runs,verse=bool(p.find('br'))))
        if not paragraphs:raise ValueError('Empty chapter')
        output.append(dict(id=f'chapter-{i}',title=title,paragraphs=paragraphs))
    book['source_sha256']=digest(source);book['pg_notice']=PG_NOTICE
    return dict(id=book['id'],chapters=output),licence

def transformed(data,book,profile):
    request=dict(data=data,source=book['language'],profile=profile,book=book['id'])
    js="""
const fs=require('node:fs'),E=require(process.argv[1]);
const q=JSON.parse(fs.readFileSync(0,'utf8'));let eligible=0,replaced=0,letters=0;
for(const c of q.data.chapters)for(const p of c.paragraphs)p.runs.forEach((r,j)=>{
const o=E.transform(r.text,{source:q.source,profile:q.profile,percent:q.profile==='original'?0:20,seed:`${q.book}:${p.id}:${j}`});r.text=o.text;eligible+=o.eligible;replaced+=o.replaced;letters+=o.letters;});
console.log(JSON.stringify({data:q.data,eligible,replaced,letters,profile:E.profiles[q.profile]||null}));
"""
    r=subprocess.run(['node','-e',js,str(ROOT/'static/js/engine.js')],input=json.dumps(request),text=True,capture_output=True,check=True)
    return json.loads(r.stdout)

pdfmetrics.registerFont(TTFont('Noto',str(FONT/'NotoSerif-Regular.ttf')))
pdfmetrics.registerFont(TTFont('NotoItalic',str(FONT/'NotoSerif-Italic.ttf')))
pdfmetrics.registerFontFamily('Noto',normal='Noto',italic='NotoItalic',bold='Noto',boldItalic='NotoItalic')
INK=HexColor('#23272B');BLUE=HexColor('#1A73E8');MUTED=HexColor('#525960')
BODY=ParagraphStyle('body',fontName='Noto',fontSize=10.3,leading=15.8,alignment=TA_JUSTIFY,firstLineIndent=13,spaceAfter=3,textColor=INK,allowWidows=0,allowOrphans=0,splitLongWords=False)
FIRST=ParagraphStyle('first',parent=BODY,firstLineIndent=0)
VERSE=ParagraphStyle('verse',parent=BODY,alignment=TA_CENTER,firstLineIndent=0,fontName='NotoItalic',spaceBefore=9,spaceAfter=9)
HEADING=ParagraphStyle('chapter',parent=BODY,fontSize=16,leading=22,alignment=TA_CENTER,firstLineIndent=0,spaceAfter=25,keepWithNext=True)
SMALL=ParagraphStyle('small',parent=FIRST,fontSize=8,leading=11.5,alignment=TA_LEFT,spaceAfter=7,splitLongWords=True)
TITLE=ParagraphStyle('title',parent=FIRST,fontSize=30,leading=39,spaceAfter=24,alignment=TA_LEFT)

class BookDoc(BaseDocTemplate):
    def __init__(self,path,book,label):
        self.book=book;self.label=label
        super().__init__(str(path),pagesize=(420,595),leftMargin=48,rightMargin=45,topMargin=48,bottomMargin=47,title=book['title']+' — '+label,author=book['author'],subject='Boulingua alphabet-familiarisation edition; original-language literary text',creator='Boulingua Scriptlibrary',pageCompression=1)
        self.addPageTemplates(PageTemplate('book',frames=[Frame(48,47,327,500,id='text',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.decorate))
    def decorate(self,c,doc):
        if doc.page==1:return
        c.saveState();c.setFont('Noto',7);c.setFillColor(MUTED)
        text=self.book['title'] if doc.page%2 else self.book['author']
        c.drawCentredString(210,567,text)
        c.drawCentredString(210,25,str(doc.page));c.restoreState()
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and hasattr(f,'bookmark'):
            self.canv.bookmarkPage(f.bookmark);self.canv.addOutlineEntry(f.getPlainText(),f.bookmark,0,False)
            self.notify('TOCEntry',(0,f.getPlainText(),self.page,f.bookmark))

def markup(runs):
    return ''.join(('<i>'+escape(r['text']).replace('\n','<br/>')+'</i>') if r['em'] else escape(r['text']).replace('\n','<br/>') for r in runs)

def make_pdf(book,result,label,profile,licence):
    path=ROOT/f"static/downloads/{book['id']}-{profile}.pdf"
    story=[Spacer(1,48),Paragraph('boulingua / reading room',SMALL),Spacer(1,30),Paragraph(escape(book['title']),TITLE),Paragraph(escape(book['author']),HEADING),Spacer(1,24),Paragraph(escape(label)+(' — 20% of eligible letters' if profile!='original' else ' — unchanged literary text'),FIRST),Spacer(1,18),Paragraph(book['language_name']+' · '+str(book['year']),SMALL),PageBreak()]
    story += [Paragraph('About this reading edition',HEADING),Paragraph(escape(book['edition_note']),SMALL),Paragraph('Original literary author: '+escape(book['author'])+'. Edition prepared for Boulingua. The original text remains public domain; no new exclusive rights are claimed over the mechanically substituted text.',SMALL)]
    if result['profile']:
        p=result['profile']
        story += [Paragraph(escape(p['note']),SMALL),Paragraph('Letter key (context rules restrict where these pairs apply):',SMALL),Paragraph(escape(' · '.join(f'{a} / {b}' for a,b in p['map'].items())),FIRST),Spacer(1,12),Paragraph(f"{result['replaced']:,} of {result['eligible']:,} eligible letters changed. Approximately {100*result['replaced']/max(1,result['letters']):.1f}% of all letters. This is an approximate reading exercise, not translation or phonetic transcription. The source language and spelling context still matter.",SMALL)]
    story += [Paragraph('Source: <link href="'+book['source_url']+'" color="#1A73E8">'+book['source_url']+'</link>',SMALL),Paragraph(escape(PG_NOTICE),SMALL),Paragraph('The complete source licence is reproduced at the end. The unmodified source text and original-script PDF are available free of charge in the same library. Self-hosted Noto Serif is distributed under the SIL Open Font License 1.1; see the repository font notices.',SMALL),PageBreak(),Paragraph('Contents',HEADING)]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',parent=SMALL,fontSize=9,leading=14,spaceBefore=6)];story += [toc]
    for ch in result['data']['chapters']:
        h=Paragraph(escape(ch['title']),HEADING);h.bookmark=ch['id']
        story += [PageBreak(),h]
        for i,p in enumerate(ch['paragraphs']):story.append(Paragraph(markup(p['runs']),VERSE if p['verse'] else FIRST if i==0 else BODY))
    story += [PageBreak(),Paragraph('Source licence',HEADING)]
    # Keep every line of the complete source licence, untransformed.
    for line in licence.splitlines():
        if line.strip():story.append(Paragraph(escape(line),SMALL))
    BookDoc(path,book,label).multiBuild(story,canvasmaker=lambda *a,**kw:canvas.Canvas(*a,**{**kw,"invariant":1}))
    return dict(profile=profile,label=label,pdf=f'downloads/{path.name}',pages=len(PdfReader(path).pages),sha256=digest(path),replaced=result['replaced'],eligible=result['eligible'])

def main():
    lock=json.loads((ROOT/'third_party/engine.lock.json').read_text())
    if digest(ROOT/'static/js/engine.js')!=lock['sha256']:raise ValueError('Engine digest mismatch; sync it explicitly')
    catalog=[]
    for book in BOOKS:
        data,licence=extract(book)
        write_json(ROOT/f"data/texts/{book['id']}.json",data)
        write_json(ROOT/f"static/books-data/{book['id']}.json",data)
        original='\n\n'.join(ch['title']+'\n\n'+'\n\n'.join(''.join(r['text']for r in p['runs'])for p in ch['paragraphs'])for ch in data['chapters'])
        txt=book['title']+'\n'+book['author']+'\n\n'+PG_NOTICE+'\n\n'+original+'\n\n'+licence
        (ROOT/f"static/downloads/{book['id']}-original.txt").write_text('\n'.join(line.rstrip() for line in txt.splitlines())+'\n')
        book['chapters']=len(data['chapters']);book['words']=len(original.split());book['editions']=[]
        for profile,label in PROFILES:
            result=transformed(data,book,profile)
            if profile!='original' and not result['replaced']:raise ValueError(f'Empty practice edition: {book["id"]} {profile}')
            edition=make_pdf(book,result,label,profile,licence);book['editions'].append(edition)
            print(book['id'],profile,edition['pages'],'pages',edition['replaced'],'replacements',flush=True)
        front=dict(title=book['title'],book=book['id'],type='books',chapters=[dict(id=c['id'],title=c['title'])for c in data['chapters']])
        p=ROOT/f"content/books/{book['id']}/index.md";p.parent.mkdir(exist_ok=True,parents=True)
        p.write_text(json.dumps(front,ensure_ascii=False,indent=2)+'\n\n{{< booktext "'+book['id']+'" >}}\n')
        catalog.append(book)
    write_json(ROOT/'data/catalog.json',catalog)
    write_json(ROOT/'sources/editions-manifest.json',dict(engine=lock,books=catalog))

if __name__=='__main__':main()
