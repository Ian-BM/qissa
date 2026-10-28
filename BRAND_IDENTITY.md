# Qissa editorial identity

## Implementation and remaining artwork

Public pages and Studio share the Editorial Ivory / Midnight Obsidian themes.
The design uses quiet surfaces, restrained gold, literary headings, compact
story grids and comfortable reading columns. Subscription prices, payment
verification, access control, content and database models are unchanged.

**Approved logo: missing.** No approved wordmark or isolated Q artwork was found
in the repository, attachment directory, or production static/media folders.
The existing text branding is retained in a shared partial. It is not presented
as an implementation of the supplied image logo.

Required source destinations:

- `static/branding/qissa-logo.png`: approved transparent dark wordmark.
- `static/branding/qissa-logo-ivory.png`: matching ivory version.
- `static/branding/qissa-mark.svg`: approved isolated Q motif (or high-resolution PNG).

The image sizing hooks are 120px desktop / 105px mobile, with natural aspect ratio
and no filters. See `static/branding/README.md` for replacement instructions.

**New favicon family: pending artwork.** No fabricated Q or generic replacement
was generated. The existing `static/favicon.svg` remains temporarily, now linked
consistently by both base templates. Once approved Q artwork is supplied, generate
ICO (16/32/48), PNG (16/32), Apple touch (180), Android (192/512), and a manifest.
Replace the single declaration in `partials/brand_head.html`; this updates public,
authentication, Premium, reading, error and Studio pages together.

## Color and typography

| Token | Ivory | Obsidian |
| --- | --- | --- |
| Background | #F8F7F4 | #111419 |
| Surface | #FFFFFF | #1B2027 |
| Primary text | #20252C | #F4F0E8 |
| Secondary | #74777C | #A2A5AC |
| Accent | #B39260 | #D1B17A |
| Border | #E6E3DC | #30343B |

All six requested tokens are defined in `static/css/brand.css`. Small light-theme
secondary text and action labels use darker companion tones to meet contrast
requirements, while decorative gold uses the specified accent token.

Cormorant Garamond handles display and section headings, DM Sans handles interface
text and Studio, and Literata handles chapter and short-story prose. Google Fonts
uses preconnects and `display=swap`. Headings scale responsively; card titles are
14px desktop / 13px mobile, metadata 12px / 11px, and Premium prices 42px / 36px.

## Theme and reading behavior

`theme.js` runs before styles/paint and uses the existing `theme` localStorage key.
Without an explicit preference, system color preference applies. The same toggle
works across Studio, public pages and readers, persists after refresh, updates
other open tabs, and tolerates unavailable storage. There is no second theme key.

Both readers use a column no wider than 680px, Literata at 19px desktop / 18px
mobile, 1.8 line height, left-aligned text, and 1.2em paragraph spacing. Font
controls adjust between 16px and 24px and persist as `reader-font-size`. Existing
chapter links, reading progress, locking and payment entry points are retained.
The locking dialog now supports Escape, focus restoration and a keyboard trap.

All public story collections reuse the shared card partial with 160px maximum
width, 2:3 cover ratio, centered wrapping and two-line title space. Ivory lock glyphs remain legible over bright artwork and expose a Premium label to assistive technology. Two columns
fit mobile widths, including 320px. Shorts remain before long stories. Image
containers reserve cover space, including the short-story lead image.

Forms, errors, focus states, mobile navigation, management screens and charts use
shared tokens. Motion is disabled under `prefers-reduced-motion`. Error templates
retain their correct 400/403/404/500 statuses and do not expose diagnostic details.

## Static build and deployment

The browser Tailwind CDN runtime has been replaced with a committed 15KB static
utility stylesheet. Rebuild after adding utility classes:

```sh
npx tailwindcss@3.4.19 -c tailwind.config.cjs \
  -i static/css/tailwind.input.css -o static/css/utilities.css --minify
```

There are **no database migrations** in this release. Use the existing protected
server `.env` and the environment-aware `gunicorn-qissa` service. Do not enable
the competing `qissa.service`.

After saving the current commit and confirming a clean checkout:

```sh
cd /home/django_deploy/qissa
set -a
source .env
set +a
git pull --ff-only origin main
venv/bin/python manage.py check
venv/bin/python manage.py migrate --plan  # Expect no planned operations.
venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-qissa
sudo systemctl status gunicorn-qissa --no-pager -l
curl --fail --head https://getqissa.com/
```

Validate page bodies, versioned CSS/JS URLs and fonts in both themes. For an
application rollback, return to the recorded prior commit, collect its static
assets and restart Gunicorn. No database rollback is needed.

## Verification

- Django checks and JavaScript syntax checks pass.
- Complete Django suite passes on production Python 3.12: **33 tests**.
- Migration consistency check reports no changes.
- Static collection succeeds in isolated staging before production deployment.
- Chrome verified both themes at 320, 375, 768 and 1440px without horizontal overflow.
- Reader measured 678px on desktop, 19px/18px font sizes and 1.8 line height.
- Verified theme persistence, font persistence/bounds, mobile menus, chapter locking,
  dialog Escape behavior, short-story reading, and 200% CSS zoom reflow.
- axe found no WCAG A/AA violations in tested homepage, listings, authentication,
  Premium, both readers, Studio dashboard and management forms in both themes.
  These automated checks are not a claim of complete WCAG certification.
- No JavaScript errors or failed local asset responses appeared in tested flows.

## Files

New files: `static/css/{brand,dashboard,utilities,tailwind.input}.css`,
`static/js/theme.js`, `tailwind.config.cjs`, `static/branding/README.md`,
`templates/partials/{brand,brand_head,reader_controls}.html`,
`templates/{400,403,404,500}.html`, `pages/test_brand.py`, and this report.

Updated files: `static/js/qissa.js`, both base templates, public story/card/list
and reading templates, authentication/account templates, Premium/paywall templates,
Studio chapter list/Premium/home/performance templates, and `DEPLOYMENT.md`.
No settings, environment files, model definitions, migration files, stored content,
subscription service or payment logic changed.
