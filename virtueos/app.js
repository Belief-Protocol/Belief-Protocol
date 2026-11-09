const pathwayUrl = new URL("./pathways/parents-church-ai.json", import.meta.url);

const feed = document.getElementById("feed");
const progress = document.getElementById("progress");
const toast = document.getElementById("toast");

let cards = [];
let activeIndex = 0;
let toastTimer;

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

function renderCard(card, index) {
  const section = document.createElement("section");
  section.className = `card ${card.type}`;
  section.dataset.index = String(index);
  section.setAttribute("aria-label", `${index + 1} of ${cards.length}`);

  const panel = document.createElement("div");
  panel.className = "card-panel";

  if (card.type === "cover") {
    panel.innerHTML = `
      <span class="kicker">${escapeHtml(card.kicker || "VirtueOS")}</span>
      <h1>${escapeHtml(card.title)}</h1>
      <p>${escapeHtml(card.body)}</p>
      <p class="cta">${escapeHtml(card.cta || "Swipe up")}</p>
    `;
  } else if (card.type === "quote") {
    panel.innerHTML = `
      <span class="badge">Quote</span>
      <blockquote>${escapeHtml(card.text)}</blockquote>
      <cite>${escapeHtml(card.cite || "")}</cite>
    `;
  } else if (card.type === "scripture") {
    panel.innerHTML = `
      <span class="badge">Scripture</span>
      <blockquote>${escapeHtml(card.text)}</blockquote>
      <p class="ref">${escapeHtml(card.ref || "")}</p>
      ${card.question ? `<p class="ask">${escapeHtml(card.question)}</p>` : ""}
    `;
  } else if (card.type === "question") {
    panel.innerHTML = `
      <span class="badge">Question</span>
      <h2>${escapeHtml(card.title)}</h2>
      <p class="ask">${escapeHtml(card.body)}</p>
    `;
  } else if (card.type === "practice") {
    panel.innerHTML = `
      <span class="badge">Practice</span>
      <h2>${escapeHtml(card.title)}</h2>
      <p>${escapeHtml(card.body)}</p>
    `;
  } else if (card.type === "prayer") {
    panel.innerHTML = `
      <span class="badge">Prayer</span>
      <h2>${escapeHtml(card.title)}</h2>
      <p>${escapeHtml(card.body)}</p>
    `;
  } else {
    panel.innerHTML = `
      <span class="badge">Reflect</span>
      <h2>${escapeHtml(card.title)}</h2>
      <p>${escapeHtml(card.body)}</p>
    `;
  }

  section.appendChild(panel);
  return section;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderProgress() {
  progress.innerHTML = cards
    .map((_, i) => `<span class="${i <= activeIndex ? "on" : ""}"></span>`)
    .join("");
  progress.setAttribute(
    "aria-valuenow",
    String(Math.round(((activeIndex + 1) / cards.length) * 100))
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
        const card = cards[activeIndex];
        const text = card?.title || card?.text || "VirtueOS pathway";
        if (navigator.share) {
          navigator.share({ title: "VirtueOS", text }).catch(() => {
            showToast("Share canceled");
          });
        } else {
          showToast("Share coming with publish");
        }
      }
    });
  });
}

async function boot() {
  const res = await fetch(pathwayUrl);
  if (!res.ok) throw new Error(`Failed to load pathway (${res.status})`);
  const pathway = await res.json();
  cards = pathway.cards || [];

  feed.innerHTML = "";
  cards.forEach((card, index) => feed.appendChild(renderCard(card, index)));
  renderProgress();
  wireRail();

  feed.addEventListener("scroll", () => syncActiveFromScroll(), { passive: true });

  // Keyboard for desktop browser testing
  window.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" || event.key === "j") {
      event.preventDefault();
      feed.querySelector(`[data-index="${Math.min(activeIndex + 1, cards.length - 1)}"]`)
        ?.scrollIntoView({ behavior: "smooth" });
    }
    if (event.key === "ArrowUp" || event.key === "k") {
      event.preventDefault();
      feed.querySelector(`[data-index="${Math.max(activeIndex - 1, 0)}"]`)
        ?.scrollIntoView({ behavior: "smooth" });
    }
  });
}

boot().catch((err) => {
  feed.innerHTML = `<section class="card"><div class="card-panel"><h2>Could not load pathway</h2><p>${escapeHtml(
    err.message
  )}</p></div></section>`;
});
