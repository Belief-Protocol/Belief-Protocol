#!/usr/bin/env node
import fs from "node:fs";
import { rssToPathway } from "../rss-to-pathway.js";

const file = process.argv[2];
if (!file) {
  console.error("Usage: node scripts/print-pathway.js <feed.xml>");
  process.exit(2);
}

const pathway = rssToPathway(fs.readFileSync(file, "utf8"), file);
console.log(
  JSON.stringify(
    {
      title: pathway.title,
      sourceNote: pathway.sourceNote,
      cards: pathway.cards.length,
      types: pathway.cards.map((c) => c.type),
      firstItem: pathway.cards[1],
    },
    null,
    2
  )
);
