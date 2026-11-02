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
The course-wide A1 checker still reports the two head shadows; its unqualified
course-fork wording does not describe this documented product transition.
New integration validation compares the copies to the actual candidate kit and
exercises both module configurations.

When approved foundation publication permits the library pin to move, remove
the three listed local files and kit-compatibility.json in that same change,
then rerun strict Hugo, links, product tests and browser checks. The regression
rejects a new pin with stale compatibility copies. Do not change the public-domain
book authors or turn this product into a course to satisfy unrelated gates.
