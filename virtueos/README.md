# VirtueOS

Local-first reader that turns feeds into pathways.

v0 focus: **feed → pathway** works on phone and browser. Visual design is intentionally temporary.

## Product spine

1. Local reader (now)
2. Creative editor
3. Agents + Omarchy later

Brand: **VirtueOS**. First app later: **Examen**. Domain: **virtueos.org**.

Creators: Mikey (X bookmarks) + sisters (Church orders/offices).

## Run

```bash
cd virtueos
npm start
```

Open `http://127.0.0.1:8765`.

- Paste an RSS/Atom URL or raw feed XML → **Import feed**
- Or **Sample RSS** / **Stub pathway JSON**

Remote URLs are fetched in the browser. If CORS blocks a feed, paste the XML instead.

## Test

```bash
npm test
```

Offline fixtures under `feeds/`:

- `sample-parents-ai.xml` — Virtue `v:card` JSON over RSS
- `fixture-nasa-breaking.rss` — trimmed public NASA RSS
- `fixture-github-blog.atom` — trimmed public Atom
- `fixture-hn-frontpage.rss` — trimmed public HN RSS (HTML descriptions)

## Repo layout

```
virtueos/
  server.js             local static + feed proxy
  index.html            import screen + reader shell
  app.js                UI
  rss-to-pathway.js     RSS/Atom → pathway cards
  feeds/                sample + public feed fixtures
  pathways/             stub pathway JSON
  test/                 converter smoke tests
```

## Status

This tree is the VirtueOS product. It should live in its own GitHub repository (not inside Belief Protocol). Until that repo is granted to Cursor, development continues in this folder.
