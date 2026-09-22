#!/usr/bin/env python3
"""Check every local HTML link, fragment, script, font CSS URL and download."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,unquote
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else 'public').resolve();bad=[];checked=0
base='/scriptlibrary/'
def target(url,current):
    global checked
    u=urlparse(url)
    if u.scheme or u.netloc:return
    if not u.path:return
    path=unquote(u.path)
    if path.startswith(base):dest=root/path[len(base):]
    elif path.startswith('/'):bad.append((current,url,'outside project base'));return
    else:dest=current.parent/path
    if dest.is_dir():dest=dest/'index.html'
    checked+=1
    if not dest.exists():bad.append((current,url,'missing'))
    elif u.fragment and dest.suffix=='.html':
        page=BeautifulSoup(dest.read_text(),'html.parser')
        if not page.find(id=unquote(u.fragment)):bad.append((current,url,'missing anchor'))
for p in root.rglob('*.html'):
    s=BeautifulSoup(p.read_text(),'html.parser')
    for el in s.select('[href],[src]'):
        value=el.get('href',el.get('src',''))
        if value.startswith('#'):
            if len(value)>1 and not s.find(id=unquote(value[1:])):bad.append((p,value,'missing anchor'))
        else:target(value,p)
for p in root.rglob('*.css'):
    for value in re.findall(r'url\([\'"]?([^\)\'\"]+)',p.read_text()):target(value,p)
for p,url,reason in bad:print(p.relative_to(root),url,reason)
print(checked,'local references;',len(bad),'failures')
raise SystemExit(bool(bad))
