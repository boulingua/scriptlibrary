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
import hashlib, json, re, subprocess, shutil, os, argparse
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'static/fonts'
BOOKS = json.loads((ROOT / 'sources/books.json').read_text())
PROFILES = [('original','Original')]+[(k,v['label']) for k,v in json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require(process.argv[1]).profiles))",str(ROOT/'static/js/engine.js')],text=True)).items()]
MODES = ['20','100','progressive']
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
    elif book['id']=='sandmann':
        start=next(p for p in soup.find_all('p') if clean(p.get_text())=='Der Sandmann')
        ps=[]
        for p in start.find_all_next('p'):
            if clean(p.get_text())=='Ignaz Denner':break
            ps.append(p)
        chapters=[('Der Sandmann',ps)]
    elif book['id']=='jekyll-hyde':
        chapters=[(clean(d.h2.get_text(' ')),d.find_all('p')) for d in soup.select('div.chapter')]
    elif book['id']=='trois-contes':
        story='';current=None
        for n in soup.body.find_all(['h3','p']):
            if n.find_parent(id='pg-footer'):break
            text=clean(n.get_text(' '))
            if n.name=='h3' and text in ['UN COEUR SIMPLE',"LA LÉGENDE DE SAINT JULIEN L'HOSPITALIER",'HÉRODIAS']:story=text
            elif n.name=='h3' and story and text in ['I','II','III','IV','V']:
                current=[story+' — '+text,[]];chapters.append(current)
            elif n.name=='p' and current:current[1].append(n)
    elif book['id']=='faust':
        for d in soup.select('div.chapter'):
            ps=d.find_all('p')
            if ps:chapters.append((clean(d.h2.get_text(' ')),ps))
    elif book['id']=='schimmelreiter':
        chapters=[(book['title'],soup.select_one('div.chapter').find_all('p'))]
    elif book['id']=='eugenie-grandet':
        start=next(h for h in soup.find_all('h2') if h.get_text(strip=True)=='A MARIA,')
        ps=[]
        for n in start.find_all_next():
            if n.get('id')=='pg-footer':break
            if n.name=='p' and n.get_text(strip=True):ps.append(n)
        chapters=[(book['title'],ps)]
    elif book['id']=='horla':
        current=None
        for n in soup.body.find_all(['h2','p']):
            if n.find_parent(id='pg-footer'):break
            title=clean(n.get_text(' '))
            if n.name=='p' and title=='FIN':break
            if n.name=='h2' and title not in ['1887'] and not n.find_parent(id='pg-header'):
                if title=="TROIS PAGES DU LIVRE D'UN CHASSEUR":
                    if current:current[0]+=' — '+title
                else:
                    current=[title,[]];chapters.append(current)
            elif n.name=='p' and current:current[1].append(n)
    elif book['id']=='hamlet':
        cast=soup.find('h3',string=lambda t:t and 'Dramatis' in t)
        ps=[]
        for n in cast.next_siblings:
            if isinstance(n,Tag) and n.name in ['h2','h3','div']:break
            if isinstance(n,Tag) and n.name=='p':ps.append(n)
        chapters.append(('Dramatis Personæ',ps))
        for d in soup.select('div.chapter'):
            h=d.find('h2')
            if not h or not clean(h.get_text()).startswith('ACT '):continue
            act=clean(h.get_text(' '));current=None
            for n in d.find_all(['h3','p']):
                if n.name=='h3':
                    current=[act+' — '+clean(n.get_text(' ')),[]];chapters.append(current)
                elif current:current[1].append(n)
    elif book['id']=='christmas-carol':
        current=None
        for n in soup.body.find_all(['h2','p']):
            if n.find_parent(id='pg-footer'):break
            if n.name=='h2' and clean(n.get_text()).startswith('STAVE '):
                current=[clean(n.get_text(' ')),[]];chapters.append(current)
            elif n.name=='p' and current and not n.find('img') and n.get_text(strip=True):current[1].append(n)
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
            paragraphs.append(dict(id=f'c{i}p{j}',runs=runs,verse=bool(p.find('br')),drama=book['id'] in ['faust','hamlet']))
        if not paragraphs:raise ValueError('Empty chapter')
        output.append(dict(id=f'chapter-{i}',title=title,paragraphs=paragraphs))
    book['source_sha256']=digest(source);book['pg_notice']=PG_NOTICE
    return dict(id=book['id'],chapters=output),licence

def transformed(data,book,profile,mode):
    request=dict(data=data,source=book['language'],profile=profile,mode=mode,book=book['id'])
    js="""
const fs=require('node:fs'),E=require(process.argv[1]),D=require(process.argv[2]);
const q=JSON.parse(fs.readFileSync(0,'utf8'));let eligible=0,replaced=0,letters=0;
const paragraphs=q.data.chapters.flatMap(c=>c.paragraphs);
paragraphs.forEach((p,index)=>p.runs.forEach((r,j)=>{
const o=E.transform(r.text,{source:q.source,profile:q.profile,percent:q.profile==='original'?0:D.percent(q.mode,index,paragraphs.length),seed:`${q.book}:${p.id}:${j}`});r.text=o.text;eligible+=o.eligible;replaced+=o.replaced;letters+=o.letters;}));
console.log(JSON.stringify({data:q.data,eligible,replaced,letters,profile:E.profiles[q.profile]||null}));
"""
    r=subprocess.run(['node','-e',js,str(ROOT/'static/js/engine.js'),str(ROOT/'static/js/editions.js')],input=json.dumps(request),text=True,capture_output=True,check=True)
    return json.loads(r.stdout)

pdfmetrics.registerFont(TTFont('Noto',str(FONT/'NotoSerif-Regular.ttf')))
pdfmetrics.registerFont(TTFont('NotoItalic',str(FONT/'NotoSerif-Italic.ttf')))
pdfmetrics.registerFontFamily('Noto',normal='Noto',italic='NotoItalic',bold='Noto',boldItalic='NotoItalic')
INK=HexColor('#23272B');BLUE=HexColor('#1A73E8');MUTED=HexColor('#525960')
BODY=ParagraphStyle('body',fontName='Noto',fontSize=10.3,leading=15.8,alignment=TA_JUSTIFY,firstLineIndent=13,spaceAfter=3,textColor=INK,allowWidows=0,allowOrphans=0,splitLongWords=False)
FIRST=ParagraphStyle('first',parent=BODY,firstLineIndent=0)
DRAMA=ParagraphStyle('drama',parent=FIRST,alignment=TA_LEFT,fontSize=9.5,leading=14,spaceAfter=9)
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

def make_pdf(book,result,label,profile,licence,mode):
    suffix='' if profile=='original' or mode=='20' else '-'+mode
    path=ROOT/f"static/downloads/{book['id']}-{profile}{suffix}.pdf"
    density={'20':'20% of eligible letters','100':'100% of eligible letters','progressive':'20–100% of eligible letters, increasing through the book'}[mode]
    story=[Spacer(1,48),Paragraph('boulingua / reading room',SMALL),Spacer(1,30),Paragraph(escape(book['title']),TITLE),Paragraph(escape(book['author']),HEADING),Spacer(1,24),Paragraph(escape(label)+(' — '+density if profile!='original' else ' — unchanged literary text'),FIRST),Spacer(1,18),Paragraph(book['language_name']+' · '+str(book['year']),SMALL),PageBreak()]
    story += [Paragraph('About this reading edition',HEADING),Paragraph(escape(book['edition_note']),SMALL),Paragraph('Original literary author: '+escape(book['author'])+'. Edition prepared for Boulingua. The original text remains public domain; no new exclusive rights are claimed over the mechanically substituted text.',SMALL)]
    if result['profile']:
        p=result['profile']
        story += [Paragraph(escape(p['note'].replace('→','to')),SMALL),Paragraph('Letter key (context rules restrict where these pairs apply):',SMALL),Paragraph(escape(' · '.join(f'{a} / {b}' for a,b in p['map'].items())),FIRST),Spacer(1,12),Paragraph(f"{result['replaced']:,} of {result['eligible']:,} eligible letters changed. Approximately {100*result['replaced']/max(1,result['letters']):.1f}% of all letters. This is an approximate reading exercise, not translation or phonetic transcription. The source language and spelling context still matter.",SMALL)]
    if profile!='original':
        story += [Paragraph('Learning exercise: a simplified representation',SMALL),Paragraph('For learning purposes only. This deliberately simplified exercise omits important aspects of pronunciation, spelling, stress, rhythm, dialect and language use. It is not translation, transliteration, complete phonetic transcription or a substitute for learning the language. 100% means all eligible letters, not every letter in the book.',SMALL)]
        story.append(Paragraph('Nur zu Lernzwecken: Dies ist eine bewusst vereinfachte und in verschiedenen Aspekten verkürzte Darstellung von Sprache. Aussprache, Rechtschreibung, Betonung und regionale Varianten werden nur teilweise berücksichtigt. Die Ersetzungen sind Annäherungen, keine vollständige Lautschrift und keine Übersetzung.',SMALL))
        if mode=='progressive':story.append(Paragraph('The rate increases linearly by paragraph position across the complete literary text: the first paragraph uses 20%, the last 100%. Every run within a paragraph uses the same rate. Headings, this introduction and the source licence stay unchanged.',SMALL))
    if profile=='cyrillic':
        story += [Paragraph('Cyrillic: one script, many alphabets',SMALL),Paragraph('Cyrillic is used in Russia, Ukraine, Belarus, Bulgaria, Serbia, North Macedonia and Montenegro, and by communities in Bosnia and Herzegovina and elsewhere. Rusyn uses regional Cyrillic standards. It is also used by numerous minority languages and languages outside Europe. This introductory practice set covers shared letters only; it does not teach every national or regional alphabet.',SMALL),Paragraph('Russian г usually represents /g/, whereas Ukrainian г represents /ɦ/ and ґ represents /g/. Ukrainian and Belarusian use і; Belarusian also uses ў. Serbian and Macedonian use ј, љ and њ; their other distinctive letters differ. Bulgarian ъ is a vowel, unlike the Russian hard sign. Sound values, letter inventories and even typographic forms vary. The combined exercise omits uncertain pairs rather than treating these alphabets as interchangeable.',SMALL)]
    if profile=='nordic':
        story += [Paragraph('Nordic letters: related forms, different sounds',SMALL),Paragraph('Danish and Norwegian use æ, ø and å; Swedish uses å, ä and ö. Finnish also uses ä and ö, with å mainly in Swedish names. Icelandic uses æ, ö, þ, ð and accented vowels; Faroese has distinct conventions including ð, æ and ø. Nordic is not one alphabet or pronunciation system.',SMALL),Paragraph('Icelandic æ usually represents /ai/, unlike the æ-like vowel practised here in selected English words. Icelandic þ and ð resemble the two English th sounds, but cannot replace a single English letter. Danish and Norwegian sounds vary with context and dialect. This exercise uses only selected Danish/Norwegian and Swedish approximations; it is not a complete Nordic alphabet course.',SMALL)]
    story += [Paragraph('Source: <link href="'+book['source_url']+'" color="#1A73E8">'+book['source_url']+'</link>',SMALL),Paragraph(escape(PG_NOTICE),SMALL),Paragraph('The complete source licence is reproduced at the end. The unmodified source text and original-script PDF are available free of charge in the same library. Self-hosted Noto Serif is distributed under the SIL Open Font License 1.1; see the repository font notices.',SMALL),PageBreak(),Paragraph('Contents',HEADING)]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',parent=SMALL,fontSize=9,leading=14,spaceBefore=6)];story += [toc]
    for ch in result['data']['chapters']:
        h=Paragraph(escape(ch['title']),HEADING);h.bookmark=ch['id']
        story += [PageBreak(),h]
        for i,p in enumerate(ch['paragraphs']):story.append(Paragraph(markup(p['runs']),DRAMA if p.get('drama') else VERSE if p['verse'] else FIRST if i==0 else BODY))
    story += [PageBreak(),Paragraph('Source licence',HEADING)]
    # Keep every line of the complete source licence, untransformed.
    for line in licence.splitlines():
        if line.strip():story.append(Paragraph(escape(line),SMALL))
    BookDoc(path,book,label).multiBuild(story,canvasmaker=lambda *a,**kw:canvas.Canvas(*a,**{**kw,"invariant":1}))
    return dict(profile=profile,mode='original' if profile=='original' else mode,label=label,density=density if profile!='original' else 'Unchanged original',pdf=f'downloads/{path.name}',pages=len(PdfReader(path).pages),sha256=digest(path),replaced=result['replaced'],eligible=result['eligible'])

def build_edition(args):
    book,data,licence,profile,label,mode=args
    result=transformed(data,book,profile,mode)
    if profile!='original' and not result['replaced']:raise ValueError(f'Empty practice edition: {book["id"]} {profile}')
    edition=make_pdf(book,result,label,profile,licence,mode)
    print(book['id'],profile,mode,edition['pages'],'pages',flush=True)
    return edition

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--books',nargs='+');args=ap.parse_args()
    if args.books and not set(args.books)<=set(b['id'] for b in BOOKS):raise ValueError('Unknown book selection')
    previous={b['id']:b for b in json.loads((ROOT/'data/catalog.json').read_text())} if args.books else {}
    lock=json.loads((ROOT/'third_party/engine.lock.json').read_text())
    if digest(ROOT/'static/js/engine.js')!=lock['sha256']:raise ValueError('Engine digest mismatch; sync it explicitly')
    write_json(ROOT/'data/profiles.json',[dict(id=k,label=v) for k,v in PROFILES])
    catalog=[]
    for book in BOOKS:
        if args.books and book['id'] not in args.books:
            catalog.append(previous[book['id']]);continue
        data,licence=extract(book)
        write_json(ROOT/f"data/texts/{book['id']}.json",data)
        write_json(ROOT/f"static/books-data/{book['id']}.json",data)
        original='\n\n'.join(ch['title']+'\n\n'+'\n\n'.join(''.join(r['text']for r in p['runs'])for p in ch['paragraphs'])for ch in data['chapters'])
        txt=book['title']+'\n'+book['author']+'\n\n'+PG_NOTICE+'\n\n'+original+'\n\n'+licence
        (ROOT/f"static/downloads/{book['id']}-original.txt").write_text('\n'.join(line.rstrip() for line in txt.splitlines())+'\n')
        book['chapters']=len(data['chapters']);book['words']=len(original.split());book['editions']=[]
        jobs=[(book,data,licence,profile,label,mode) for profile,label in PROFILES for mode in (['20'] if profile=='original' else MODES)]
        with ProcessPoolExecutor(max_workers=int(os.environ.get('BOOK_WORKERS','6'))) as pool:
            book['editions']=list(pool.map(build_edition,jobs))
        front=dict(title=book['title'],book=book['id'],type='books',chapters=[dict(id=c['id'],title=c['title'])for c in data['chapters']])
        p=ROOT/f"content/books/{book['id']}/index.md";p.parent.mkdir(exist_ok=True,parents=True)
        p.write_text(json.dumps(front,ensure_ascii=False,indent=2)+'\n\n{{< booktext "'+book['id']+'" >}}\n')
        catalog.append(book)
    write_json(ROOT/'data/catalog.json',catalog)
    write_json(ROOT/'sources/editions-manifest.json',dict(engine=lock,schedule=dict(file='static/js/editions.js',sha256=digest(ROOT/'static/js/editions.js'),progression='linear by global paragraph index, 20 to 100 inclusive'),books=catalog))

if __name__=='__main__':main()
