# Refinement record — 30 October 2026

This is an engineering candidate on `refine/2026-10-30`. Exact-revision hosted
validation is recorded below. No release publication or production deployment
of these changes has been performed.
The suite strategy and integration order live in the organisation repository,
`docs/refinement-2026-10-30.md` and `docs/release-candidate-2026-10-30.md`.

## Findings, implementation and verification

The library serves 18 preserved public-domain books with 16 PDF variants each and optional reversible script practice.

- High: Hugo HTML minification collapsed source paragraph whitespace. The reading shortcode now emits preformatted paragraph elements styled as normal book prose; browser verification compares original text, including whitespace, with frozen sources.
- High: the pinned PDF dependency had reported advisories. `pypdf` is now pinned to 6.21.4. A fresh Python 3.12 environment installed the exact requirements and verified all 288 PDFs and 36,623 pages, including source/licence metadata, outlines, font coverage and shared-engine digest.
- Medium: browser behaviour was outside CI. The Pages workflow now installs bundled Chromium, serves the built project under its actual URL prefix, and runs the browser test before deployment.

The real browser suite passed all 288 book/profile combinations, original-text restoration, preferences, dark mode, mobile layout, covers and no-JavaScript reading. Strict Hugo compilation and 943 local links passed. Existing PDF/source bytes were preserved. Passing these checks does not establish hosted CI success or publication of this candidate.

README.md contains the install, build, verification and preview commands. The next release action is review of the dependency/rendering changes and package digests, then a hosted run and deliberately approved deployment. Book-specific provenance remains in the existing source/licence records.

## Re-audit remediation — 31 October 2026

The reader now stores its last practice alphabet separately from original view.
Cyrillic → original → reload → resume retains Cyrillic; existing saved records
without the new field retain their available practice profile. A legacy record
that stored only `original` never retained its prior alphabet, so falls back to
the documented default. The browser regression covers both journeys. Setup
instructions consistently use Playwright's bundled Chromium.

The verifier now re-extracts all 18 frozen source texts and complete licences,
recomputes all edition transformations and counts, and requires each expected
narrative paragraph to appear in PDF text in order. It checks every narrative
character against both supplied font styles. Whitespace and discretionary
hyphens are normalized for PDF layout; this is complete ordered narrative
inclusion, not a detector of arbitrary extra inserted text. Negative tests reject
missing, reordered or changed paragraphs and missing glyphs. Extraction no longer
writes licence files during read-only verification.

Fresh results:

- All **288 PDFs**, including all **270 transformed PDFs**, passed: **36,623
  pages and 166,912 ordered narrative paragraphs**, plus source/engine/edition
  hashes, complete licences, counts, outlines and author metadata.
- All **288 browser edition combinations** passed, including the new preference
  cases, original/no-JavaScript reading, responsive navigation and light/dark
  views; no browser errors or failed requests in the passing run.
- The three Python parity regressions and JS progression test passed. Strict
  Hugo 0.159.2 compilation against the local candidate kit passed; **989 local
  references** had no failures. One earlier browser run hit a wait timeout; added
  per-book diagnostics and a complete rerun passed without relaxing checks. Its
  original timeout cause was not established.
- Original source HTML, extracted book data, licences, fonts and all PDF bytes
  remain unchanged. The extension ZIP alone was replaced with Scriptbridge's
  byte-identical deterministic package and its digest lock updated to
  `c4ac9545183f623e66fd975849266cc65b9c6b440e873d80a3461de2405cc7c3`.

An independent code review found no further material defect in the parity or
packaging changes. These are local results. Hosted checks, the final published
kit dependency, production deployment/downloads and native Chrome consent for
the companion extension remain separate acceptance steps. The library can be
released independently of unfinished teaching-course or private-assessment
reviews. Whole-book slider work remains synchronous (roughly 100 ms for a large
book in the earlier probe); batching for slower devices is deferred.


## Analytics notice consistency — 31 October 2026

Plausible remains disabled. The privacy notice explicitly says so; copied claims of active Plausible collection were removed. This does not remove or make claims about separately documented hosting or other services.

Privacy pages declare their analytics policy, language and built URL. New kit gate C9 checks actual HTML scripts and visible notices against configuration; it rejects missing, duplicate or mismatched scripts and contradictory notices. Six gate regressions and three scaffold tests passed. Representative strict builds/C9 passed for website, nsf, nvt, gfl, Scriptlibrary and all three resource-hub notice languages; the suite integration run verifies the remaining sites. This is configuration/content evidence, not certification of the remote server or legal compliance.


## Hosted candidate verification — 31 October 2026

Commit `d84ae9be553b1684d2117b4d5759a50e223724a2` passed the [hosted workflow](https://github.com/boulingua/scriptlibrary/actions/runs/41203013519) on the review branch. The build checked the complete PDF corpus, unit tests, strict Hugo output, links and browser reader journeys. The deployment job was skipped because this was not `main`. These results apply to the recorded dependency pins; the separate coordinated foundation release remains pending.

## 2026-11-02 candidate-kit and historical-pin integration

The library's blue text failed contrast on its tinted panel and on the older
kit's background; old footer opacity reduced link contrast further. The product
now uses the existing darker hub token and opaque footer links. Book covers use
their visible author/title text as the accessible name. Automatic dark mode now
uses dark button ink as well as the explicit dark toggle. These changes preserve
all original book text, PDF bytes, source authors and the extension package.

Both the historical v1.22.0 pin and the local candidate kit passed strict Hugo
builds, all 288 reader/edition combinations, persisted-alphabet/original-view
journeys, mobile navigation, complete no-JavaScript text, and automated WCAG
2/2.1 A/AA home and automatic-dark reader-controls checks. Local-link checks
passed (946 historical / 998 candidate references); four Python regressions and
one JavaScript suite passed. The candidate shared C14 browser check also passed.
The initial Python preview transport intermittently reset script connections;
catch-only diagnostics establish that failure, and both final unchanged-timeout
runs passed against a stable static server. No production-runtime retry was added.

Three explicitly listed compatibility files remain byte-identical to the
candidate kit because the published historical pin lacks them. The manifest,
regression and retirement procedure in docs/kit-compatibility.md constrain this
transition. The initial A1 run reported two head shadows; the subsequent narrow
registry-bound exception described below does not permit arbitrary overrides.
The old kit's main.wrapper does not satisfy the candidate C14 #main-content
selector, so historical behavior is evidenced by the product checks rather than
claiming that new shared DOM assertion passed there. Course-only author,
curriculum, shortcode and RSS assumptions do not redefine this reading product.

Independent review found the automatic-dark button gap above; it was fixed and
both complete product runs repeated successfully. No further material finding
was identified in that bounded review. The dated integration JSON remains the
immutable local checkpoint; subsequent hosted verification is recorded below.
The earlier d84ae9b success remains evidence for that exact commit.

## Compatibility gate and hosted follow-up — 2 November 2026

The updated candidate A1 gate now accepts exactly the three registered temporary
copies at kit v1.22.0 when the manifest, local files and current kit bytes match.
Changed branding or partials, additional paths, module replacements and partial
retirement fail. Promoting the kit pin still requires removing all three copies
and the manifest together. The earlier integration receipt has not been rewritten.

Commit `21acdef705ae40a7162e23e458a43b9a6ddc06dc` passed the
[hosted workflow](https://github.com/boulingua/scriptlibrary/actions/runs/41480154465).
The build verified the complete PDF corpus, unit tests, strict Hugo output,
local links and browser reader/accessibility journeys. The deployment job was
skipped. This is hosted verification of that runtime commit under its recorded
pins, not publication of the coordinated foundation release or a deployment.
