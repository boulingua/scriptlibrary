# Current state — 2026-09-22

Version 0.2.0. Public repository: https://github.com/boulingua/scriptlibrary, branch `main`. Pages: https://boulingua.github.io/scriptlibrary/. Check GitHub Actions for the hosted status of the current commit; local verification below precedes publication.

Twelve complete selected original-language works, four each in German, French and English: 137 sections, 381,047 words. The catalogue and source extraction policies are in `sources/books.json`.

Five practice sets: Greek, shared Cyrillic, Nordic, Polish and Czech. Every title has an unchanged original and three PDF densities per set: 20%, 100%, progressive 20–100%. Total: **192 searchable A5 PDFs, 27,635 pages**. Progressive rates follow global paragraph order, never reset at chapters, and use the same shared schedule and engine as the online reader. Both source modules have digests in the edition manifest.

Cyrillic and Nordic introductions explain language/country differences and the limited shared subset. Page and PDF learning disclaimers explain the simplified treatment of pronunciation, spelling, stress and regional usage, in English and German. Nordic does not apply Icelandic æ with Norwegian sound values. Polish/Czech are intentionally sparse. No complete-language or learning-effectiveness claim is made.

Camus and Le Petit Prince are excluded for rights reasons. Maupassant’s full Le Horla collection fills the conditional slot. The collection includes Faust I with its preliminary pieces, all Hamlet scenes and cast, and the complete selected Sandmann story from Nachtstücke. Frozen source HTML, source notices, full licences, author metadata and output digests are retained. No modern translations, source illustrations or VG Wort marks are included.

Local verification passed: 192 exact reader/edition combinations, fixed/progressive schedule tests, persisted settings, original view, no-JavaScript complete text, mobile navigation and light/dark views; strict Hugo build; 685 local references without failures; all PDF/source/engine digests, complete licence text, outlines and fonts. Every PDF page was scanned for out-of-page text (zero issues); representative covers, notes, contents, prose and drama pages were visually reviewed. This is not a visual inspection of every page or a linguistic review of every word.

Hugo extended 0.159.2 and Go 1.26.1 remain pinned; ignored `.tools/` provides the local toolchain. Extension 0.2.0 is bundled and digest-checked. See `HANDOVER.md` for continuation and rebuild commands.
