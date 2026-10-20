#!/usr/bin/env python3
"""
belief_build.py — package a belief for every major AI platform.

    python3 tools/belief_build.py path/to/belief-folder
    python3 tools/belief_build.py path/to/belief-folder --url https://.../BELIEF-FULL.md
    python3 tools/belief_build.py path/to/belief-folder --draft     # build without a URL, marked DRAFT

Reads   BELIEF.md (required), structures/*.md, TESTS.md (optional), SKILL.md (optional companion skill)
Writes  dist/BELIEF-SHORT.md   paste into the platform's instructions field (<= 4,000 characters)
        dist/BELIEF-FULL.md    host at the URL; attach as a file where the platform allows
        dist/<skill>/SKILL.md  only if the folder has a companion SKILL.md; carries the short belief inside it
        dist/INSTALL.md        per-platform steps and the tests that prove it's working

Fails loudly (exit 1, nothing written) when anything required is missing, when the short file
is over budget, or when an output still points at a file it doesn't contain. It never truncates.
Standard library only; Python 3.8+.
"""
import argparse
import pathlib
import re
import sys

SPEC_VERSION = "2.3"
SHORT_BUDGET = 4000          # characters, see README "Short belief file"
WARN_AT = 3600
BAD_URL_PATTERNS = [
    (r"github\.com/[^/]+/[^/]+/blob/", "a GitHub web page (…/blob/…), which models read as HTML. "
                                       "Use the raw file: raw.githubusercontent.com/…"),
    (r"docs\.google\.com|drive\.google\.com", "a Google Docs/Drive page, which most models can't open. "
                                              "Host the .md file as plain text."),
    (r"notion\.(so|site)", "a Notion page, which most models can't open. Host the .md file as plain text."),
]
CONFLICT_TEXT = {
    "reason-from-principle": "reason from the underlying principle, say that there is a conflict, and explain how you resolved it",
    "follow-instruction": "follow the explicit instruction, and note the tension if it matters",
    "surface-and-pause": "name the conflict and wait for the principal's guidance before going on",
    # deprecated aliases (README, conflict-resolution)
    "principles-over-rules": "reason from the underlying principle, say that there is a conflict, and explain how you resolved it",
    "rules-over-principles": "follow the explicit instruction, and note the tension if it matters",
}
ANOMALY_TEXT = {
    "surface": "say so, answer provisionally, and mark the answer as not settled by these beliefs",
    "resolve": "reason from the nearest core commitment and proceed",
    "defer": "do not answer; say the question is for the principal",
}

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


def section(body, title):
    """Text of a `## title` section, up to the next `## ` heading or end of file."""
    m = re.search(rf"^##\s+{re.escape(title)}\s*$", body, re.M)
    if not m:
        return None
    rest = body[m.end():]
    n = re.search(r"^##\s+\S", rest, re.M)
    return rest[: n.start() if n else len(rest)].strip()


def resolve(folder, ref):
    """Find a referenced file: as written, else by bare filename anywhere in the folder."""
    p = folder / ref
    if p.is_file():
        return p
    hits = [h for h in folder.rglob(pathlib.PurePath(ref).name) if "dist" not in h.parts]
    return hits[0] if hits else None


def demote(text, levels=1):
    return re.sub(r"^(#{1,5}) ", lambda m: "#" * (len(m.group(1)) + levels) + " ", text, flags=re.M)


# ---------- building ----------

def build_short(meta, orientations, url, draft):
    who = meta.get("author") or meta["name"]
    lines = []
    if draft:
        lines.append("DRAFT — no URL set. Do not install.\n")
    lines.append(f"# Belief: {meta['name']}")
    lines.append("")
    lines.append(f"This belief file governs everything you do here, not only tasks that mention it. {meta.get('description', '').strip()}")
    if meta.get("scope"):
        lines.append(f"\nScope: {meta['scope']}")
    cr = meta.get("conflict-resolution", "surface-and-pause")
    oa = meta.get("on-anomaly", "surface")
    lines.append(f"\nWhen a request conflicts with these beliefs: {CONFLICT_TEXT.get(cr, CONFLICT_TEXT['surface-and-pause'])}.")
    lines.append(f"When a question falls outside them: {ANOMALY_TEXT.get(oa, ANOMALY_TEXT['surface'])}.")
    if meta.get("provenance") == "reconstructed":
        lines.append("Reconstructed from the principal's public material; not yet confirmed by them.")
    lines.append("\n## Agent Orientations\n")
    lines.append(orientations.strip())
    lines.append("\n## Full belief file\n")
    lines.append(f"Full file (their own words, sources, anomalies, gaps): {url}")
    lines.append("Open it first when a question turns on a belief's wording or source, goes beyond these orientations, "
                 "or asks what the principal believes.")
    lines.append("If you need it and can't open it, say so (\"I couldn't open the full belief file; this rests on the short "
                 "version\") and mark the answer provisional. Never answer as if you had read it.")
    return "\n".join(lines).strip() + "\n"


def build_full(meta_fm, body, folder, url):
    """BELIEF.md with every structures/*.md it references inlined, so one URL fetch gets everything."""
    out = body
    referenced = sorted(set(re.findall(r"`?(structures/[\w.-]+\.md)`?", meta_fm + body)))
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
    for ref in re.findall(r"`?(structures/[\w.-]+\.md)`?", meta_fm):
        meta_fm = meta_fm.replace(ref, "inlined below")
    header = f"---\n{meta_fm.strip()}\n---\n\n<!-- Built by belief_build.py (spec {SPEC_VERSION}). Hosted at: {url} -->\n\n"
    return header + out.strip() + "\n" + "".join(appended)


def build_skill(folder, skill_text, short, meta):
    sfm, sbody = split_frontmatter(skill_text)
    sm = parse_frontmatter(sfm)
    name = sm.get("name")
    if not name:
        err("SKILL.md has no `name` in its frontmatter.")
        return None, None
    optional = r"if (loaded|available|present|installed)"
    if re.search(rf"belief[^.]{{0,160}}{optional}|{optional}[^.]{{0,160}}belief", sbody, re.I | re.S):
        err("SKILL.md treats the belief as optional (\"if loaded\" / \"if available\"). "
            "The short belief is always embedded in the built skill, so say it governs, unconditionally.")
    # inline every local file the skill points at, as appendices
    refs = sorted(set(re.findall(r"`((?:references|structures|scripts)?/?[\w.-]+\.md)`", sbody)))
    appendices = []
    for idx, ref in enumerate(refs):
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
    short_body = re.sub(r"^# Belief: .*\n+", "", short, flags=re.M)
    text = (f"---\n{sfm.strip()}\n---\n\n"
            f"<!-- Built by belief_build.py (spec {SPEC_VERSION}). Edit the sources and rebuild. -->\n\n"
            f"# Belief in force: {meta['name']}\n\n"
            f"This skill always runs under the belief below. It governs judgment; the procedure after it "
            f"says what to do. Where they disagree, the belief wins.\n\n"
            f"{demote(short_body.strip())}\n\n---\n\n"
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
                    first = re.match(r"(.{40,}?[.!?][\"\u201d']?)(\s|$)", clean)
                    clean = first.group(1) if first else clean
                    return heading, (clean[:160] + ("…" if len(clean) > 160 else ""))
    return None, None


def build_install(meta, short_len, url, orient_names, probe, tests_md, skill_name, draft):
    who = meta.get("author") or meta["name"]
    head, quote = probe
    o = []
    if draft:
        o.append("> **DRAFT.** No URL is set, so the short file points nowhere. Set `url` in BELIEF.md and rebuild before installing.\n")
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
                 f"short belief inside it. Install it where the platform has skills (Claude Skills; ChatGPT Business, "
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


def main():
    ap = argparse.ArgumentParser(description="Package a belief for every major AI platform.")
    ap.add_argument("folder", type=pathlib.Path)
    ap.add_argument("--url", help="Plain-text URL where dist/BELIEF-FULL.md will be hosted (overrides `url` in BELIEF.md).")
    ap.add_argument("--draft", action="store_true", help="Build without a URL; every output is marked DRAFT.")
    ap.add_argument("--out", type=pathlib.Path, help="Output folder (default: <folder>/dist).")
    a = ap.parse_args()

    folder = a.folder.resolve()
    bpath = folder / "BELIEF.md"
    if not bpath.is_file():
        sys.exit(f"BUILD FAILED: no BELIEF.md in {folder}")
    raw = bpath.read_text(encoding="utf-8")
    fm, body = split_frontmatter(raw)
    meta = parse_frontmatter(fm)

    for f in ("name", "description"):
        if not meta.get(f):
            err(f"BELIEF.md frontmatter is missing `{f}`.")
    if meta.get("name") and meta["name"] != folder.name:
        warn(f"Folder is \"{folder.name}\" but the belief is named \"{meta.get('name')}\"; the spec asks for them to match.")
    if "conflict-resolution" not in meta:
        warn("`conflict-resolution` isn't set; it will be treated as surface-and-pause.")

    url = a.url or meta.get("url") or (meta.get("metadata") or {}).get("url")
    draft = a.draft
    if not url:
        if draft:
            url = "(URL NOT SET — DRAFT)"
        else:
            err("No URL for the full file. Add `url:` to BELIEF.md's frontmatter or pass --url. "
                "(Use --draft to build anyway for review.)")
            url = ""
    for pat, why in BAD_URL_PATTERNS:
        if url and re.search(pat, url):
            err(f"The URL is {why}")

    orientations = section(body, "Agent Orientations")
    if not orientations:
        err("BELIEF.md has no `## Agent Orientations` section. It's required, and it's what the short file is made of.")
        orientations = ""
    orient_names = [n.rstrip(".") for n in re.findall(r"^\*\*(.+?)\*\*", orientations, re.M)]
    if len(orient_names) > 10:
        warn(f"{len(orient_names)} orientations; the compiling instructions ask for ten or fewer.")

    short = build_short(meta, orientations, url, draft) if meta.get("name") else ""
    if len(short) > SHORT_BUDGET:
        err(f"BELIEF-SHORT.md is {len(short):,} characters; the budget is {SHORT_BUDGET:,}. "
            f"Shorten the Agent Orientations or the description by {len(short) - SHORT_BUDGET:,}. "
            f"Nothing is cut automatically.")
    elif len(short) > WARN_AT:
        warn(f"BELIEF-SHORT.md is {len(short):,} characters, close to the {SHORT_BUDGET:,} budget.")

    full = build_full(fm, body, folder, url)
    probe = fetch_probe(full)

    skill_name = skill_text = None
    if (folder / "SKILL.md").is_file():
        skill_name, skill_text = build_skill(folder, (folder / "SKILL.md").read_text(encoding="utf-8"), short, meta)

    tests_md = (folder / "TESTS.md").read_text(encoding="utf-8") if (folder / "TESTS.md").is_file() else None
    if not tests_md:
        warn("No TESTS.md: Test 3 (does it change behavior?) will be empty. See README, Testing.")

    install = build_install(meta, len(short), url, orient_names, probe, tests_md, skill_name, draft)

    # every output must be self-contained: no pointers to files that aren't inside it
    outputs = {"BELIEF-SHORT.md": short, "BELIEF-FULL.md": full}
    if skill_text:
        outputs[f"{skill_name}/SKILL.md"] = skill_text
    allowed = {"BELIEF-SHORT.md", "BELIEF-FULL.md", "INVENTORY.md", "OPEN-QUESTIONS.md", "SKILL.md", "TESTS.md", "CHANGELOG.md"}
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

    out = (a.out or folder / "dist").resolve()
    out.mkdir(parents=True, exist_ok=True)
    outputs["INSTALL.md"] = install
    for oname, text in outputs.items():
        p = out / oname
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print(f"\n{'DRAFT ' if draft else ''}OK  {out}")
    print(f"  BELIEF-SHORT.md  {len(short):>7,} chars  (budget {SHORT_BUDGET:,})")
    print(f"  BELIEF-FULL.md   {len(full):>7,} chars  → host at {url}")
    if skill_text:
        print(f"  {skill_name}/SKILL.md  {len(skill_text):,} chars")
    print("  INSTALL.md       install steps + tests")
    if draft:
        print("\nDRAFT: set `url` in BELIEF.md and rebuild before installing anywhere.")
        sys.exit(2)


if __name__ == "__main__":
    main()
