# Current state — 2026-09-22

Local version 0.1.0. Hugo library implemented with pinned Boulingua kit v1.22.0 and hugo-coder. The public repository is `https://github.com/boulingua/scriptlibrary`, with `main` as the publication branch. GitHub Pages is configured to deploy through GitHub Actions at `https://boulingua.github.io/scriptlibrary/`; check the workflow for hosted deployment status.

Three complete original-language narratives, 45 chapters, 77,278 words:

| Book | Chapters | Words |
|---|---:|---:|
| Alice’s Adventures in Wonderland | 12 | 26,349 |
| Candide, ou l’optimisme | 30 | 31,686 |
| Die Verwandlung | 3 | 19,243 |

15 searchable A5 PDFs, totalling 1,627 pages: original plus four practice editions for each book. Each practice edition uses a deterministic 20% sample of eligible letters. The online reader adjusts 0–100%, remembers settings locally, and retains a complete original-text fallback without JavaScript. PDF authors remain the literary authors. Source catalogues, frozen HTML, SHA-256 locks and full source licences are retained.

Verified: strict Hugo production build; local links/assets/downloads; complete PDF licence text, source/engine/PDF hashes, chapter counts, bookmarks, author metadata and glyph coverage; no out-of-page text blocks across all 1,627 pages. Representative PDF pages and desktop/mobile/light/dark browser views inspected. Browser tests compare all 15 book/profile combinations exactly against the edition engine and exercise persistence, original view, mobile navigation and no-JavaScript reading.

The local checkout contains ignored, checksum-verified Hugo 0.159.2 and Go 1.26.1 tools under `.tools/`. `scripts/hugo.sh` uses them without changing the global environment. This convenience payload is not part of Git; a fresh clone installs the documented toolchain normally.

Text is public domain in Germany and the USA; source distribution terms remain applicable. No modern translation or illustrations are included. Candide's later editorial preface and footnotes are excluded explicitly. No VG Wort marks or curriculum-conformance claims are assigned to the library.

README expanded for fresh clones, usage, troubleshooting, maintenance and licensing on 2026-09-22. Local checks rerun successfully before publication: extension unit/DOM and Chromium integration tests; library PDF/provenance verification, strict production build, 236 local references and browser parity checks.
