# Handover

Read `README.md`, `NOTICE.md`, `sources/books.json` and `CURRENT_STATE.md` first.

## Preview

```sh
./scripts/hugo.sh server --bind 127.0.0.1 --port 1317 --baseURL http://localhost:1317/scriptlibrary/ --disableFastRender
```

Open `http://localhost:1317/scriptlibrary/`. The helper uses the ignored local toolchain when available. A fresh clone needs Hugo extended 0.159.2 and Go 1.26.1 installed.

## Verify

```sh
python3 -m pip install -r requirements.txt
python3 scripts/verify.py
./scripts/hugo.sh --minify --gc --panicOnWarning --destination build-check
python3 scripts/check_links.py build-check
npm ci
npm run test:browser
```

Browser tests expect the preview on port 1317, overrideable with `LIBRARY_URL`. Chromium defaults to `/usr/bin/chromium`, overrideable with `CHROMIUM`. Screenshots are written under ignored `tmp/`. Do not use a running development server's livereload output as the production-link baseline.

## Editions and limitations

Version 0.2.0 has twelve books (four per source language), five practice sets and 192 PDFs. Greek, shared Cyrillic, Nordic, Polish and Czech each have fixed 20%, fixed 100% and progressive 20–100% editions. The shared `static/js/editions.js` schedule uses global paragraph position and is digest-recorded alongside the engine. Reader and PDF runs use the same seed and rate. English/German learning disclaimers and Cyrillic/Nordic differences are part of the product.

Only a limited sound-compatible subset is transformed, especially in the Latin practice sets. Cyrillic is deliberately consolidated; Nordic does not claim one common alphabet. Camus and Le Petit Prince were excluded for rights reasons; Maupassant fills that conditional slot.

## Rebuild or add books

`python3 scripts/build_books.py` (six worker processes by default, adjustable with `BOOK_WORKERS`) reads frozen source HTML offline and refuses source hash drift. It validates expected chapter counts, preserves inline emphasis and verse breaks, runs the pinned JS engine for every practice edition, emits PDFs and a provenance manifest, and regenerates Hugo content/data. No book text or PDF is generated during deployment.

New sources require a catalogue record, original author/death/publication information, a jurisdiction-specific rights basis, complete source licence, frozen file hash, explicit extraction scope and chapter count. Do not add copyrighted modern translations or illustrations on the strength of a public-domain underlying work.

`python3 scripts/sync_engine.py --source ../scriptbridge` deliberately updates the vendored engine and lock. It is never part of a routine build. The reader and PDFs must pass exact parity tests after an engine change. Copy an updated extension ZIP from `../scriptbridge/dist/` after packaging it.

## Architecture details

Course navigation, footer, colour control, tokens and shared CSS are imported. The library owns only its catalogue/reader templates and product styles. Two small head overrides omit root-relative theme font preloads and point icons at a project-relative local asset. The stylesheet pipeline remains hugo-coder's, with its MIT notice retained. Library accent aliases resolve on the body so they follow the inherited dark-mode tokens.

`third_party/` holds the engine lock and licences; do not rename it `vendor/`, which Go interprets as a module-vendoring directory. `.tools/`, generated site output, dependencies and review images are ignored.

The public repository is `https://github.com/boulingua/scriptlibrary`. GitHub Pages uses the GitHub Actions source; pushes to `main` run verification, build and deployment. Inspect the latest workflow and deployed URL for current hosted status. Native Chrome permission-consent review remains outside the automated browser harness. Sound matching is heuristic, not a phonetic dictionary or evidence of educational efficacy.

Use `--books <id>` only for a title-specific extraction/layout change. Rebuild every title after engine, schedule, shared front matter or typography changes. Optional `python3 scripts/check_pdf_layout.py` needs PyMuPDF and scans every PDF page for out-of-page text. The required verifier uses pinned dependencies; no optional layout package is required for deployment.
