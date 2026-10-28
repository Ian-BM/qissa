# Approved Qissa artwork needed

The supplied brief describes an approved Q/book-page wordmark, but no artwork
was present in the repository or task attachments. The existing text wordmark
and legacy favicon are retained temporarily; they are not the approved identity.

Add the source artwork here:

- `qissa-logo.png`: approved transparent dark wordmark for ivory surfaces.
- `qissa-logo-ivory.png`: the same approved wordmark in ivory for dark surfaces.
- `qissa-mark.svg` or a high-resolution transparent PNG: approved isolated Q motif.

Do not invent the Q shape, trace a generic font, apply image inversion filters,
or derive a generic book icon. If the Q cannot be extracted faithfully from the
supplied wordmark, obtain the approved isolated mark.

With those assets supplied, replace `templates/partials/brand.html` with the
image variants (120px desktop / 105px mobile, intrinsic dimensions, no filters).
Generate favicon.ico (16, 32, 48), favicon-16x16.png, favicon-32x32.png,
apple-touch-icon.png (180), android-chrome-192x192.png and
android-chrome-512x512.png from the approved Q, on an obsidian background.
Then replace the single legacy favicon declaration in
`templates/partials/brand_head.html` and add an accompanying web manifest.
Both public and Studio templates already include this shared head.
