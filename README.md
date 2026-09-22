# Scriptlibrary

Boulingua's reading library: complete French, German and English classics with adjustable, sound-oriented single-letter practice. Includes original editions and Modern Greek, Russian Cyrillic, Ukrainian and Nordic practice editions, online and as typeset A5 PDFs.

## Read locally

Requires Hugo **extended 0.159.2** and Go **1.26.1**, matching the existing platform toolchain. Run `./scripts/hugo.sh server --baseURL http://localhost:1313/scriptlibrary/` and open that URL. The committed books and PDFs require no generation or network source retrieval. The local checkout also contains checksum-verified tools under ignored `.tools/`; the helper uses those without changing your global PATH. Hugo resolves pinned `kit` and hugo-coder modules on the first build.

The course header, footer, light/dark control and core CSS are imported from `kit v1.22.0`; reading layouts and library controls are specific to this product. No existing course files are modified. The catalogue uses the shared hub blue with language-coloured book covers. All fonts are self-hosted.

## Rebuild editions

Use Node 22+ and Python 3.12+ with `pip install -r requirements.txt`, then `python3 scripts/build_books.py`. It reads only frozen local sources. The initial collection contains all 12 Alice chapters, all 30 Candide narrative chapters and all 3 Verwandlung parts. PDFs retain searchable Unicode, embedded fonts, contents, outline bookmarks, running heads, original authorship, source notes and the complete source licence.

The unchanged JS engine is vendored with a SHA-256 lock. To update deliberately from the sibling extension, run `python3 scripts/sync_engine.py --source ../scriptbridge`, review the engine and lock changes, rebuild editions, and run the verification. Ordinary builds never silently sync rules or fetch new book text.

Run `python3 scripts/verify.py`, then `hugo --minify --gc --panicOnWarning` and `python3 scripts/check_links.py public`. For browser checks, run `npm ci` and `npm run test:browser` with the local server on port 1317 (or set `LIBRARY_URL`). The test uses `/usr/bin/chromium` by default; set `CHROMIUM` for another installation. The deployment workflow builds already committed editions and verifies them; it does not regenerate PDFs during deployment.

## Licensing

Original-language narratives: public domain in Germany and the USA, with source distribution terms retained. No modern translations or source illustrations are included. New editorial prose: CC BY-SA 4.0. Code: MIT. Fonts: SIL OFL 1.1. See [NOTICE.md](NOTICE.md), [source records](sources/books.json), and [edition provenance](sources/editions-manifest.json). No exclusive copyright is claimed over mechanical substitutions and no VG Wort marks are assigned to these narratives.

The supplied Azbuka notes informed pristine-source transforms, staged letter exposure and original-text access. Its R/Bookdown scaffold is preserved in the supplied archive, not required by this Hugo product. The broader German transliteration rules are not represented as equivalent sound mappings.
