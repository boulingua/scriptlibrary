#!/usr/bin/env python3
"""Explicitly update the vendored engine from a sibling checkout; builds never sync."""
from pathlib import Path
import argparse,hashlib,json,shutil
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=root.parent/'scriptbridge');args=ap.parse_args()
src=args.source/'extension/engine.js'
dest=root/'static/js/engine.js'
shutil.copyfile(src,dest)
shutil.copyfile(args.source/'LICENSE',root/'third_party/scriptbridge-LICENSE')
(root/'third_party/engine.lock.json').write_text(json.dumps({'package':'@boulingua/scriptbridge','version':'0.1.0','source':'scriptbridge/extension/engine.js','sha256':hashlib.sha256(src.read_bytes()).hexdigest()},indent=2)+'\n')
print('Engine copied and digest locked')
