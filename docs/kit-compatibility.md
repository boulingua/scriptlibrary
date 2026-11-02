# Temporary compatibility with the published kit

The standalone library still pins kit v1.22.0. That release has neither shared
head/theme-styles.html nor head/custom-icons.html nor static/brand/hub.svg.
The older theme otherwise introduces font/icon paths that do not work reliably
on the library's project subpath. The three paths in kit-compatibility.json are
therefore retained locally, byte-identical to the reviewed candidate kit.
The stylesheet pipeline itself is unchanged; the hub SVG supplies the same
shared branding in both the historically pinned and candidate builds.

This is a narrow transition record, not a waiver for arbitrary module overrides.
The product test checks exact file hashes and the historical module pin.
The updated candidate A1 gate registers only these three paths at the historical
pin. It requires the suite contract, manifest, local files and current kit
counterparts to agree, and rejects module replacements, extra paths, changed
bytes and incomplete retirement. Earlier A1 runs reported the two head shadows;
the dated integration receipt preserves that earlier checkpoint. Both module
configurations remain covered by the product integration checks.

When approved foundation publication permits the library pin to move, remove
the three listed local files and kit-compatibility.json in that same change,
then rerun strict Hugo, links, product tests and browser checks. The regression
rejects a new pin with stale compatibility copies. Do not change the public-domain
book authors or turn this product into a course to satisfy unrelated gates.
