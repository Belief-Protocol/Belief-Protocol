import { rssToPathway } from "./rss-to-pathway.js";

const importView = document.getElementById("import");
const readerView = document.getElementById("reader");
const feed = document.getElementById("feed");
const progress = document.getElementById("progress");
const toast = document.getElementById("toast");
const statusEl = document.getElementById("import-status");
const feedUrlInput = document.getElementById("feed-url");
const feedXmlInput = document.getElementById("feed-xml");

let cards = [];
let activeIndex = 0;
let toastTimer;
let railWired = false;

function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.hidden = false;
  toast.style.display = "block";
  toast.style.opacity = "1";
  toast.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("is-visible");
    toast.style.opacity = "0";
    toastTimer = setTimeout(() => {
      toast.hidden = true;
      toast.style.display = "none";
    }, 200);
  }, 1800);
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderCard(card, index) {
  const section = document.createElement("section");
  section.className = `card ${card.type || "text"}`;
  section.dataset.index = String(index);
  section.setAttribute("aria-label", `${index + 1} of ${cards.length}`);

  const panel = document.createElement("div");
  panel.className = "card-panel";
  const type = card.type || "text";

  if (type === "cover") {
    panel.innerHTML = `
      <span class="kicker">${escapeHtml(card.kicker || "VirtueOS")}</span>
      <h1>${escapeHtml(card.title || "Pathway")}</h1>
      <p>${escapeHtml(card.body || "")}</p>
      <p class="cta">${escapeHtml(card.cta || "Swipe up")}</p>
    `;
  } else if (type === "quote") {
    panel.innerHTML = `
      <span class="badge">Quote</span>
      <blockquote>${escapeHtml(card.text || card.body || "")}</blockquote>
      <cite>${escapeHtml(card.cite || "")}</cite>
    `;
  } else if (type === "scripture") {
    panel.innerHTML = `
      <span class="badge">Scripture</span>
      <blockquote>${escapeHtml(card.text || card.body || "")}</blockquote>
      <p class="ref">${escapeHtml(card.ref || "")}</p>
      ${card.question ? `<p class="ask">${escapeHtml(card.question)}</p>` : ""}
    `;
  } else if (type === "question") {
    panel.innerHTML = `
      <span class="badge">Question</span>
      <h2>${escapeHtml(card.title || "Question")}</h2>
      <p class="ask">${escapeHtml(card.body || "")}</p>
    `;
  } else if (type === "practice") {
    panel.innerHTML = `
      <span class="badge">Practice</span>
      <h2>${escapeHtml(card.title || "Practice")}</h2>
      <p>${escapeHtml(card.body || "")}</p>
    `;
  } else if (type === "prayer") {
    panel.innerHTML = `
      <span class="badge">Prayer</span>
      <h2>${escapeHtml(card.title || "Prayer")}</h2>
      <p>${escapeHtml(card.body || "")}</p>
    `;
  } else {
    panel.innerHTML = `
      <span class="badge">Reflect</span>
      <h2>${escapeHtml(card.title || "Card")}</h2>
      <p>${escapeHtml(card.body || card.text || "")}</p>
    `;
  }

  section.appendChild(panel);
  return section;
}

function renderProgress() {
  progress.innerHTML = cards
    .map((_, i) => `<span class="${i <= activeIndex ? "on" : ""}"></span>`)
    .join("");
  progress.setAttribute(
    "aria-valuenow",
    String(Math.round(((activeIndex + 1) / Math.max(cards.length, 1)) * 100))
  );
}

function syncActiveFromScroll() {
  const mid = feed.scrollTop + feed.clientHeight / 2;
  let next = 0;
  for (const el of feed.querySelectorAll(".card")) {
    const top = el.offsetTop;
    const bottom = top + el.offsetHeight;
    if (mid >= top && mid < bottom) {
      next = Number(el.dataset.index);
      break;
    }
  }
  if (next !== activeIndex) {
    activeIndex = next;
    renderProgress();
  }
}

function wireRail() {
  if (railWired) return;
  railWired = true;
  document.querySelectorAll(".rail-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.action;
      if (action === "save") {
        btn.classList.toggle("is-on");
        showToast(btn.classList.contains("is-on") ? "Saved" : "Removed");
        return;
      }
      if (action === "note") {
        showToast("Notes come in the editor phase");
        return;
      }
      if (action === "share") {
        showToast("Share coming with publish");
      }
    });
  });
}

function showReader(pathway) {
  cards = pathway.cards || [];
  activeIndex = 0;
  feed.innerHTML = "";
  cards.forEach((card, index) => feed.appendChild(renderCard(card, index)));
  renderProgress();
  wireRail();
  feed.scrollTop = 0;

  importView.hidden = true;
  readerView.hidden = false;
  feed.focus();
}

function showImport() {
  readerView.hidden = true;
  importView.hidden = false;
}

function importFromXml(xml, sourceLabel) {
  const pathway = rssToPathway(xml, sourceLabel);
  setStatus(`Imported ${pathway.cards.length - 1} items from feed.`);
  showReader(pathway);
}

async function importFromUrl(url) {
  setStatus("Fetching feed…");
  let res;
  try {
    res = await fetch(url, {
      headers: {
        Accept: "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
      },
    });
  } catch {
    throw new Error(
      "Could not fetch that URL from the browser (often CORS). Paste the feed XML below instead."
    );
  }
  if (!res.ok) throw new Error(`Import failed (${res.status})`);
  const xml = await res.text();
  importFromXml(xml, url);
}

async function importSampleRss() {
  setStatus("Loading sample RSS…");
  const res = await fetch("./feeds/sample-parents-ai.xml");
  if (!res.ok) throw new Error("Could not load sample feed");
  const xml = await res.text();
  const pathway = rssToPathway(xml, "./feeds/sample-parents-ai.xml");
  setStatus(`Sample feed → ${pathway.cards.length - 1} cards.`);
  showReader(pathway);
}

async function importStubJson() {
  setStatus("Loading stub pathway JSON…");
  const res = await fetch("./pathways/parents-church-ai.json");
  if (!res.ok) throw new Error("Could not load stub pathway");
  const pathway = await res.json();
  setStatus(`Stub pathway → ${pathway.cards.length} cards.`);
  showReader(pathway);
}

function boot() {
  document.getElementById("btn-import").addEventListener("click", async () => {
    const xml = feedXmlInput.value.trim();
    const url = feedUrlInput.value.trim();
    try {
      if (xml) {
        importFromXml(xml, "pasted-feed");
        return;
      }
      if (!url) {
        setStatus("Paste a feed URL or feed XML first.", true);
        return;
      }
      await importFromUrl(url);
    } catch (err) {
      setStatus(err.message || String(err), true);
    }
  });

  document.getElementById("btn-sample").addEventListener("click", async () => {
    try {
      await importSampleRss();
    } catch (err) {
      setStatus(err.message || String(err), true);
    }
  });

  document.getElementById("btn-stub").addEventListener("click", async () => {
    try {
      await importStubJson();
    } catch (err) {
      setStatus(err.message || String(err), true);
    }
  });

  document.getElementById("btn-back").addEventListener("click", showImport);

  feed.addEventListener("scroll", () => syncActiveFromScroll(), { passive: true });

  window.addEventListener("keydown", (event) => {
    if (readerView.hidden) return;
    if (event.key === "ArrowDown" || event.key === "j") {
      event.preventDefault();
      feed
        .querySelector(`[data-index="${Math.min(activeIndex + 1, cards.length - 1)}"]`)
        ?.scrollIntoView({ behavior: "smooth" });
    }
    if (event.key === "ArrowUp" || event.key === "k") {
      event.preventDefault();
      feed
        .querySelector(`[data-index="${Math.max(activeIndex - 1, 0)}"]`)
        ?.scrollIntoView({ behavior: "smooth" });
    }
    if (event.key === "Escape") showImport();
  });
}

boot();
