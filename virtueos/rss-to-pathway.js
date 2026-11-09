/**
 * Turn RSS 2.0 / Atom XML into a VirtueOS pathway object.
 * Prefers <v:card> JSON when present; otherwise falls back to text cards.
 *
 * Browser-safe: no Node built-ins. CLI lives in scripts/print-pathway.js.
 */

const NS_HINT = "virtueos.org/ns/pathway";

function decodeXml(text) {
  return String(text || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => {
      const code = Number.parseInt(hex, 16);
      return Number.isFinite(code) ? String.fromCodePoint(code) : "";
    })
    .replace(/&#([0-9]+);/g, (_, dec) => {
      const code = Number.parseInt(dec, 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : "";
    })
    .replace(/&nbsp;/gi, " ")
    .replace(/&mdash;/gi, "—")
    .replace(/&ndash;/gi, "–")
    .replace(/&rsquo;/gi, "\u2019")
    .replace(/&lsquo;/gi, "\u2018")
    .replace(/&rdquo;/gi, "\u201D")
    .replace(/&ldquo;/gi, "\u201C")
    .replace(/&hellip;/gi, "…")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, "&")
    .trim();
}

/** Collapse HTML (common in RSS description / Atom content) into plain text. */
function stripHtml(html) {
  return decodeXml(html)
    .replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(p|div|h[1-6]|li|tr)>/gi, "\n")
    .replace(/<(p|div|h[1-6]|li|tr)\b[^>]*>/gi, "")
    .replace(/<[^>]+>/g, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

function firstMatch(xml, patterns) {
  for (const pattern of patterns) {
    const match = xml.match(pattern);
    if (match) return decodeXml(match[1]);
  }
  return "";
}

function sliceTags(xml, tagNames) {
  const chunks = [];
  for (const tag of tagNames) {
    const re = new RegExp(
      `<(?:[\\w.-]+:)?${tag}\\b[\\s\\S]*?<\\/(?:[\\w.-]+:)?${tag}>`,
      "gi"
    );
    let m;
    while ((m = re.exec(xml))) chunks.push(m[0]);
  }
  return chunks;
}

function attr(attrs, name) {
  const match = String(attrs || "").match(
    new RegExp(`\\b${name}=["']([^"']+)["']`, "i")
  );
  return match ? decodeXml(match[1]) : "";
}

/**
 * Prefer Atom rel="alternate", then any href link, then RSS text <link>.
 */
function pickLink(itemXml) {
  const withAttrs = [
    ...itemXml.matchAll(/<(?:[\w.-]+:)?link\b([^>]*?)(?:\/>|>([\s\S]*?)<\/(?:[\w.-]+:)?link>)/gi),
  ];

  const candidates = withAttrs.map((m) => {
    const attrs = m[1] || "";
    const href = attr(attrs, "href");
    const rel = (attr(attrs, "rel") || "alternate").toLowerCase();
    const text = decodeXml(m[2] || "").trim();
    return { href, rel, text };
  });

  const alternate = candidates.find((c) => c.href && c.rel === "alternate");
  if (alternate) return alternate.href;

  const anyHref = candidates.find((c) => c.href);
  if (anyHref) return anyHref.href;

  const textLink = candidates.find((c) => /^https?:\/\//i.test(c.text));
  return textLink ? textLink.text : "";
}

function pickItemId(itemXml, index, link) {
  const guid = firstMatch(itemXml, [
    /<(?:[\w.-]+:)?guid\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?guid>/i,
    /<(?:[\w.-]+:)?id\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?id>/i,
  ]);
  if (guid) return guid;
  if (link) return link;
  return `item-${index + 1}`;
}

function plainBody(itemXml) {
  // Prefer fuller HTML payloads, then short summaries; always strip to text.
  const raw = firstMatch(itemXml, [
    /<(?:[\w.-]+:)?encoded\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?encoded>/i,
    /<(?:[\w.-]+:)?content\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?content>/i,
    /<(?:[\w.-]+:)?description\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?description>/i,
    /<(?:[\w.-]+:)?summary\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?summary>/i,
  ]);
  return stripHtml(raw);
}

function parseCardPayload(itemXml) {
  // Match v:card / pathway:card / bare card (Virtue namespace).
  const cardTag = itemXml.match(
    /<(?:[\w.-]+:)?card\b([^>]*)>([\s\S]*?)<\/(?:[\w.-]+:)?card>/i
  );
  if (!cardTag) return null;

  const attrs = cardTag[1] || "";
  const type = attr(attrs, "type") || "text";
  const raw = decodeXml(cardTag[2]);

  try {
    const data = JSON.parse(raw);
    if (data && typeof data === "object" && !Array.isArray(data)) {
      return { type, ...data };
    }
    return { type, body: raw, title: type };
  } catch {
    return { type, body: stripHtml(raw) || raw, title: type };
  }
}

function itemToCard(itemXml, index) {
  const rich = parseCardPayload(itemXml);
  const title = stripHtml(
    firstMatch(itemXml, [
      /<(?:[\w.-]+:)?title\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?title>/i,
    ])
  );
  const description = plainBody(itemXml);
  const link = pickLink(itemXml);
  const id = pickItemId(itemXml, index, link);

  if (rich) {
    return {
      id,
      link,
      ...rich,
      type: rich.type || "text",
      title: rich.title || title || `Item ${index + 1}`,
      body: rich.body || rich.text || description || title || "Empty feed item",
      text: rich.text,
      cite: rich.cite,
      ref: rich.ref,
      question: rich.question,
    };
  }

  return {
    id,
    type: "text",
    title: title || `Item ${index + 1}`,
    body: description || title || "Empty feed item",
    link,
  };
}

function channelMeta(xml) {
  // Prefer channel/feed wrappers so item titles are not mistaken for channel title.
  const channelBlock =
    xml.match(/<channel\b[\s\S]*?<\/channel>/i)?.[0] ||
    xml.match(/<feed\b[\s\S]*?(?=<entry\b)/i)?.[0] ||
    xml;

  const title = stripHtml(
    firstMatch(channelBlock, [
      /<(?:[\w.-]+:)?title\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?title>/i,
    ])
  );
  const description = stripHtml(
    firstMatch(channelBlock, [
      /<(?:[\w.-]+:)?description\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?description>/i,
      /<(?:[\w.-]+:)?subtitle\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?subtitle>/i,
    ])
  );
  return { title, description };
}

export function rssToPathway(xml, sourceUrl = "") {
  if (!xml || !String(xml).trim()) {
    throw new Error("Empty feed document");
  }

  const { title: channelTitle, description: channelDesc } = channelMeta(xml);
  const items = sliceTags(xml, ["item", "entry"]);
  const cards = items.map((item, i) => itemToCard(item, i));

  if (!cards.length) {
    throw new Error("No <item> or <entry> elements found in feed");
  }

  const cover = {
    id: "cover",
    type: "cover",
    kicker: "VirtueOS · Imported feed",
    title: channelTitle || "Imported pathway",
    body: channelDesc || `Converted from ${sourceUrl || "feed"}`,
    cta: "Swipe up to begin",
  };

  const hasVirtueCards = /<(?:[\w.-]+:)?card\b/i.test(xml) || xml.includes(NS_HINT);

  return {
    id: "imported-feed",
    title: channelTitle || "Imported pathway",
    subtitle: sourceUrl || "Local import",
    kind: "magazine",
    sourceNote: hasVirtueCards
      ? "Feed includes VirtueOS card payloads."
      : "Plain feed — items mapped to text cards.",
    sourceUrl,
    cards: [cover, ...cards],
  };
}

