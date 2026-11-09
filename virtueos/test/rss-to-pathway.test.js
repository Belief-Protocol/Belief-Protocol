import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { rssToPathway } from "../rss-to-pathway.js";

const root = path.dirname(fileURLToPath(import.meta.url));
const feeds = path.join(root, "..", "feeds");

function load(name) {
  return fs.readFileSync(path.join(feeds, name), "utf8");
}

function assertPlainText(body, label) {
  assert.ok(body && body.length > 0, `${label} should have a body`);
  assert.equal(/<[^>]+>/.test(body), false, `${label} body should be plain text, got: ${body.slice(0, 80)}`);
}

// Virtue sample: RSS + v:card JSON
{
  const pathway = rssToPathway(load("sample-parents-ai.xml"), "sample");
  assert.equal(pathway.cards.length, 6);
  assert.deepEqual(
    pathway.cards.map((c) => c.type),
    ["cover", "text", "quote", "question", "practice", "prayer"]
  );
  assert.match(pathway.sourceNote, /VirtueOS card/);
  assert.equal(pathway.cards[2].cite.includes("Church teaching"), true);
}

// NASA RSS fixture (plain items)
{
  const pathway = rssToPathway(load("fixture-nasa-breaking.rss"), "nasa");
  assert.ok(pathway.cards.length >= 2, "NASA fixture should yield cards");
  assert.match(pathway.title, /NASA/i);
  assert.match(pathway.sourceNote, /Plain feed/);
  assertPlainText(pathway.cards[1].body, "NASA item");
  assert.ok(pathway.cards[1].link, "NASA item should keep a link");
}

// GitHub Blog Atom fixture (plain entries + HTML content)
{
  const pathway = rssToPathway(load("fixture-github-blog.atom"), "gh");
  assert.ok(pathway.cards.length >= 2, "Atom fixture should yield cards");
  assert.match(pathway.title, /GitHub/i);
  assertPlainText(pathway.cards[1].body, "Atom entry");
  assert.ok(
    /^https?:\/\//.test(pathway.cards[1].link || ""),
    "Atom entry should prefer an http(s) alternate link"
  );
  assert.ok(pathway.cards[1].id && pathway.cards[1].id !== "item-1");
  // numeric / named entities in titles and bodies should decode
  assert.equal(/&#|&[a-z]+;/i.test(pathway.cards[1].title || ""), false);
  assert.equal(/&mdash;|&rsquo;/i.test(pathway.cards[1].body || ""), false);
}

// HN RSS fixture (HTML descriptions)
{
  const pathway = rssToPathway(load("fixture-hn-frontpage.rss"), "hn");
  assert.ok(pathway.cards.length >= 2);
  assert.match(pathway.title, /Hacker News/i);
  assertPlainText(pathway.cards[1].body, "HN item");
}

// Empty / invalid
{
  assert.throws(() => rssToPathway(""), /Empty feed/);
  assert.throws(() => rssToPathway("<rss><channel></channel></rss>"), /No <item>/);
}

console.log("rss-to-pathway tests passed");
