# VirtueOS

Local-first reader that turns feeds into pathways.

v0 focus: **feed → pathway** works on phone and browser. Visual design is intentionally temporary.

## Product spine

1. Local reader (now)
2. Creative editor
3. Agents + Omarchy later

Brand: **VirtueOS**. First app later: **Examen**. Domain: **virtueos.org**.

## Run

```bash
npm start
```

Open `http://127.0.0.1:8765`.

- Paste an RSS/Atom URL → **Import feed**
- Or **Sample RSS** / **Stub pathway JSON**

The local server exposes `GET /api/feed?url=` so the browser can fetch remote feeds without CORS issues.

## Repo layout

```
virtueos/
  server.js           local static + feed proxy
  index.html          import screen + reader shell
  app.js              UI
  rss-to-pathway.js   RSS/Atom → pathway cards
  feeds/              sample RSS
  pathways/           stub pathway JSON
```

## Status

This tree is the VirtueOS product. It should live in its own GitHub repository (not inside Belief Protocol).
