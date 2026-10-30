# Refinement record — 30 October 2026

This is a local engineering candidate on `refine/2026-10-30`. No hosted CI,
published release or production deployment of these changes has been observed.
The suite strategy and integration order live in the organisation repository,
`docs/refinement-2026-10-30.md` and `docs/release-candidate-2026-10-30.md`.

## Findings, implementation and verification

The library serves 18 preserved public-domain books with 16 PDF variants each and optional reversible script practice.

- High: Hugo HTML minification collapsed source paragraph whitespace. The reading shortcode now emits preformatted paragraph elements styled as normal book prose; browser verification compares original text, including whitespace, with frozen sources.
- High: the pinned PDF dependency had reported advisories. `pypdf` is now pinned to 6.21.4. A fresh Python 3.12 environment installed the exact requirements and verified all 288 PDFs and 36,623 pages, including source/licence metadata, outlines, font coverage and shared-engine digest.
- Medium: browser behaviour was outside CI. The Pages workflow now installs bundled Chromium, serves the built project under its actual URL prefix, and runs the browser test before deployment.

The real browser suite passed all 288 book/profile combinations, original-text restoration, preferences, dark mode, mobile layout, covers and no-JavaScript reading. Strict Hugo compilation and 943 local links passed. Existing PDF/source bytes were preserved. Passing these checks does not establish hosted CI success or publication of this candidate.

README.md contains the install, build, verification and preview commands. The next release action is review of the dependency/rendering changes and package digests, then a hosted run and deliberately approved deployment. Book-specific provenance remains in the existing source/licence records.
