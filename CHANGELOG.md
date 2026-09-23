# Changelog

## v1.1.0 (2026-09-23)

- Case version is now 1.1.0. The collateral cap is sized on pro forma exposure: stressed proceeds divided by 1.25x coverage, less the $50,000 accrued amount ($3,046,480 in the base case). The base recommendation stays at $3.0 million; the 30% collateral decline now rounds to $2.1 million.
- Renamed the repository to `mara-credit-case` and updated the badge, live-site, and README links.
- Added link previews to the decision view: a page title, description, Open Graph and Twitter tags, a canonical URL, and a favicon.
- Added a social card (`docs/social-card.png`) and a README screenshot (`docs/screenshot.png`).
- PDF and workbook rebuilds are now byte-identical, so a second `scripts/build_package.py` run leaves the tree clean.
- Added a weekly link check and Dependabot updates for GitHub Actions.

