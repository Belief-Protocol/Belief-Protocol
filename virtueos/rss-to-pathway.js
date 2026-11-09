/**
 * Turn RSS 2.0 / Atom XML into a VirtueOS pathway object.
 * Prefers <v:card> JSON when present; otherwise falls back to text cards.
 */

const NS_HINT = "virtueos.org/ns/pathway";

function decodeXml(text) {
  return String(text || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, "&")
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
    const re = new RegExp(`<(?:[\\w.-]+:)?${tag}\\b[\\s\\S]*?<\\/(?:[\\w.-]+:)?${tag}>`, "gi");
    let m;
    while ((m = re.exec(xml))) chunks.push(m[0]);
  }
  return chunks;
}

function parseCardPayload(itemXml) {
  const cardTag = itemXml.match(
    /<(?:[\w.-]+:)?card\b([^>]*)>([\s\S]*?)<\/(?:[\w.-]+:)?card>/i
  );
  if (!cardTag) return null;

  const attrs = cardTag[1] || "";
  const typeMatch = attrs.match(/\btype=["']([^"']+)["']/i);
  const type = typeMatch ? typeMatch[1] : "text";
  const raw = decodeXml(cardTag[2]);

  try {
    const data = JSON.parse(raw);
    return { type, ...data };
  } catch {
    return { type, body: raw, title: type };
  }
}

function itemToCard(itemXml, index) {
  const rich = parseCardPayload(itemXml);
  const title = firstMatch(itemXml, [
    /<(?:[\w.-]+:)?title\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?title>/i,
  ]);
  const description = firstMatch(itemXml, [
    /<(?:[\w.-]+:)?description\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?description>/i,
    /<(?:[\w.-]+:)?summary\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?summary>/i,
    /<(?:[\w.-]+:)?content\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?content>/i,
  ]);
  const link = firstMatch(itemXml, [
    /<(?:[\w.-]+:)?link\b[^>]*href=["']([^"']+)["'][^>]*\/?>/i,
    /<(?:[\w.-]+:)?link\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?link>/i,
  ]);

  if (rich) {
    return {
      id: `item-${index + 1}`,
      type: rich.type || "text",
      title: rich.title || title,
      body: rich.body || rich.text || description,
      text: rich.text,
      cite: rich.cite,
      ref: rich.ref,
      question: rich.question,
      link,
      ...rich,
    };
  }

  return {
    id: `item-${index + 1}`,
    type: "text",
    title: title || `Item ${index + 1}`,
    body: description || title || "Empty feed item",
    link,
  };
}

export function rssToPathway(xml, sourceUrl = "") {
  const channelTitle = firstMatch(xml, [
    /<channel[\s\S]*?<(?:[\w.-]+:)?title\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?title>/i,
    /<feed[\s\S]*?<(?:[\w.-]+:)?title\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?title>/i,
  ]);
  const channelDesc = firstMatch(xml, [
    /<channel[\s\S]*?<(?:[\w.-]+:)?description\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?description>/i,
    /<feed[\s\S]*?<(?:[\w.-]+:)?subtitle\b[^>]*>([\s\S]*?)<\/(?:[\w.-]+:)?subtitle>/i,
  ]);

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

  return {
    id: "imported-feed",
    title: channelTitle || "Imported pathway",
    subtitle: sourceUrl || "Local import",
    kind: "magazine",
    sourceNote: xml.includes(NS_HINT)
      ? "Feed includes VirtueOS card payloads."
      : "Plain feed — items mapped to text cards.",
    sourceUrl,
    cards: [cover, ...cards],
  };
}
