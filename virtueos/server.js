#!/usr/bin/env node
/**
 * Minimal VirtueOS local daemon spike.
 * Serves the reader and fetches remote feeds so the browser can turn RSS/Atom into pathways.
 */
const http = require("http");
const https = require("https");
const fs = require("fs");
const path = require("path");
const { URL } = require("url");

const ROOT = __dirname;
const PORT = Number(process.env.PORT || 8765);
const HOST = process.env.HOST || "127.0.0.1";

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".webp": "image/webp",
};

function send(res, status, body, headers = {}) {
  const payload = Buffer.isBuffer(body) ? body : Buffer.from(body);
  res.writeHead(status, {
    "Content-Length": payload.length,
    ...headers,
  });
  res.end(payload);
}

function sendJson(res, status, obj) {
  send(res, status, JSON.stringify(obj, null, 2), {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
}

function safeJoin(root, reqPath) {
  const decoded = decodeURIComponent(reqPath.split("?")[0]);
  const cleaned = decoded.replace(/^\/+/, "") || "index.html";
  const full = path.normalize(path.join(root, cleaned));
  if (!full.startsWith(root)) return null;
  return full;
}

function fetchText(targetUrl, redirects = 0) {
  return new Promise((resolve, reject) => {
    let parsed;
    try {
      parsed = new URL(targetUrl);
    } catch (err) {
      reject(new Error("Invalid URL"));
      return;
    }
    if (!["http:", "https:"].includes(parsed.protocol)) {
      reject(new Error("Only http(s) feed URLs are allowed"));
      return;
    }
    const lib = parsed.protocol === "https:" ? https : http;
    const req = lib.get(
      parsed,
      {
        headers: {
          "User-Agent": "VirtueOS/0.1 (+local feed import)",
          Accept: "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        },
        timeout: 15000,
      },
      (res) => {
        if (
          res.statusCode >= 300 &&
          res.statusCode < 400 &&
          res.headers.location &&
          redirects < 5
        ) {
          const next = new URL(res.headers.location, parsed).toString();
          res.resume();
          fetchText(next, redirects + 1).then(resolve, reject);
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`Feed fetch failed (${res.statusCode})`));
          res.resume();
          return;
        }
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => {
          resolve(Buffer.concat(chunks).toString("utf8"));
        });
      }
    );
    req.on("timeout", () => {
      req.destroy(new Error("Feed fetch timed out"));
    });
    req.on("error", reject);
  });
}

function serveStatic(req, res) {
  const filePath = safeJoin(ROOT, req.url === "/" ? "/index.html" : req.url);
  if (!filePath) {
    send(res, 400, "Bad path");
    return;
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      send(res, 404, "Not found");
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    send(res, 200, data, {
      "Content-Type": MIME[ext] || "application/octet-stream",
    });
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${HOST}:${PORT}`);

  if (req.method === "GET" && url.pathname === "/api/health") {
    sendJson(res, 200, { ok: true, service: "virtueos-local", version: "0.1.0" });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/feed") {
    const feedUrl = url.searchParams.get("url");
    if (!feedUrl) {
      sendJson(res, 400, { error: "Missing url query parameter" });
      return;
    }
    try {
      const xml = await fetchText(feedUrl);
      sendJson(res, 200, {
        url: feedUrl,
        fetchedAt: new Date().toISOString(),
        xml,
      });
    } catch (err) {
      sendJson(res, 502, { error: err.message || String(err) });
    }
    return;
  }

  if (req.method !== "GET" && req.method !== "HEAD") {
    send(res, 405, "Method not allowed");
    return;
  }

  serveStatic(req, res);
});

server.listen(PORT, HOST, () => {
  console.log(`VirtueOS local reader at http://${HOST}:${PORT}`);
  console.log(`Feed import API: GET /api/feed?url=<rss-or-atom-url>`);
});
