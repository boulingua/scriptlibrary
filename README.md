# Scriptlibrary

Boulingua's reading library: complete French, German and English classics with adjustable, sound-oriented single-letter practice. Includes original editions and Modern Greek, Russian Cyrillic, Ukrainian and Nordic practice editions, online and as typeset A5 PDFs.

Companion extension: [Scriptbridge](https://github.com/boulingua/scriptbridge). Both products use the same pinned transformation engine.

## Collection

| Original language | Book | Author | Complete narrative |
|---|---|---|---|
| English | Alice’s Adventures in Wonderland (1865) | Lewis Carroll | 12 chapters |
| French | Candide, ou l’optimisme (1759) | Voltaire | 30 chapters |
| German | Die Verwandlung (1915) | Franz Kafka | 3 parts |

Each title includes an original PDF and four practice PDFs, for **15 editions** in total, plus its original text download. Practice PDFs use 20% of eligible letters. The online reader offers 0–100%, alphabet selection and an original-text view; settings stay in browser local storage. Without JavaScript, the complete original remains readable. Sound matches are conservative heuristics, not a pronunciation dictionary.

## Read locally

Requires Hugo **extended 0.159.2** and Go **1.26.1**, matching the existing platform toolchain. Run `./scripts/hugo.sh server --baseURL http://localhost:1313/scriptlibrary/` and open that URL. The committed books and PDFs require no generation or network source retrieval. The local checkout also contains checksum-verified tools under ignored `.tools/`; the helper uses those without changing your global PATH. Hugo resolves pinned `kit` and hugo-coder modules on the first build.

The course header, footer, light/dark control and core CSS are imported from `kit v1.22.0`; reading layouts and library controls are specific to this product. No existing course files are modified. The catalogue uses the shared hub blue with language-coloured book covers. All fonts are self-hosted.

## Rebuild editions

Use Node 22+ and Python 3.12+ with `pip install -r requirements.txt`, then `python3 scripts/build_books.py`. It reads only frozen local sources. The initial collection contains all 12 Alice chapters, all 30 Candide narrative chapters and all 3 Verwandlung parts. PDFs retain searchable Unicode, embedded fonts, contents, outline bookmarks, running heads, original authorship, source notes and the complete source licence.

The unchanged JS engine is vendored with a SHA-256 lock. To update deliberately from the sibling extension, run `python3 scripts/sync_engine.py --source ../scriptbridge`, review the engine and lock changes, rebuild editions, and run the verification. Ordinary builds never silently sync rules or fetch new book text.

Run `python3 scripts/verify.py`, then `./scripts/hugo.sh --minify --gc --panicOnWarning --destination build-check` and `python3 scripts/check_links.py build-check`. For browser checks, run `npm ci` and `npm run test:browser` with the local server on port 1317 (or set `LIBRARY_URL`). The test uses `/usr/bin/chromium` by default; set `CHROMIUM` for another installation. The deployment workflow builds already committed editions and verifies them; it does not regenerate PDFs during deployment.

## Licensing

Original-language narratives: public domain in Germany and the USA, with source distribution terms retained. No modern translations or source illustrations are included. New editorial prose: CC BY-SA 4.0. Code: MIT. Fonts: SIL OFL 1.1. See [NOTICE.md](NOTICE.md), [source records](sources/books.json), and [edition provenance](sources/editions-manifest.json). No exclusive copyright is claimed over mechanical substitutions and no VG Wort marks are assigned to these narratives.

The supplied Azbuka notes informed pristine-source transforms, staged letter exposure and original-text access. Its R/Bookdown scaffold is preserved in the supplied archive, not required by this Hugo product. The broader German transliteration rules are not represented as equivalent sound mappings.

## Fresh-clone setup and checks

Install Hugo **extended 0.159.2**, Go **1.26.1**, Node **22+** and Python **3.12+**. Ignored `.tools/` binaries are a convenience in the original workspace and are not included in a clone. The Hugo helper also works with the documented tools on your PATH.

```sh
git clone https://github.com/boulingua/scriptlibrary.git
cd scriptlibrary
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/verify.py
./scripts/hugo.sh --minify --gc --panicOnWarning --destination build-check
python3 scripts/check_links.py build-check
npm ci
npx playwright install chromium
./scripts/hugo.sh server --bind 127.0.0.1 --port 1317 --baseURL http://localhost:1317/scriptlibrary/ --disableFastRender
```

Leave the server running and open `http://localhost:1317/scriptlibrary/`. In a second terminal inside the clone, run:

```sh
CHROMIUM="$(node -p 'require("@playwright/test").chromium.executablePath()')" npm run test:browser
```

Use `LIBRARY_URL` to test a different preview address. On Linux, missing browser system libraries can be installed with `npx playwright install --with-deps chromium`. The browser suite checks all book/alphabet combinations against the shared engine, saved settings, original view, mobile navigation, light/dark mode and complete no-JavaScript text. PDF verification checks source/engine/edition hashes, chapter counts, bookmarks, author metadata, glyph coverage and retained licence text.

## Repository structure

| Path | Contents |
|---|---|
| `sources/books.json`, `sources/raw/` | Source catalogue, extraction scope and frozen original HTML. |
| `sources/editions-manifest.json` | Generated edition metadata and digests. |
| `data/texts/`, `static/books-data/` | Extracted chapter and paragraph data. |
| `content/`, `layouts/`, `assets/css/` | Hugo pages, reader templates and product styles. |
| `static/downloads/` | 15 PDFs, original text downloads and extension ZIP. |
| `static/js/engine.js`, `third_party/` | Shared engine, digest locks and dependency licences. |
| `scripts/` | Extraction, PDF generation, explicit engine sync and verification. |
| `tests/` | Browser integration checks. |

Generated book content and downloads are committed so deployment never needs to retrieve or transform source books. Build output, tools, virtual environments and test screenshots stay ignored.

## Update editions or add a title

1. For mapping changes, update and test Scriptbridge first, then run `python3 scripts/sync_engine.py --source ../scriptbridge` here.
2. For a new title, record the original author, death and publication dates, catalogue URL, jurisdiction-specific rights basis, complete distribution licence, frozen source SHA-256, extraction scope and expected chapter count. Add extraction support in `scripts/build_books.py` as needed; the current parsers are specific to the three included books.
3. Run `python3 scripts/build_books.py`, review the generated text and representative PDF pages, and run the provenance, build, link and browser checks above. Confirm complete chapters, typography, bookmarks, glyph coverage and retained source terms.
4. If the extension changes, package it in its repository, copy the resulting ZIP to `static/downloads/`, and update `third_party/extension.lock.json` with its version, relative file path and SHA-256. Engine sync alone does not refresh the ZIP. The verifier checks that its embedded engine matches the library.
5. Commit source records, generated data, downloads and digest locks together. Document changed scope and verification in the state and handover files.

Do not infer that a modern translation, introduction, illustration or annotation is freely usable merely because the underlying narrative is old. Candide's later editorial preface and footnotes and the source illustrations are excluded; the original narratives are complete. Rights outside the documented Germany/USA basis need separate review.

## Hosting and troubleshooting

The configured production URL is `https://boulingua.github.io/scriptlibrary/`. GitHub Pages uses the **GitHub Actions** source. `.github/workflows/pages.yml` verifies committed editions, builds with the pinned toolchain, checks local links, uploads the site and deploys successful `main` builds. Pull requests build without deployment. Repository publication, a successful workflow and a live Pages deployment are separate milestones; see the current checkpoint below.

If Hugo cannot resolve modules on its first run, check network access and Go installation. If styles or downloads return 404, ensure the preview base URL includes `/scriptlibrary/`. Run production link checks against `build-check`, not a development server's livereload output. A digest mismatch requires reviewing the changed source or artifact and deliberately rebuilding it; do not bypass the verifier. A fresh clone does not require the sibling extension unless updating the engine or ZIP.

The reader loads fonts and scripts from the site and has no analytics configured. Its preferences stay in the browser; normal hosting requests still reach the hosting provider. PDFs can be downloaded for offline reading. See [NOTICE.md](NOTICE.md) for source and font terms, [LICENSE](LICENSE) for code and [LICENSE-CONTENT.md](LICENSE-CONTENT.md) for new editorial content.

[CURRENT_STATE.md](CURRENT_STATE.md), [HANDOVER.md](HANDOVER.md) and [VALIDATION.json](VALIDATION.json) record the checkpoint, continuation procedures and initial local evidence respectively.
