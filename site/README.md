# Sleeperplan Viewer

Static customer-facing WebGL showcase for Sleeperplan offer options.

## Features

- Presents 1-course, 2-course and 3-course offer variants
- Interactive 3D orbit/pan/zoom using browser WebGL
- Uses manifest camera defaults for a zoomed-out start view
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
