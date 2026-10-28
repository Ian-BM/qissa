# Approved Qissa branding

The wordmark uses the user-supplied **Elegant Qissa Logo with Bookish Flourish**.
The standalone Q used for SVG/favicons is the separate long-tail Q reference
explicitly confirmed by the user. The favicon does not contain the full wordmark.

- `qissa-logo.png`: transparent charcoal wordmark, 480×200.
- `qissa-logo-ivory.png`: identical geometry/alpha in ivory, 480×200.
- `qissa-mark.svg`: true vector paths for the approved standalone Q.
- `favicon.svg`: ivory Q on an obsidian tile; no fonts or embedded bitmap.
- `favicon.ico`: 16×16, 32×32 and 48×48 frames.
- `favicon-16x16.png`, `favicon-32x32.png`.
- `apple-touch-icon.png`: 180×180.
- `android-chrome-192x192.png`, `android-chrome-512x512.png`.
- `site.webmanifest`: app name, colors and icon URLs.

Both inks are rendered from one deterministic vector trace of the supplied
wordmark, preserving its spacing and book flourish. The supplied Q is traced
independently. SVG even-odd filling preserves its counters and thin tail.
No replacement font, browser image filter or invented brand mark is used.

Original sources are retained in `design/branding/`. Build-only tooling is kept
out of production dependencies. See `scripts/build_brand_assets.cjs` to rebuild
with `potrace`, `jimp` and `@resvg/resvg-js` available through `NODE_PATH`.

The shared brand/head templates apply these assets to public pages, authentication,
Premium and Studio. Logos display at 120px desktop / 105px mobile with reserved
aspect ratio. Icon and logo URLs are versioned to avoid stale browser/CDN caches.
`static/favicon.svg` is a matching compatibility alias, not the old book icon.
