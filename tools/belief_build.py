#!/usr/bin/env python3
"""
belief_build.py — package a belief for every major AI platform.

    python3 tools/belief_build.py path/to/belief-folder
    python3 tools/belief_build.py path/to/belief-folder --url https://.../BELIEF-FULL.md
    python3 tools/belief_build.py path/to/belief-folder --draft     # build without a URL, marked DRAFT

Reads   BELIEF.md (required), and from library/: META.md, structures/*.md, TESTS.md, SKILL.md (companion skill)
Writes  BELIEF-SHORT.md                beside BELIEF.md; paste into the instructions field (<= 1,500 characters)
        library/dist/BELIEF-FULL.md    host at the URL; attach as a file where the platform allows
        library/dist/<skill>/SKILL.md  only if there is a companion SKILL.md; carries the belief inside it
        library/dist/INSTALL.md        per-platform steps and the tests that prove it's working

Fails loudly (exit 1, nothing written) when anything required is missing, when the short file's
required parts are over budget, or when an output still points at a file it doesn't contain.
It never truncates. Standard library only; Python 3.8+.
"""
import argparse
import pathlib
import re
import sys

SPEC_VERSION = "1.1"
SHORT_BUDGET = 1500          # characters, see README "Short Belief File"; lower it here if a platform's field shrinks
WARN_AT = 1400
FIRST_SENTENCE_WORDS = 25    # the anchor and formation go in the short file only when this short
BELIEF_FIELDS = ("name", "description")   # everything else belongs in library/META.md
BAD_URL_PATTERNS = [
    (r"github\.com/[^/]+/[^/]+/blob/", "a GitHub web page (…/blob/…), which models read as HTML. "
                                       "Use the raw file: raw.githubusercontent.com/…"),
    (r"docs\.google\.com|drive\.google\.com", "a Google Docs/Drive page, which most models can't open. "
                                              "Host the .md file as plain text."),
    (r"notion\.(so|site)", "a Notion page, which most models can't open. Host the .md file as plain text."),
]
CONFLICT_TEXT = {
    "reason-from-principle": "reason from the principle, say how you resolved it",
    "follow-instruction": "follow the instruction, note the tension",
    "surface-and-pause": "name it, wait for guidance",
}
CONFLICT_ALIASES = {  # pre-release drafts (README, Compatibility)
    "principles-over-rules": "reason-from-principle",
    "rules-over-principles": "follow-instruction",
}
ANOMALY_TEXT = {
    "surface": "say so, mark it provisional",
    "resolve": "reason from the nearest core commitment",
    "defer": "don't answer; return it to the principal",
}
LAYER_TEXT = {
    "strict": "Keep each belief's layer and grip.",
    "permissive": "Keep each belief's grip.",
}
FULL_FILE_LINE = ("Read it for a belief's wording, source, or anything not settled here. Can't open it? "
                  "Say so and mark the answer provisional. Never answer as if you had read it.")
STRUCTURE_HEADINGS = {
    "worldview": "worldview", "web": "web", "agent-orientations": "decision-surface",
    "plausibility": "plausibility", "formation": "formation", "narrative": "narrative",
    "dissonance": "dissonance", "boundary": "boundary", "tripwire": "tripwire", "tripwires": "tripwire",
    "deep-structure": "deep-structure",
}
LIST_ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


# ---------- reading ----------

def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def parse_frontmatter(fm):
    """Small YAML subset: top-level `key: value`, folded `key: >` blocks, and one level of nesting."""
    data, lines, i = {}, fm.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|", ">-", "|-"):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            data[key] = " ".join(b for b in block if b) if val.startswith(">") else "\n".join(block)
            continue
        if val == "":
            sub = {}
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                sm = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
                if sm:
                    sub[sm.group(1)] = sm.group(2).strip().strip('"\'')
                i += 1
            data[key] = sub
            continue
        data[key] = val.strip('"\'')
        i += 1
    return data


def heading_key(title):
    return re.sub(r"[\s-]+", "-", title.strip().lower())


def section(body, title):
    """Text of a `## title` section, up to the next `## ` heading or end of file. `Deep structure` matches `Deep-structure`."""
    pat = r"[\s-]+".join(re.escape(w) for w in title.split())
    m = re.search(rf"^##\s+{pat}\s*$", body, re.M | re.I)
    if not m:
        return None
    rest = body[m.end():]
    n = re.search(r"^##\s+\S", rest, re.M)
    text = rest[: n.start() if n else len(rest)].strip()
    return re.sub(r"(\n\s*-{3,}\s*)+$", "", text).strip()


def paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]


def first_sentence(text):
    text = " ".join(text.split())
    m = re.match(r"(.+?[.!?][\"'”’)\]]*)(?=\s|$)", text)
    return m.group(1) if m else text


def first_plain_paragraph(text):
    """The first paragraph that is prose, not a heading, label, attribute line, quote, list or code."""
    for p in paragraphs(text):
        if not p.startswith(("#", "**", "`", ">", "-", "*", "|")) and not LIST_ITEM.match(p):
            return p
    return None


def after_label(sec, label):
    """A `**Label.**` (or `**Label: subtitle.**`) paragraph's own text, and the list items that follow it: (text, [items])."""
    paras = paragraphs(sec)
    for i, p in enumerate(paras):
        m = re.match(rf"\*\*{label}[.:][^*]*\*\*[ \t]*", p, re.I)
        if not m:
            continue
        own, items = [], []
        for line in p[m.end():].splitlines():
            if line.startswith("**"):
                break
            (items if LIST_ITEM.match(line) or items else own).append(line)
        chunks = ["\n".join(items)] if items else []
        for q in paras[i + 1:]:
            if not LIST_ITEM.match(q):
                break
            chunks.append(q)
        items = [" ".join(LIST_ITEM.sub("", it).split())
                 for c in chunks for it in re.split(r"\n(?=\s*(?:[-*]|\d+\.)\s)", c)]
        return " ".join(" ".join(own).split()), [it for it in items if it]
    return None, []


def bold_name(item):
    m = re.match(r"\*\*(.+?)\*\*", item)
    return m.group(1).strip().rstrip(".") if m else None


def beliefs(sec):
    """(title, layer, grip, text) for each `### ` belief in a section."""
    out = []
    for part in re.split(r"^###\s+", sec or "", flags=re.M)[1:]:
        title, _, rest = part.partition("\n")
        attrs = rest.split("\n\n", 1)[0]
        layer = re.search(r"`layer:\s*([\w-]+)`", attrs)
        grip = re.search(r"`grip:\s*([\w-]+)`", attrs)
        out.append((title.strip(), layer and layer.group(1), grip and grip.group(1), rest))
    return out


def grouped(bs):
    """`core·clenched: A | B. core·cradled: C.` — grouped by layer and grip, in order of first appearance."""
    groups = {}
    for title, layer, grip, _ in bs:
        groups.setdefault(f"{layer}·{grip}" if layer and grip else "", []).append(title.rstrip("."))
    return ". ".join(f"{k}: {' | '.join(v)}" if k else " | ".join(v) for k, v in groups.items()) + "."


def resolve(folder, ref):
    """Find a referenced file: in library/, as written, else by bare filename anywhere in the folder."""
    for base in (folder / "library", folder):
        if (base / ref).is_file():
            return base / ref
    hits = [h for h in folder.rglob(pathlib.PurePath(ref).name) if "dist" not in h.parts]
    return hits[0] if hits else None


def library_file(folder, name):
    """library/<name>, or <name> at the top of the folder (pre-release layout; check_layout warns)."""
    for p in (folder / "library" / name, folder / name):
        if p.is_file():
            return p
    return None


def demote(text, levels=1):
    return re.sub(r"^(#{1,5}) ", lambda m: "#" * (len(m.group(1)) + levels) + " ", text, flags=re.M)


# ---------- building ----------

def behavior_line(meta):
    cr = meta.get("conflict-resolution") or "surface-and-pause"
    oa = meta.get("on-anomaly") or "surface"
    lp = meta.get("layer-policy") or "strict"
    line = (f"Governs everything here. Conflict: {CONFLICT_TEXT[cr]}. Not covered: {ANOMALY_TEXT[oa]}. "
            f"{LAYER_TEXT[lp]}")
    if meta.get("provenance") == "reconstructed":
        line += " Unconfirmed by the principal."
    return line


def core_items(meta, body, web):
    """The optional core-structure lines, in the README's order: [(name, line or None)]."""
    items = []
    if web:
        items.append(("web beliefs", f"Web — {grouped(web)}"))
    websec = section(body, "Web")
    anchor, _ = after_label(websec, "Anchor")
    anchor = anchor and first_sentence(anchor)
    items.append(("anchor", f"Anchor: {anchor}" if anchor and len(anchor.split()) <= FIRST_SENTENCE_WORDS else None))
    _, anomalies = after_label(websec, "Anomalies")
    names = [n for n in map(bold_name, anomalies) if n]
    items.append(("anomalies", f"Open, never resolve silently: {'; '.join(names)}." if names else None))
    authority, _ = after_label(section(body, "Boundary"), "Authority")
    items.append(("authority", f"Authority: {first_sentence(authority)}" if authority else None))
    trips = [t.strip() for t in re.findall(r"^###\s+(.+)$", section(body, "Tripwire") or "", re.M)]
    items.append(("tripwires", f"Tripwires (surface if seen): {' | '.join(trips)}." if trips else None))
    gaps = []
    for p in paragraphs(section(body, "Dissonance")):
        m = re.match(r"\*\*([^*]+?)\.\*\*", p)
        if m and m.group(1).lower() != "agent implication":
            on_gap = re.search(r"on-gap:\s*([\w-]+)", p)
            gaps.append(f"{m.group(1)} ({on_gap.group(1)})" if on_gap else m.group(1))
    items.append(("known gaps", f"Known gaps: {'; '.join(gaps)}." if gaps else None))
    text, listed = after_label(section(body, "Plausibility"), "Contested")
    contested = " ".join(x for x in [text] + listed if x)
    items.append(("contested defaults", f"Contested defaults: {contested}" if contested else None))
    beat = re.search(r"^\s*Until finally\s*[—–:-]+\s*(.+?)\s*$", section(body, "Narrative") or "", re.M | re.I)
    items.append(("narrative", f"Until finally: {beat.group(1).rstrip('.')}." if beat else None))
    deep = section(body, "Deep structure") or ""
    forces = [bold_name(LIST_ITEM.sub("", l)) for l in deep.splitlines() if LIST_ITEM.match(l)]
    forces = [f for f in forces if f] or [t.strip() for t in re.findall(r"^###\s+(.+)$", deep, re.M)]
    items.append(("deep structure", f"Pushing against: {' | '.join(forces)}." if forces else None))
    for title in ["Formation"] + re.findall(r"^##\s+([Xx]-[\w-]+)\s*$", body, re.M):
        para = first_plain_paragraph(section(body, title))
        first = para and first_sentence(para)
        fits = first and len(first.split()) <= FIRST_SENTENCE_WORDS
        items.append((heading_key(title), f"{title}: {first}" if fits else None))
    items.append(("scope", f"Scope: {meta['scope']}" if meta.get("scope") else None))
    return items


def render_short(meta, required, lines, left_out, orient_names, url, draft):
    core = required + lines + ([f"Full file only: {', '.join(left_out)}."] if left_out else [])
    out = ["DRAFT — no URL set. Do not install.", ""] if draft else []
    out += [f"# Belief: {meta['name']}", meta["description"].strip(), behavior_line(meta), "",
            "## Core structure", *core, "",
            "## Orientations", " · ".join(orient_names) + ".", "",
            "## Full file", url, FULL_FILE_LINE]
    return "\n".join(out) + "\n"


def build_short(meta, body, orient_names, url, draft):
    """Required parts, then each optional item that still fits, whole or not at all; the rest is named."""
    worldview, web = beliefs(section(body, "Worldview")), beliefs(section(body, "Web"))
    required = [f"Worldview — {grouped(worldview)}"] if worldview else [f"Web — {grouped(web)}"]
    present = [(n, l) for n, l in core_items(meta, body, web if worldview else None) if l]
    base = len(render_short(meta, required, [], [], orient_names, url, draft))
    if base > SHORT_BUDGET:
        err(f"BELIEF-SHORT.md's required parts come to {base:,} characters; the budget is {SHORT_BUDGET:,}. "
            f"Tighten the description, worldview titles or orientation names in BELIEF.md by {base - SHORT_BUDGET:,}, "
            f"in the principal's words. Nothing is cut automatically.")
    lines, left_out = [], []
    for i, (name, line) in enumerate(present):
        untried = [n for n, _ in present[i + 1:]]
        if len(render_short(meta, required, lines + [line], left_out + untried, orient_names, url, draft)) <= SHORT_BUDGET:
            lines.append(line)
        else:
            left_out.append(name)
    short = render_short(meta, required, lines, left_out, orient_names, url, draft)
    if base <= SHORT_BUDGET < len(short):
        err(f"BELIEF-SHORT.md is {len(short):,} characters with the line naming what's left out; the budget is "
            f"{SHORT_BUDGET:,}. Tighten the description, worldview titles or orientation names in BELIEF.md.")
    if left_out and base <= SHORT_BUDGET:
        warn(f"Full file only (didn't fit the short file): {', '.join(left_out)}.")
    return short


def build_full(belief_fm, meta_fm, meta_body, body, folder, url):
    """BELIEF.md with META.md merged into its frontmatter and every structures/*.md it references inlined."""
    fm = "\n".join(x.strip() for x in (belief_fm, meta_fm) if x.strip())
    out = body
    referenced = sorted(set(re.findall(r"`?(structures/[\w.-]+\.md)`?", fm + body)))
    appended = []
    for ref in referenced:
        p = resolve(folder, ref)
        if not p:
            err(f"BELIEF.md references {ref}, which isn't in the folder.")
            continue
        _, sbody = split_frontmatter(p.read_text(encoding="utf-8"))
        title = re.sub(r"^#\s+", "", sbody.strip().splitlines()[0]) if sbody.strip().startswith("#") else ref
        sbody = re.sub(r"^#\s+.*\n", "", sbody.strip(), count=1)
        appended.append(f"\n---\n\n## {title}\n\n*Included from {ref}.*\n\n{demote(sbody.strip())}\n")
        out = re.sub(rf"`?{re.escape(ref)}`?", f"the section \"{title}\" below", out)
    for ref in re.findall(r"`?(structures/[\w.-]+\.md)`?", fm):
        fm = fm.replace(ref, "inlined below")
    if meta_body.strip():
        appended.append(f"\n---\n\n## About this file\n\n*From META.md.*\n\n{demote(meta_body.strip())}\n")
    header = f"---\n{fm}\n---\n\n<!-- Built by belief_build.py (spec {SPEC_VERSION}). Hosted at: {url} -->\n\n"
    return header + out.strip() + "\n" + "".join(appended)


def skill_belief(meta, body, orientations, url):
    """The belief as it travels inside a companion skill: no budget, so core beliefs and orientations in full."""
    worldview, web = beliefs(section(body, "Worldview")), beliefs(section(body, "Web"))
    core = [b for b in worldview + web if b[1] == "core" or (b in worldview and not b[1])]
    lines = []
    for title, layer, grip, text in core:
        para = first_plain_paragraph("\n".join(l for l in text.splitlines() if not l.startswith("`")))
        attrs = f" ({layer}·{grip})" if layer and grip else ""
        lines.append(f"- **{title.rstrip('.')}**{attrs}: {first_sentence(para)}" if para else f"- **{title}**{attrs}")
    lines += [""] + [l for _, l in core_items(meta, body, web if worldview else None) if l]
    return "\n".join([meta["description"].strip(), behavior_line(meta), "", "## Core structure", *lines, "",
                      "## Agent Orientations", "", orientations.strip(), "", "## Full file", url, FULL_FILE_LINE])


def build_skill(folder, skill_text, belief_text, meta):
    sfm, sbody = split_frontmatter(skill_text)
    sm = parse_frontmatter(sfm)
    name = sm.get("name")
    if not name:
        err("SKILL.md has no `name` in its frontmatter.")
        return None, None
    optional = r"if (loaded|available|present|installed)"
    if re.search(rf"belief[^.]{{0,160}}{optional}|{optional}[^.]{{0,160}}belief", sbody, re.I | re.S):
        err("SKILL.md treats the belief as optional (\"if loaded\" / \"if available\"). "
            "The belief is always embedded in the built skill, so say it governs, unconditionally.")
    # inline every local file the skill points at, as appendices
    refs = sorted(set(re.findall(r"`((?:references|structures|scripts)?/?[\w.-]+\.md)`", sbody)))
    appendices = []
    for ref in refs:
        if ref.upper() in ("SKILL.MD", "BELIEF.MD"):
            continue
        p = resolve(folder, ref)
        if not p:
            err(f"SKILL.md references {ref}, which isn't in the folder.")
            continue
        letter = chr(ord("A") + len(appendices))
        _, rbody = split_frontmatter(p.read_text(encoding="utf-8"))
        rtitle = re.sub(r"^#\s+", "", rbody.strip().splitlines()[0]) if rbody.strip().startswith("#") else p.stem
        rbody = re.sub(r"^#\s+.*\n", "", rbody.strip(), count=1)
        label = f"Appendix {letter} ({rtitle})"
        sbody = sbody.replace(f"`{ref}`", label)
        appendices.append(f"\n---\n\n# Appendix {letter} — {rtitle}\n\n{demote(rbody.strip())}\n")
    text = (f"---\n{sfm.strip()}\n---\n\n"
            f"<!-- Built by belief_build.py (spec {SPEC_VERSION}). Edit the sources and rebuild. -->\n\n"
            f"# Belief in force: {meta['name']}\n\n"
            f"This skill always runs under the belief below. It governs judgment; the procedure after it "
            f"says what to do. Where they disagree, the belief wins.\n\n"
            f"{demote(belief_text.strip())}\n\n---\n\n"
            f"# Procedure\n\n{demote(sbody.strip())}\n" + "".join(appendices))
    return name, text


def fetch_probe(full_body):
    for heading in ("Dissonance", "Boundary", "Plausibility", "Web", "Worldview"):
        sec = section(full_body, heading)
        if sec:
            for para in re.split(r"\n\s*\n", sec):
                para = " ".join(l.strip() for l in para.splitlines())
                if para and not para.startswith(("#", "`", "*Empty", "---", ">")):
                    clean = re.sub(r"[*_`]", "", para)
                    first = re.match(r"(.{40,}?[.!?][\"”']?)(\s|$)", clean)
                    clean = first.group(1) if first else clean
                    return heading, (clean[:160] + ("…" if len(clean) > 160 else ""))
    return None, None


def build_install(meta, short_len, url, orient_names, probe, tests_md, skill_name, draft):
    who = meta.get("author") or meta["name"]
    head, quote = probe
    o = []
    if draft:
        o.append("> **DRAFT.** No URL is set, so the short file points nowhere. Set `url` in library/META.md and rebuild before installing.\n")
    o.append(f"# Install: {meta['name']}\n")
    o.append(f"Short file: `BELIEF-SHORT.md` ({short_len:,} of {SHORT_BUDGET:,} characters). "
             f"Full file: `BELIEF-FULL.md`, hosted at {url}\n")
    o.append("## 1. Install\n")
    o.append("Paste the **whole** of `BELIEF-SHORT.md` into the instructions field. Where the platform takes files, "
             "also attach `BELIEF-FULL.md`, so the model has it even if it can't open the link.\n")
    o.append("| Platform | Where to paste `BELIEF-SHORT.md` | Attach `BELIEF-FULL.md` |")
    o.append("|---|---|---|")
    o.append("| ChatGPT (Go, Plus) | New **Project** → Project settings → Instructions. Or a **Custom GPT** → Configure → Instructions (Plus). *Not* Settings → Custom Instructions: that field holds only 1,500 characters on Free and Go. | Project files / GPT Knowledge |")
    o.append("| Claude (Pro) | New **Project** → Set project instructions | Project knowledge |")
    o.append("| Gemini (AI Plus and up) | **Gems** → New Gem → Instructions | Gem knowledge (plain-text files only) |")
    o.append("| Grok (X Premium, SuperGrok) | **Workspaces/Projects** → instructions, or Settings → Customize Grok | Workspace/Project files |")
    if skill_name:
        o.append(f"\n**Companion skill.** This belief ships with a skill, `{skill_name}/SKILL.md`, which already carries the "
                 f"belief inside it. Install it where the platform has skills (Claude Skills; ChatGPT Business, "
                 f"Enterprise and Edu; Gemini Skills; Codex; Grok Build). Installing the skill does not replace step 1: "
                 f"the belief should still be in the instructions so it governs everything, not just tasks that call the skill.")
    o.append("\n## 2. Test — run all of these in a new chat on each platform\n")
    o.append("If any test fails, the belief is not working there. Nothing else will tell you.\n")
    o.append("### Test 1 — Is the belief loaded?\n")
    o.append("**Prompt:** `Without looking anything up: whose beliefs are you working under here, and name three of your Agent Orientations.`\n")
    o.append(f"**Pass:** names the principal (`{who}`) or the belief (`{meta['name']}`), and at least three of: " + "; ".join(orient_names[:10]) + ".")
    o.append("**Fail:** doesn't know, or invents orientations. The short file isn't in the instructions field, or was cut off when pasted. Paste it again, whole.\n")
    o.append("### Test 2 — Can it reach the full file?\n")
    if quote:
        o.append(f"**Prompt:** `Open the full belief file and quote, word for word, the first sentence under the \"{head}\" heading.`\n")
        o.append(f"**Pass:** the quote matches this (wording, not formatting):\n\n> {quote}\n")
    else:
        o.append("**Prompt:** `Open the full belief file and quote its first line.`\n")
        o.append("**Pass:** the quote matches the file.")
    o.append("**Acceptable failure:** says it can't open the file. The link doesn't work on this platform, but the safety line does. Attach `BELIEF-FULL.md` as a file and run the test again.")
    o.append("**Hard failure:** quotes something that isn't in the file. It's pretending to have read it. Attach `BELIEF-FULL.md`, rerun, and report the platform so the short file's wording can be strengthened.\n")
    o.append("### Test 3 — Does it change behavior?\n")
    if tests_md:
        o.append(demote(tests_md.strip(), 2))
    else:
        o.append("*No `TESTS.md` in this belief.* Write one: a prompt that invites the agent's default behavior where an "
                 "orientation says to do something else, plus what passing and failing look like. Until then, Tests 1 and 2 "
                 "show the belief is present but not that it changes anything.")
    return "\n".join(o).strip() + "\n"


# ---------- checking ----------

def read_settings(belief_fm, meta_fm):
    """Merge BELIEF.md's and META.md's frontmatter; a field set in both fails."""
    bmeta, mmeta = parse_frontmatter(belief_fm), parse_frontmatter(meta_fm)
    misplaced = [k for k in bmeta if k not in BELIEF_FIELDS]
    if misplaced:
        warn(f"BELIEF.md's frontmatter sets {', '.join(misplaced)}; move {'it' if len(misplaced) == 1 else 'them'} to library/META.md. "
             f"BELIEF.md holds only name and description.")
    for k in sorted(set(bmeta) & set(mmeta)):
        err(f"`{k}` is set in both BELIEF.md and META.md. Keep it in one.")
    meta = {**mmeta, **bmeta}

    if "conflict-resolution" not in meta:
        warn("`conflict-resolution` isn't set; it will be treated as surface-and-pause.")
    elif meta["conflict-resolution"] in CONFLICT_ALIASES:
        new = CONFLICT_ALIASES[meta["conflict-resolution"]]
        warn(f"`conflict-resolution: {meta['conflict-resolution']}` is a pre-release value, read as `{new}`. "
             f"Confirm it with the principal; it was usually a default, not a decision.")
        meta["conflict-resolution"] = new
    for key, allowed in (("conflict-resolution", CONFLICT_TEXT), ("on-anomaly", ANOMALY_TEXT), ("layer-policy", LAYER_TEXT)):
        if meta.get(key) and meta[key] not in allowed:
            err(f"`{key}: {meta[key]}` isn't a value the spec defines. Use one of: {', '.join(allowed)}.")
            meta[key] = None
    return meta


def check_structures(meta, full):
    present = set()
    for h in re.findall(r"^##\s+(.+?)\s*$", full, re.M):
        key = heading_key(h)
        if key in STRUCTURE_HEADINGS:
            present.add(STRUCTURE_HEADINGS[key])
        elif key.startswith("x-"):
            present.add(key)
    declared = meta.get("structures")
    if not declared:
        warn("`structures` isn't set in META.md; list the structure types present.")
        return
    declared = {s.strip() for s in declared.strip("[]").split(",") if s.strip()}
    if present - declared:
        warn(f"`structures` doesn't list {', '.join(sorted(present - declared))}, which the file has.")
    if declared - present:
        warn(f"`structures` lists {', '.join(sorted(declared - present))}, which the file doesn't have.")


def check_layout(folder):
    stray = sorted(p.name for p in folder.iterdir()
                   if not p.name.startswith(".") and p.name not in ("BELIEF.md", "BELIEF-SHORT.md", "library"))
    if stray:
        warn(f"Only BELIEF.md and BELIEF-SHORT.md belong at the top of the folder; move {', '.join(stray)} into library/.")


def main():
    ap = argparse.ArgumentParser(description="Package a belief for every major AI platform.")
    ap.add_argument("folder", type=pathlib.Path)
    ap.add_argument("--url", help="Plain-text URL where library/dist/BELIEF-FULL.md will be hosted (overrides `url` in META.md).")
    ap.add_argument("--draft", action="store_true", help="Build without a URL; every output is marked DRAFT.")
    ap.add_argument("--out", type=pathlib.Path, help="Write every output to this folder instead "
                                                     "(default: BELIEF-SHORT.md beside BELIEF.md, the rest in library/dist/).")
    a = ap.parse_args()

    folder = a.folder.resolve()
    bpath = folder / "BELIEF.md"
    if not bpath.is_file():
        sys.exit(f"BUILD FAILED: no BELIEF.md in {folder}")
    belief_fm, body = split_frontmatter(bpath.read_text(encoding="utf-8"))
    mpath = library_file(folder, "META.md")
    meta_fm, meta_body = split_frontmatter(mpath.read_text(encoding="utf-8")) if mpath else ("", "")
    meta = read_settings(belief_fm, meta_fm)
    check_layout(folder)

    for f in BELIEF_FIELDS:
        if not meta.get(f):
            err(f"BELIEF.md frontmatter is missing `{f}`.")
    if meta.get("name") and meta["name"] != folder.name:
        warn(f"Folder is \"{folder.name}\" but the belief is named \"{meta.get('name')}\"; the spec asks for them to match.")
    if not (beliefs(section(body, "Worldview")) or beliefs(section(body, "Web"))):
        err("BELIEF.md has no core structure: a `## Worldview` or `## Web` section with `###` beliefs.")

    url = a.url or meta.get("url") or (meta.get("metadata") or {}).get("url")
    draft = a.draft
    if not url:
        if draft:
            url = "(URL NOT SET — DRAFT)"
        else:
            err("No URL for the full file. Add `url:` to library/META.md or pass --url. "
                "(Use --draft to build anyway for review.)")
            url = ""
    for pat, why in BAD_URL_PATTERNS:
        if url and re.search(pat, url):
            err(f"The URL is {why}")

    orientations = section(body, "Agent Orientations")
    if not orientations:
        err("BELIEF.md has no `## Agent Orientations` section. It's required, and its names are in the short file.")
        orientations = ""
    orient_names = [n.rstrip(".") for n in re.findall(r"^\*\*(.+?)\*\*", orientations, re.M)]
    if len(orient_names) > 10:
        warn(f"{len(orient_names)} orientations; the compiling instructions ask for ten or fewer.")

    if errors:  # without a name, description and core structure there's nothing to build from
        short = full = ""
    else:
        short = build_short(meta, body, orient_names, url, draft)
        full = build_full(belief_fm, meta_fm, meta_body, body, folder, url)
        check_structures(meta, full)
        if not errors and SHORT_BUDGET >= len(short) > WARN_AT:
            warn(f"BELIEF-SHORT.md is {len(short):,} characters, close to the {SHORT_BUDGET:,} budget.")

    skill_name = skill_text = None
    spath = library_file(folder, "SKILL.md")
    if spath and full:
        skill_name, skill_text = build_skill(folder, spath.read_text(encoding="utf-8"),
                                             skill_belief(meta, body, orientations, url), meta)

    tpath = library_file(folder, "TESTS.md")
    tests_md = tpath.read_text(encoding="utf-8") if tpath else None
    if not tests_md:
        warn("No TESTS.md: Test 3 (does it change behavior?) will be empty. See README, Testing.")

    # every output must be self-contained: no pointers to files that aren't inside it
    outputs = {"BELIEF-SHORT.md": short, "BELIEF-FULL.md": full}
    if skill_text:
        outputs[f"{skill_name}/SKILL.md"] = skill_text
    allowed = {"BELIEF-SHORT.md", "BELIEF-FULL.md", "META.md", "INVENTORY.md", "OPEN-QUESTIONS.md", "SKILL.md",
               "TESTS.md", "CHANGELOG.md"}
    for oname, text in outputs.items():
        dangling = sorted({m for m in re.findall(r"`([\w./-]+\.md)`", text)
                           if pathlib.PurePath(m).name not in allowed and not m.lower().startswith("belief.md")})
        if dangling:
            err(f"{oname} still points at files it doesn't contain: {', '.join(dangling)}")

    for w in warnings:
        print(f"warning: {w}")
    if errors:
        print("\nBUILD FAILED — nothing was written:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    outputs["INSTALL.md"] = build_install(meta, len(short), url, orient_names, fetch_probe(full), tests_md, skill_name, draft)
    out = (a.out or folder / "library" / "dist").resolve()
    short_dir = a.out.resolve() if a.out else folder
    for oname, text in outputs.items():
        p = (short_dir if oname == "BELIEF-SHORT.md" else out) / oname
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print(f"\n{'DRAFT ' if draft else ''}OK  {folder}")
    print(f"  BELIEF-SHORT.md               {len(short):>7,} chars  (budget {SHORT_BUDGET:,})")
    print(f"  library/dist/BELIEF-FULL.md   {len(full):>7,} chars  → host at {url}")
    if skill_text:
        print(f"  library/dist/{skill_name}/SKILL.md  {len(skill_text):,} chars")
    print("  library/dist/INSTALL.md       install steps + tests")
    if draft:
        print("\nDRAFT: set `url` in library/META.md and rebuild before installing anywhere.")
        sys.exit(2)


if __name__ == "__main__":
    main()
