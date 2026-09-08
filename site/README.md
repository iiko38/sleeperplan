# Sleeperplan Viewer

Static customer-facing WebGL showcase for Sleeperplan offer options.

## Features

- Presents 1-course, 2-course and 3-course offer variants
- Interactive 3D orbit/pan/zoom using browser WebGL (Z-up, vendored three.js, no CDN dependency)
- Deterministic **assembly player**: play/pause/step/scrub through the compiled
  operation schedule (`operations.json`) — receive/label/cut per board,
  place/clamp per course, mark-STOP or drill + drive per fixing. Screw insertion
  is deterministic (`head(u) = E - d*(L+g)*(1-u)`); the final frame equals the
  approved model exactly.
- Status & blockers panel showing the loaded plan's real unresolved issues
- Uses manifest camera defaults for a zoomed-out start view; batch beds render
  side by side via display-only offsets
- Links to generated docs/drawings from the same bundle

## Run locally

```sh
python -m http.server 4173
```

Open `http://localhost:4173/site/` and use the option tabs.

Optional direct option query:

```txt
http://localhost:4173/site/?offer=c1
```

## Deploy

Deploy this folder with Vercel:

```sh
vercel --prod
```
