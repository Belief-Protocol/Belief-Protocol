# VirtueOS local reader (v0 spike)

Full-screen pathway reader for phone and browser.

## Design notes

- **UX:** Instagram / TikTok vertical snap feed, progress segments, action rail
- **Visual:** Stripe-like clarity (whitespace, navy ink, one accent) + Ligonier-like teaching gravity (serif for quotes/Scripture)
- **Brand:** VirtueOS; first app later is Examen (not in this spike)

## Run

```bash
cd virtueos
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765` on desktop, or your machine’s LAN IP on a phone.

## Pathway under test

`pathways/parents-church-ai.json` — placeholder cards for parents leading a family through the Church’s teaching on AI. Replace stub copy with approved citations before any partner share.
