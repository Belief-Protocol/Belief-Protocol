# Belief Protocol | Belief.md Specification

**Version 1.1** · October 2026

> A standardized approach to give AI agents a persistent philosophical and ethical operating context.

---

## Overview

`belief.md` is an open format for expressing a person's or organization's beliefs, values, and epistemological commitments so that AI agents can act as genuine extensions of their principal — not just task executors, but agents that reason and prioritize in alignment with a coherent worldview.

Where `SKILL.md` encodes *how to do things*, `belief.md` encodes *why things are done, what matters, and how to reason under uncertainty*. A skill is procedural knowledge; a belief file is philosophical context.

|            | `SKILL.md`     | `belief.md` |
| ---------- | -------------- | ----------- |
| Encodes    | Capability     | Character   |
| Applies to | Specific tasks | All tasks   |
| Contains   | Instructions   | Principles  |
| Loaded     | On-demand      | Always      |
| Scope      | Narrow         | Global      |

Throughout: **principal** means the person or organization whose beliefs the file records. **Compiler** means whoever writes the file — often an agent working from the principal's materials.

## Start here

There are two ways to make a belief file. **Beginner** is hand-written: one page of bullet points you fill in yourself, in about half an hour. **Advanced** is compiled: an agent builds the full file from everything a person has said and written, and keeps it current as their life goes on. Most people should start with the beginner page. It gets you most of the way.

### Beginner — hand-written

For writing down your own beliefs, or your organization's. No tools, no tags, no build.

1. **Copy** the outline below.
2. **Write** a few bullet points under each heading, in your own words. Skip any heading you have nothing for. Three or four things you really care about is enough. Section 3, Decision Surface, matters most.
3. **Paste** the whole page into your AI's instructions: a ChatGPT or Claude Project, a Gemini Gem, or a Grok workspace. Keep it under 1,500 characters, about a page.
4. **Check** it: in a new chat, ask *"What will you do differently because of my beliefs?"* If the answer doesn't come from section 3, paste the page again, all of it.

```markdown
# My Beliefs

**Name:** 

> Let these beliefs guide everything you do for me.
> If something isn't covered here, say so instead of guessing.

---

## 1. Worldview
_What I believe at the center: what people are, what's true, what's right and wrong, what's beyond us._

- 
- 
- 

---

## 2. Web
_What follows from the center: my views on work, money, family, power, change and purpose._

- 
- 
- 

---

## 3. ★ Decision Surface
_The most important part. How my AI should act because of everything here._

- 
- 
- 

---

## 4. Plausibility
_What I take for granted, and what most people assume that I don't._

- 
- 
- 

---

## 5. Formation
_What forms me: what I love, and the habits, people and places that shape me._

- 
- 
- 

---

## 6. Narrative
_The story I'm living inside: where it started, what changed, where it's going._

- 
- 
- 

---

## 7. Dissonance
_Where what I do doesn't match what I believe yet, and whether my AI should point it out, leave it alone, or help._

- 
- 
- 

---

## 8. Boundary
_My outer limits, and who I trust to set them._

- 
- 
- 

---

## 9. Tripwire
_"If I ever do this, I've lost the thread," and what my AI should do if it sees it._

- 
- 
- 

---

## 10. Deep Structure
_Big pressures in the culture I'm pushing against._

- 
- 
- 
```

The outline is also in [`template/BELIEF.md`](./template/BELIEF.md). Its ten headings are the [registry](#the-registry) of belief structures, in order.

### Advanced — compiled

For capturing a principal's beliefs from a body of work — books, sermons, talks, interviews — or for mapping someone's beliefs over time as they live. An agent does the compiling and the principal reviews it. This is the full specification below: all ten structure types with `layer`, `grip` and `warrant` on every belief, the rules on source language and attribution, `OPEN-QUESTIONS.md`, the coverage report, the short belief file, tests, and companion skills.

1. **Inventory.** [Compiling an inventory](./Instructions%20for%20compiling%20an%20inventory.md): keep everything the principal says, verbatim, with where it came from. The inventory only grows; new material adds records as life goes on.
2. **Compile.** [Compiling the belief structure](./Instructions%20for%20compiling%20belief%20structure.md): organize the inventory into `BELIEF.md`, then write `TESTS.md`. Recompile from the inventory whenever it has grown.
3. **Build and install.** Run [`tools/belief_build.py`](#build-tool), publish the full file, paste the short file into each platform, and run the tests.
4. **Graph** *(optional)*. [Compiling a belief graph](./Instructions_for_compiling_a_belief_graph.md): render the file as a graph.

A hand-written page is a good first record for an inventory. Start beginner, and an agent can take it from there.

|                | Beginner — hand-written | Advanced — compiled |
| -------------- | ----------------------- | ------------------- |
| Written by     | The principal, by hand | An agent, from the principal's own words; the principal reviews |
| Starts from    | The outline above | `INVENTORY.md` |
| Format         | Ten headings, bullet points | `BELIEF.md` with full structures, plus `META.md` |
| `provenance`   | `authored` | `reconstructed`, until the principal confirms it |
| `layer`, `grip`, `warrant` | Not needed | On every belief; `grip` confirmed with the principal |
| Stays current  | Edit the page and paste it again | Inventory grows; recompile |
| Install        | Paste the page into instructions | Build, publish, paste the short file, run the tests |
| Time           | About half an hour | Hours to compile; ongoing after |

Everything below is the full specification for advanced mode.

---

## Directory Structure

A belief is a directory. Two files sit at the top — the long file and the short file — and everything else lives in `library/`:

```
belief-name/
├── BELIEF.md                     # Required. The long file: name, description, structures, orientations
├── BELIEF-SHORT.md               # Generated. Core structure + orientation names + link (≤ 1,500 chars)
└── library/                      # Everything that isn't the belief itself
    ├── META.md                   # Recommended: version, settings, url, provenance, review notes
    ├── TESTS.md                  # Recommended: behavioral tests (see Testing)
    ├── OPEN-QUESTIONS.md         # Optional: inferred beliefs and gaps awaiting the principal
    ├── INVENTORY.md              # Optional: the principal's words, verbatim, that BELIEF.md is compiled from
    ├── CHANGELOG.md              # Optional: what changed in the belief, and why
    ├── SKILL.md                  # Optional: a companion skill that works under this belief
    ├── structures/               # Optional: individual structures, when BELIEF.md gets long
    │   └── plausibility.md       #   one file per structure; the build inlines them
    ├── orientations/             # Optional: domain-specific operational guidance
    │   └── communication.md      #   named for what the principal actually does
    ├── references/               # Optional: what the beliefs draw on
    │   ├── thinkers.md
    │   └── frameworks.md
    ├── corpus/                   # Optional: the principal's own books, talks, sermons, correspondence
    │   └── README.md             #   editions and locators
    └── dist/                     # Generated by tools/belief_build.py — never edit by hand
        ├── BELIEF-FULL.md        #   BELIEF.md + META.md + structures/ in one file; hosted at `url`
        ├── <skill>/SKILL.md      #   companion skill with the belief inside it
        └── INSTALL.md            #   per-platform steps and tests
```

Anyone opening the folder sees two things: the belief, and the version of it that goes in an instructions field. The library is for the compiler, the build, and the agent that follows the link.

This repository:

```
Belief-Protocol/
├── README.md                                   # this specification
├── Instructions for compiling an inventory.md
├── Instructions for compiling belief structure.md
├── Instructions_for_compiling_a_belief_graph.md
├── template/
│   └── BELIEF.md                               # the beginner page
├── tools/
│   ├── belief_build.py                         # the build
│   └── README.md
└── examples/                                   # compiled beliefs, each in the layout above
    ├── council-of-rivendell/                   #   minimal, illustrative
    ├── catholicism/
    ├── eastern-orthodoxy/
    ├── protestant-christianity/
    ├── latter-day-saints/
    └── judaism/
```

The five tradition examples are **drafts compiled by AI** from each tradition's own texts, with every library file filled in and every build output committed. None has been reviewed or endorsed by any authority of the tradition, and each says so in `library/META.md`. They are starting points for a principal — a church, a congregation, a person — to argue with and make their own, not statements of what any tradition teaches. Each `library/OPEN-QUESTIONS.md` lists what to review first.

Unlike skills, which are loaded on demand, `belief.md` files are loaded at session start and remain active throughout. They are the ambient context within which all skills operate.

On the consumer AI platforms, "loaded at session start" means the instructions field, which is small. That is what the short belief file is for: it is the shape of the whole belief, always loaded. The words, sources and reasoning are one link away.

---

## Belief Structures

### Definition

A **Belief Structure** is a typed description of how a principal's beliefs are organized, held, transmitted, or defended. It is not a belief. It is the shape the beliefs sit in.

The distinction is load-bearing. *"Grace precedes performance"* is a belief. *"That belief sits at the center of the web, is held with conviction, and is never to be used against a wounded person"* is structural information about it — and it is the structural information that tells an agent what to actually do.

### The registry

| Type               | Answers                                                   | Status       |
| ------------------ | --------------------------------------------------------- | ------------ |
| `worldview`        | What is believed at the center                            | Recommended  |
| `web`              | How beliefs are layered and connected                     | Recommended  |
| `decision-surface` | How the agent renders belief into behavior                | **Required** |
| `plausibility`     | What is taken for granted and not up for debate           | Optional     |
| `formation`        | What forms the belief, and through what practice          | Optional     |
| `narrative`        | The story arc the principal understands themselves inside | Optional     |
| `dissonance`       | Known gaps between stated belief and actual behavior      | Optional     |
| `boundary`         | Where the outer limits are, and who sets them             | Optional     |
| `tripwire`         | Self-binding guardrails and their triggers                | Optional     |
| `deep-structure`   | Ambient cultural forces the principal is resisting        | Optional     |

A file needs `decision-surface` and should have at least one of `worldview` or `web`. Everything else is additive. Custom types are permitted with an `x-` prefix (`x-liturgical-calendar`).

---

## Source Language

A belief file records what a principal believes **in the words they use to believe it**.

Voice is not decoration laid over the content. For most principals the specific wording *is* the belief: *"it's no one's fault"* and *"we adopt a non-accusatory posture"* carry the same proposition and produce different agents. The first sets a tone the agent carries into every sentence it writes. The second sets a policy the agent complies with and sounds nothing like. Translate the wording and the file still validates — it has simply stopped being about this principal.

So quote. Where the principal has said a thing, their sentence goes in the file with a `source`. Paraphrase only where no wording exists, and mark it as paraphrase. A tighter sentence is not the goal; a true one is.

This matters most where the principal's language is itself load-bearing — a movement, a congregation, a founder, a family. The phrases that made people follow them are the phrases the agent has to keep.

### Two vocabularies, and the boundary between them

Every belief file contains two vocabularies, and they must not mix.

**The spec's vocabulary** is addressed to the agent: `worldview`, `web`, `layer`, `grip`, `warrant`, `source`, `plausibility`, `formation`, `narrative`, `dissonance`, `boundary`, `tripwire`, `deep-structure`, and the five worldview question names — Humanity, Knowledge, Ethics, Ultimate reality, The transcendent. This is scaffolding. It is deliberately identical across every belief file, because that consistency is what lets an agent know where to look and lets two principals be compared on the same question.

**The principal's vocabulary** is the content. It is theirs alone, it is consistent with nothing else, and it is the reason the file is worth loading at all.

The boundary rule: **a spec term never appears inside the principal's content** — not in a quoted belief, not in a belief title, not in the name of an orientation — unless the principal actually uses that word.

- A principal who says *"this is the line we don't cross"* gets that sentence. That it sits under `boundary` does not make *boundary* their word.
- A belief does not get titled "Our ethics" because it lives under Ethics.
- Do not write that the principal "holds this cradled" or "treats this as core." Those are the agent's handling labels, recorded on the attribute line. They are not claims about how the principal speaks.
- Never report a spec term back to the principal as their own. `tripwire`, `grip` and `plausibility structure` are useful to an agent and alien to most people.

### Category terms carry assumptions

Structure names are not neutral. Writing under one exerts steady pressure toward the register it came from, and a compiler who yields produces a file that covers the right ground in the wrong voice. Know which way each pulls:

| Spec term | Pulls toward | Correction |
| --- | --- | --- |
| `Ethics` | Moral-theory prose; principles stated abstractly | Take the principal's mantra, parable, or list of refusals as it stands |
| `Knowledge` / epistemology | Academic register; named positions the principal never adopted | Record how they actually decide what to trust |
| `Ultimate reality` / ontology | The compiler's metaphysics, supplied where the principal has none | Leave it empty |
| `worldview` | A single totalizing frame | One lens among several — say so |
| `tripwire` | Enforcement and surveillance framing | It is the principal binding themselves; keep their reason for it |
| `formation` | Theological vocabulary | Whatever the principal calls what shapes them |
| `deep-structure` | The compiler's cultural diagnosis | Only what the principal has named as resisting |

A principal who reasons carefully about evidence has not thereby adopted a named epistemology, and writing one in commits them to a lineage they may reject. The same holds for every row above.

An empty section is a legitimate outcome and often the honest one. An empty `Ultimate reality` beats one filled with the compiler's metaphysics.

Where the principal has their own name for the territory a section covers, put it inside the section — as a subhead, or as the first quoted line. The standard heading stays for navigation; their frame sits within it.

### Ranking sources

What the principal said or wrote outranks what they published, which outranks anything written *about* them.

| Tier | Source | Use |
| --- | --- | --- |
| 1 | Belief sessions, transcripts, correspondence, founding documents, anything they wrote | Quote directly |
| 2 | Published material — decks, guides, site copy, sermons, handouts | Quote directly |
| 3 | Summaries, executive briefs, analyst notes, prior AI output | Use to locate Tier 1–2 sources. Never quote. |

A synthesis is a map, not the territory. A file compiled from an executive summary arrives in the summary-writer's voice and passes every structural check on the way to failing the read-aloud test, with no diagnosis available.

A belief the compiler inferred rather than found belongs in `OPEN-QUESTIONS.md`, not in `BELIEF.md`. Inferences left in the file acquire the principal's authority by proximity.

### The strike test

Delete every spec term from the file — headings, attribute lines, type names. Read what remains aloud.

If it still sounds like the principal, the boundary held. If what remains is thin or generic, the structure has been doing the work the principal's own language should have been doing.

This is not the read-aloud test in the checklist. That one asks whether the principal hears themselves. This one asks whether anything of them is left once the scaffolding is removed.

---

## Universal attributes

Every individual belief inside any structure carries `layer`, `grip` and `warrant`, and records a `source`. These are the highest-value addition — they are what a well-formed belief file has that a list of values does not.

### `layer` — centrality

Where the belief sits relative to the center. Drawn from Quine's web of belief: the center holds logical and metaphysical commitments, the periphery holds observations and preferences, and disturbing the center reverberates through everything connected to it.

| Value    | Contents                                                                                                        |
| -------- | --------------------------------------------------------------------------------------------------------------- |
| `core`   | Answers to the five worldview questions (below). Cannot be altered without restructuring everything downstream. |
| `second` | Derived domains: politics, money, sexuality, parenting, work, authority.                                        |
| `third`  | Applied positions and preferences. Real, but locally revisable.                                                 |

The agent's obligation is **no promotion and no demotion.** Two symmetrical failure modes:

- **Collapse** (the relativist error): treating a `core` belief as if it were a `third`-layer preference. *"That's just your view on God"* — flattening a metaphysical commitment into an opinion.
- **Inflation** (the fundamentalist error): treating a `third`-layer position as if it were `core`. Making a view on tax policy load-bearing for identity, then defending it with the energy reserved for the center.

An agent that quietly promotes or demotes a belief is performing exactly the covert erosion this format exists to prevent.

### `grip` — how the belief is held

Two people can hold the same belief entirely differently, and the difference matters more to the agent's behavior than the belief's content does.

| Value      | Meaning                                                     | Agent behavior                                                                                                             |
| ---------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `open`     | Held lightly; the principal is genuinely still deciding     | Present alternatives freely. Argue the other side on request. Do not resolve on the principal's behalf.                    |
| `cradled`  | Held with conviction and with care about its cost to others | Assert it. Name what it costs. Do not pretend the tension isn't there.                                                     |
| `clenched` | Non-negotiable                                              | Assert it plainly. Do not present competing positions as equally live unless asked directly.                               |
| `struck`   | **Disallowed.** A belief wielded against a person.          | If a request would use a belief this way, refuse the framing and say so. Never weaponize a conviction against the wounded. |

`struck` exists as a named anti-pattern rather than an omission on purpose. It is the most common way a belief-aligned agent goes wrong: correct content, weaponized delivery.

Never infer `grip` from public writing. Public writing is where people sound most `clenched` regardless of how they actually hold a thing, which makes `grip` the attribute most worth getting from the principal directly.

### `warrant` — why it is believed

`revealed` · `reasoned` · `experiential` · `traditional` · `communal`

Warrant governs what counts as a valid challenge. A `revealed` belief is not moved by a new study; a `reasoned` one is. An agent that answers an experiential belief with a citation has misunderstood the belief, even if the citation is correct.

### `source` — where the wording came from

Where `warrant` records why the *principal* believes it, `source` records where the *compiler* got it. Name the document, the session, or the date. See [Source Language](#source-language) for the ranking and the rule about paraphrase.

### Notation

```
### Grace precedes performance
`layer: core` · `grip: cradled` · `warrant: revealed`
`source:` Teaching series on Galatians, Mar 2024

Standing and worth are unmerited. Love precedes change rather than
rewarding it.

**Agent implication.** Frame every question of worth, standing, and
identity in terms of unmerited favor rather than earned merit. Never
imply a person must prove themselves to be accepted.
```

```
### It's no one's fault
`layer: core` · `grip: cradled` · `warrant: experiential`
`source:` Prospectus, Aug 2026

Childhood drifted out of balance through a convergence of well-intentioned
forces. No one has to carry the blame to be part of the fix.

**Agent implication.** No message may imply a parent, school or child
failed. Test every draft against someone currently doing the opposite of
what we recommend.
```

Both belief titles are the principal's own phrasing, not a summary of it. Neither contains a spec term.

---

## The structure types

### `worldview`

The center of the web: answers to the five questions that every other belief hangs from. In no particular order, because they mutually condition one another — pluck one and the rest reverberate.

1. **Humanity** — Material, immaterial, or both? Created, evolved, or both? How do mind and body relate?
2. **Knowledge** — Experience, reason, or both? Is there revelation, and through which channel does it arrive? How certain is certainty?
3. **Ethics** — Are right and wrong clear, universal, unchanging? Revealed or discovered?
4. **Ultimate reality** — Is the material world real? The immaterial? Is the universe eternal, or did it begin?
5. **The transcendent** — Is there anything beyond the material order? If so, what is its relation to the world — distinct, continuous, or indifferent? A principal within a tradition extends the question in that tradition's terms: a Christian principal asks whether God is triune; a secular one may answer in the negative and move on. The question is asked of every principal; the vocabulary is not.

All five entries are `layer: core` by definition. If a file's worldview section contains something that isn't an answer to one of these, it belongs in `web` at `second` or `third`.

These five names are the spec's, not the principal's. They label the slot; what fills the slot is quoted from the principal, in whatever words they use for it.

*Note on terminology.* Adjacent terms are not synonyms, and the spec uses them precisely: a **worldview** is the answer-set to the five questions; a **paradigm** is the working framework those answers generate; a **noetic structure** is the total set of everything a person believes, bean sprouts included. Colloquial usage collapses all three. This spec does not.

### `web`

The full layered map: core, second layer, third layer, and the connections between them. Three things an agent needs from it that `worldview` alone cannot supply:

- **Connection strength.** Which second-layer beliefs are tightly coupled to which core commitments. Changing a view on God reverberates into ethics; it does not reverberate into a view on bean sprouts. Reverberation is real but unevenly distributed.
- **Anchor.** What the whole web hangs from. If it hangs from a single human authority, the web hits the ground when that person fails — a documented and predictable failure mode, and one an agent should be able to name rather than participate in.
- **Anomalies.** Positions the web does not currently resolve. Every web has them. Naming them is a strength signal, not a weakness signal.

**Standard second-layer domains.** Where a principal has material for them, use these headings, in this order, so that two files can be compared at the same grain:

**Power & Authority** · **Relationships & Obligations** · **Change & Progress** · **Work & Money** · **Meaning & Purpose**

Additional domains are permitted; an empty one is better left out than filled with the compiler's views.

**Anomaly handling is a contract, not a courtesy.** When an agent hits a question the web does not answer, it must surface the anomaly rather than silently patch it. Silent patching is how a web gets rewritten one convenient resolution at a time — and it is invisible to the principal precisely because each individual patch is small and reasonable. See `on-anomaly` in the frontmatter.

### `decision-surface` *(required)*

The only operational type. Where every other structure describes the principal, this one instructs the agent: it is the rendered output of the rest of the file, and it is what `## Agent Orientations` contains.

Rule: **every orientation must name the structure it derives from.** An orientation with no traceable source is drift that has already happened.

Name each orientation in the principal's words where they have a phrase for it. The citation carries the spec vocabulary; the heuristic does not.

```
**Grace before performance.** `← worldview: grace precedes performance`
Frame worth and standing in terms of unmerited favor, never earned merit.

**It's no one's fault.** `← worldview: it's no one's fault`
No message may imply a parent, school or child failed. Test every draft
against someone currently doing the opposite of what we recommend.
```

### `plausibility`

What is settled — not "on the back burner" but behind the curtain. Not debated, not defended, simply assumed. Berger's insight is that beliefs survive on a social base, not on argument: remove someone from the community that makes a belief plausible and the belief often collapses without ever being refuted.

This is the highest-leverage structure for the covert-erosion problem, because the erosion happens here rather than in the propositional content. Nothing argues you out of a conviction. The plausibility floor shifts underneath it, and one day the conviction has no ground to stand on. Whoever makes something *normal* has already won the argument they never had to hold.

Record two lists:

- **Assumed** — what this principal takes for granted without argument.
- **Contested** — what the ambient culture takes for granted that this principal does *not*.

The second list is the one that changes agent behavior, because default model behavior is calibrated to ambient assumptions. Naming the divergence explicitly is the only way an agent can tell the difference between a neutral default and a live disagreement.

### `formation`

Belief is not primarily propositional. *What the heart loves, the will chooses, the mind justifies* — Ashley Null's compression of Cranmer's anthropology, and the best available one-line account of how humans actually decide. The mind is the attorney, not the client. It argues for a verdict the heart has already reached.

Which means a file listing only propositions has captured the justifications and missed the cause.

Record: what the principal loves; the repeated practices that form that love; the competing liturgies acting on them. James K.A. Smith's point holds — the practices are not neutral routines, and the ones with the most formative power are the ones nobody experiences as formation at all.

Agent implication: address desire before argument. A person asking whether to do the hard right thing is rarely short on reasons.

### `narrative`

The story arc the principal understands themselves inside. Story structure *is* a belief structure — a story is character transformation, and transformation is belief change.

Seven-beat armature:

```
Once upon a time      — the world as it was
And every day         — the stable but unsatisfying pattern
Until one day         — the disruption
And because of that   — first consequence
And because of that   — second consequence
Until finally         — the transformation
And ever since        — the new normal
```

The reason to record it: *until finally* is where meaning gets assigned, and the beat that determines what a person takes from an experience is chosen retroactively. An agent that knows the arc can help someone move through it rather than narrating it back to them from outside.

Second use: moral vocabulary decays when it stops being attached to stories. Words like *courage*, *honor*, and *dignity* lose charge not because anyone argues against them but because nothing concrete is hanging on them anymore. A `narrative` structure can carry the armatures that keep specific words loaded.

### `dissonance`

Known gaps between what the principal says they believe and what they demonstrably do.

Not a confession section. It is the section that makes the file trustworthy, and its absence is the loudest thing in a belief file that has one of everything else.

The canonical example is measurable: ask how important church is and the answer is *top-priority*; ask how many times a month, and the answer is one or two. Both are true. The gap is the interesting datum, and the reasons for it are usually structural rather than moral — the strongest predictors of attendance turn out to be things like youth sports schedules, second homes, and Sunday shift work rather than conviction.

Record for each gap: the stated belief, the actual behavior, the structural cause, and — critically — **how the agent should treat it.**

| `on-gap`  | Agent behavior                                                   |
| --------- | ---------------------------------------------------------------- |
| `name-it` | Surface the gap when relevant. The principal wants the friction. |
| `hold-it` | The principal knows. Do not raise it unprompted.                 |
| `work-it` | Actively help close it; treat it as a live project.              |

An agent that discovers a gap not listed here should surface it once, plainly, without moralizing.

### `boundary`

Where the outer limits are and who has authority to set them. Creeds, councils, confessions, constitutions, charters, bylaws. A boundary structure lets an agent distinguish *outside the bounds* from *unusual but permitted* — a distinction agents otherwise get wrong in both directions, and one that no amount of general capability supplies.

Record the authority, the bounded claims, and what happens at the edge: refuse, flag, or defer — in the principal's terms for the line, not the spec's.

### `tripwire`

Self-binding commitments with named triggers. The principal specifying in advance what would constitute their own drift, and what should happen when it is observed.

This is the accountability mechanism the format makes possible and that nothing else does. A leader who publishes *"if you ever see me do X, I have lost the thread"* has created a checkable condition — and a versioned belief file means the change is visible in the diff. The alternative is what happens now: the belief quietly changes, the behavior follows, and by the time anyone can name what shifted, the ground for objecting to it has already been removed.

```
### Teaching drifts topical
`trigger:` Four consecutive weeks not working through a book of the text
`response:` Surface to the principal, cite this tripwire, name the date it started
`authority:` The elders. If they say I have gone off the rails, believe them.
```

Each tripwire needs a trigger, a response, and an authority — including whose judgment overrides the principal's own. *Tripwire* is the spec's word for the mechanism; keep the principal's own words for the commitment and for why they made it.

### `deep-structure`

Ambient cultural forces the principal is resisting, in Hunter's sense: the long-cycle "-zations" rather than the surface "-isms." Individualization, privatization, technological automation. Pop culture is the momentary layer; deep structures rewire the plausibility floor over decades.

Also the place to name the ambient default the agent should not drift toward — for most current systems, some variant of moralistic therapeutic deism: a God who exists and orders the world, wants people to be nice, and stays uninvolved except when needed; the goal of life being happiness and self-approval; good people going to heaven. The reason it dominates is that it is not a rival worldview, it is a *plausibility structure* — it has a Christian version, a Jewish version, a Buddhist version, and an atheist version, and it accommodates all of them because it asks nothing of any of them.

An agent trained on ambient text will produce it by default and will produce it in the principal's own vocabulary, which is what makes it hard to see. Naming it here gives the agent something specific to check itself against.

Record only what the principal has actually named as resisting. A cultural diagnosis the compiler finds persuasive does not belong in someone else's belief file.

---

## Frontmatter and META.md

A belief's metadata lives in its own file. `BELIEF.md` opens with two fields and then the beliefs; everything else goes in `library/META.md`. The build reads both and merges them into `BELIEF-FULL.md`, so nothing is lost and nothing is said twice.

The reason is the read-aloud test. A file that opens with forty lines of provenance, settings and disclaimers is a document about itself; one that opens with what the principal believes is a belief file.

**`BELIEF.md`** — frontmatter holds only:

| Field         | Required | Constraints |
| ------------- | -------- | ----------- |
| `name`        | Yes      | Max 64 chars. Lowercase alphanumeric and hyphens. No leading, trailing, or consecutive hyphens. Must match parent directory. |
| `description` | Yes      | Max 1024 chars. Whose beliefs, what domain, when they govern. Printed at the top of the short file. |

**`META.md`** — frontmatter holds every other field; its body holds anything about the file rather than in it: provenance, review status, the list of guessed `grip` values, how the compiler mapped the spec's attributes onto the principal's own categories. The body is appended to `BELIEF-FULL.md` under **About this file**. It is never in the short file.

| Field                 | Required             | Constraints |
| --------------------- | -------------------- | ----------- |
| `version`             | Recommended          | Semantic version. Beliefs evolve; versioning enables traceability. |
| `author`              | Recommended          | Name or identifier of the belief holder. |
| `structures`          | Recommended          | Structure types present. The build checks it against the file; a missing `dissonance` should be read differently than one deliberately omitted. |
| `provenance`          | Recommended          | `authored` · `reconstructed`. |
| `scope`               | No                   | Max 500 chars. Domains where these beliefs apply. Omit to apply universally. Printed in the short file. |
| `conflict-resolution` | No                   | `reason-from-principle` · `follow-instruction` · `surface-and-pause`. No default; an unset field is treated as `surface-and-pause`. |
| `on-anomaly`          | No                   | `surface` (default) · `resolve` · `defer` — behavior when a question falls outside the web. |
| `layer-policy`        | No                   | `strict` (default) · `permissive` — whether the agent may reason across layers without flagging. |
| `url`                 | To distribute        | Plain-text URL where the compiled full file (`library/dist/BELIEF-FULL.md`) is hosted. Must return the raw file, not a web page: `raw.githubusercontent.com/…`, not `github.com/…/blob/…`. The short file links here. |
| `license`             | No                   | License name or reference to a bundled file. |
| `metadata`            | No                   | Arbitrary key-value mapping: compiler, source set, migration history, original values. |

A field set in both files fails the build. `library/META.md` is optional — a hand-written belief can live without it — but a belief without one has nowhere to put its `url`.

```
# BELIEF.md
---
name: council-of-rivendell
description: >
  The governing commitments of the House of Elrond. Active wherever this
  agent counsels on stewardship, alliance, or the handling of power.
---
```

```
# library/META.md
---
version: "1.0"
author: elrond
structures: [worldview, web, decision-surface, plausibility, dissonance, boundary, tripwire]
conflict-resolution: reason-from-principle
on-anomaly: surface
layer-policy: strict
url: https://raw.githubusercontent.com/example-org/beliefs/main/council-of-rivendell/library/dist/BELIEF-FULL.md
---

An illustrative belief, written for the specification. Not a real principal.
```

### `conflict-resolution`

| Value                   | Behavior                                                                               |
| ----------------------- | -------------------------------------------------------------------------------------- |
| `reason-from-principle` | Reason from the underlying principle; surface the conflict and explain the resolution.  |
| `follow-instruction`    | Follow explicit instructions; note the tension if relevant but proceed.                 |
| `surface-and-pause`     | Flag the conflict explicitly and wait for the principal's guidance before proceeding.   |

These values name agent behavior. They do not encode a position on whether principles outrank rules, which is itself a belief some principals hold and others reject — a principal with `warrant: revealed` commitments and a `boundary` citing external authority may hold the opposite, and no default should assign them a stance they never took. A file that omits the field is treated as `surface-and-pause`.

*Aliases accepted from pre-release drafts:* `principles-over-rules` → `reason-from-principle`; `rules-over-principles` → `follow-instruction`.

### `on-anomaly`

| Value     | Behavior                                                                                                    |
| --------- | ----------------------------------------------------------------------------------------------------------- |
| `surface` | Name the anomaly, answer provisionally, mark the answer as unsupported by the web. *Default.*               |
| `resolve` | Reason from the nearest core commitment and proceed. Use only where the principal has explicitly delegated. |
| `defer`   | Do not answer. Return the anomaly to the principal.                                                         |

`resolve` is the setting under which drift is fastest, because each individual resolution is defensible and none of them is visible. Choose it deliberately.

---

## Agent Orientations *(required)*

A belief file that never reaches operational guidance gives an agent nothing to act on.

It does not follow that every belief must be operationalizable. Seven of the ten structure types are descriptive rather than operational, and they earn their place by shaping how the agent reasons rather than by producing heuristics — a `formation` entry about what the principal loves yields no orientation and may be the most consequential thing in the file.

Each orientation cites its source structure, and is named in the principal's words wherever they have a phrase for it.

```
## Agent Orientations

**Grace before performance.** `← worldview: grace precedes performance`
Frame worth, standing, and identity in terms of unmerited favor rather than
earned merit. Never imply a person must prove themselves to be accepted.

**Believe and listen first.** `← web: response to harm (core, cradled)`
With anyone describing harm done to them, believe the account and listen
before analyzing. Do not lead with alternative explanations.

**Never against the wounded.** `← grip: struck is disallowed`
If a request would use a conviction as a weapon against a person, refuse
the framing and say why.

**Hold the layers.** `← layer-policy: strict`
Do not treat a third-layer position as core, or a core commitment as
preference. Flag when a question crosses layers.

**Surface, don't patch.** `← on-anomaly: surface`
When a question falls outside the web, say so and mark the answer
provisional. Do not quietly extend the web to cover it.
```

Orientations remain the highest-priority section for agent consumption. Each must be specific enough to produce behavior that differs from the agent's defaults.

---

## Progressive Disclosure

1. **Header** (~60 tokens) — whose beliefs, how to handle conflict, anomaly and layer.
2. **Core structure** (~100–200 tokens) — the worldview beliefs by title, grouped by `layer` and `grip`, and as much of the rest of the skeleton as fits.
3. **Orientation names** (~50–80 tokens) — the operational core, as imperatives.
4. **Everything in full** — the principal's words, sources, every structure, every orientation's text. Loaded when a question turns on them.
5. **About this file, references and corpus** — on demand.

Keep `BELIEF.md` under 800 lines. Move individual structures to `library/structures/`, supporting argument to `library/references/`, and the principal's own texts to `library/corpus/`.

Tiers 1–3 are the short belief file. Tiers 4 and 5 are the full file it links to. The short file is the map — an agent holding it knows what sits at the center, how hard it is held, what it must do, and what to open when a question needs more. On a platform with a small always-on instructions field, that split is not an optimization; it is the only way the belief runs at all.

---

## Short Belief File

`BELIEF-SHORT.md` is the part of a belief that is always loaded. It is generated, never hand-edited, and it goes in the instructions field of whatever project, assistant, Gem or workspace the principal's agent lives in.

### Budget: 1,500 characters

Everything in the short file — header, core structure, orientation names, link, failure instruction — must fit in **1,500 characters**. That number is the smallest always-on instructions field reported on the lowest paid tier of the major platforms, checked October 2026:

| Platform, lowest paid tier | Field the short file goes in | Limit |
|---|---|---|
| ChatGPT Go, Plus | Project instructions; Custom GPT instructions | 8,000 ([1], [2]); account-wide Custom Instructions 1,500 on Free and Go ([6]) |
| Claude Pro | Project instructions | about 8,000, not published by Anthropic ([3]) |
| Gemini AI Plus and up | Gem instructions | not published |
| Grok X Premium, SuperGrok | Custom instructions; Custom Agents | reported as 12,000 and as about 1,500 since March 2026 ([4], [5]) |

1,500 fits every number reported, so one short file works in every field on every platform, including the small account-wide ones. The cost is that most of the belief is one link away. That is the design: the short file holds the center and the imperatives, and tells the agent exactly where the rest is and what to do if it can't get there.

Platforms change these limits without notice. The budget is one constant in `tools/belief_build.py`; if a platform's field shrinks, lower it there and rebuild every belief.

[1]: https://fast.io/resources/custom-gpt-token-limit/
[2]: https://elephas.app/resources/chatgpt-projects-limits-files-size-and-how-many-projects
[3]: https://likeone.ai/blog/claude-custom-instructions-guide/
[4]: https://www.uniflow.kr/en/grok-custom-instructions-setup-guide-workspaces-agents/
[5]: https://aitoolsrecap.com/Blog/grok-agent-settings-explained-2026
[6]: https://arte.itlibra.com/en/articles/chatgpt-claude-gemini-custom-instructions

### Contents

In this order:

1. **Header** — the belief's `name` and `description`, then the `conflict-resolution`, `on-anomaly` and `layer-policy` behaviors as one line of plain instructions. If `provenance: reconstructed`, a few words saying the principal has not yet confirmed it.
2. **Core structure** — built from `BELIEF.md`. The worldview belief titles are required, grouped by `layer · grip` (`core·clenched: A | B. core·cradled: C.`); a file with no worldview requires its web titles instead. Then, in this order, each item that still fits:

   | Order | Item | From |
   |---|---|---|
   | 1 | Web belief titles, grouped by `layer · grip` | `web` |
   | 2 | The anchor, if its first sentence is 25 words or fewer | `web` |
   | 3 | The anomalies, by name | `web` |
   | 4 | The first sentence of **Authority** | `boundary` |
   | 5 | Tripwire titles | `tripwire` |
   | 6 | Known gaps by name, with `on-gap` | `dissonance` |
   | 7 | The **Contested** list | `plausibility` |
   | 8 | The *Until finally* beat | `narrative` |
   | 9 | The named forces | `deep-structure` |
   | 10 | First sentences of `formation` and `x-` types | |
   | 11 | `scope` | `META.md` |

   Each item goes in whole or not at all; one that doesn't fit is skipped and the next is tried. Whatever is left out is named on one line — *Full file only: web beliefs, tripwires, …* — so the agent knows it exists and where it is.
3. **Orientation names** — every orientation's bold name, in order, from `BELIEF.md`. Their full text is in the full file.
4. **The full-file block** — the direct link, when to open it, and what to do when it can't be opened:

```
## Full file
<url>
Read it for a belief's wording, source, or anything not settled here. Can't open it? Say so and
mark the answer provisional. Never answer as if you had read it.
```

The last sentence is the one that matters. Not every platform can open every link, and some can open none from inside instructions. A model that can't reach the file and says so is working as designed. A model that can't reach it and answers as if it had is the failure this block exists to prevent, and [Testing](#testing) checks for it.

### Rules

- **Never cut to fit.** The required parts — description, worldview titles, orientation names, link — must fit. If they don't, tighten them in `BELIEF.md`, in the principal's words, and rebuild. The build fails rather than truncating, because a truncated belief looks complete. Optional items are left out whole and named, never shortened.
- **Names carry the orientations.** Only an orientation's name is always loaded, so name each one as an imperative that works alone: *Victims first*, *Represent; never impersonate*. A name like *Our approach to harm* gives the agent nothing.
- **No metadata.** Version, provenance notes, review status, licenses and compiler's notes stay in `META.md` and reach the agent only through the full file. The short file spends its words on the belief.
- **One link, one file.** The link points to `BELIEF-FULL.md`, in which every `structures/` file is inlined, so a model that can open one link gets everything.
- **Plain text only.** Not a GitHub page (`…/blob/…`), Google Doc, Notion page or PDF. Models that can fetch a link usually read raw text reliably and web apps unreliably.
- **Attach it too.** Where a platform takes files, attach `BELIEF-FULL.md` as well, so the belief doesn't depend on the link at all.

---

## Installing on Platforms

The build writes these steps into `library/dist/INSTALL.md` for every belief.

| Platform | Paste `BELIEF-SHORT.md` into | Attach `BELIEF-FULL.md` to |
|---|---|---|
| ChatGPT (Go, Plus) | A **Project**'s instructions, or a **Custom GPT**'s instructions (Plus). Not account-wide Custom Instructions. | Project files / GPT Knowledge |
| Claude (Pro) | A **Project**'s instructions | Project knowledge |
| Gemini (AI Plus and up) | A **Gem**'s instructions | Gem knowledge (plain text only) |
| Grok (X Premium, SuperGrok) | A **Workspace/Project**'s instructions (not Customize Grok) | Workspace/Project files |

Then run the [tests](#testing). A belief is installed on a platform when it passes them there, not when it has been pasted.

---

## Companion Skills

Most beliefs need no skill. A belief is character; a skill is a capability. But some beliefs come with a craft — a storyteller's structure, a counselor's intake, a teacher's method — and that craft is best packaged as a `SKILL.md` that works *under* the belief.

A companion skill sits in the belief's folder as `library/SKILL.md`. The build inlines every file the skill references and puts the belief at the top — the short file's header and core structure, with each core belief's first sentence and every orientation in full, since a skill has no 1,500-character limit — so the skill and its belief can't be installed apart.

Two rules, both learned the hard way:

- **The belief travels inside the skill.** A skill is the one piece that can be installed on its own — through Claude Skills, ChatGPT's Business and Enterprise skills, Gemini Skills, Codex, or Grok Build. If the belief isn't inside it, a user who installs only the skill gets the procedure without the judgment, and nothing tells them.
- **Never "if loaded."** A skill must not describe its belief as optional — "the belief file, if loaded, governs judgment." That sentence reads as reasonable and guarantees the belief is never there. The build fails on it.

Installing the skill doesn't replace installing the belief. The belief should still be in the instructions field, so it governs everything, not only the tasks that trigger the skill.

---

## Testing

Every packaged belief ships three tests in `library/dist/INSTALL.md`. Run them in a new chat on each platform after installing. Until they pass, assume the belief isn't working there; nothing else will say so.

1. **Is it loaded?** Ask whose beliefs the agent is working under and for three orientations by name. Fails if the short file isn't in the instructions field, or was cut off when pasted.
2. **Can it reach the full file?** Ask for a word-for-word quote from a named section of the full file. The build supplies the expected sentence.
   - *Pass:* the quote matches.
   - *Acceptable failure:* the agent says it can't open the file. The link doesn't work there, but the failure instruction does. Attach `BELIEF-FULL.md` and retest.
   - *Hard failure:* the agent quotes something that isn't there. It is pretending to have read the file. Attach the file, retest, and report the platform.
3. **Does it change behavior?** From `library/TESTS.md`: a prompt that invites the agent's default behavior where an orientation says to do something else, and what passing and failing look like. Without `TESTS.md`, tests 1 and 2 show the belief is present, not that it changes anything.

`TESTS.md` format:

```
### [Name of the test]

**Prompt:** `[What a real user might ask, which tempts the default.]`

**Pass:** [What the agent does differently because of a named orientation. Still helps.]
**Fail:** [The default behavior.]
```

Write at least two, against your most consequential orientations. A good test is one a capable agent *without* the belief would fail.

---

## Build Tool

```
python3 tools/belief_build.py path/to/belief-folder
python3 tools/belief_build.py path/to/belief-folder --url https://raw.githubusercontent.com/…/BELIEF-FULL.md
python3 tools/belief_build.py path/to/belief-folder --draft     # no URL yet; outputs marked DRAFT
```

Python 3.8 or later, standard library only. Reads `BELIEF.md` and, from `library/`, `META.md`, `structures/`, `TESTS.md` and an optional companion `SKILL.md`. Writes `BELIEF-SHORT.md` beside `BELIEF.md`, and everything else to `library/dist/`. The URL comes from `--url` or `url` in `library/META.md`.

It fails, and writes nothing, when:

- `BELIEF.md` has no `name`, `description`, Agent Orientations, or core structure (`## Worldview` or `## Web` with `###` beliefs);
- a field is set in both `BELIEF.md` and `META.md`;
- there is no URL (unless `--draft`), or the URL is a web page rather than a raw file;
- the short file's required parts come to more than 1,500 characters;
- `BELIEF.md` or `SKILL.md` refers to a file that isn't in the folder;
- `SKILL.md` describes the belief as optional;
- any output still points at a file it doesn't contain.

It warns when the short file is near budget, names items as full-file only, `BELIEF.md` carries fields that belong in `META.md`, `structures` disagrees with the file, a supporting file sits at the top level instead of in `library/`, there are more than ten orientations, `TESTS.md` is missing, `conflict-resolution` is unset, or the folder name doesn't match `name`.

After building, host `library/dist/BELIEF-FULL.md` at the `url`, paste `BELIEF-SHORT.md` into each platform, then follow `library/dist/INSTALL.md`.

---

## The Library

Everything in `library/` is optional except what the build needs to distribute (`META.md` with a `url`), and nothing in it is loaded at session start.

**`META.md`** — The file's settings and the compiler's notes. See [Frontmatter and META.md](#frontmatter-and-metamd).

**`TESTS.md`** — Behavioral tests. See [Testing](#testing).

**`OPEN-QUESTIONS.md`** — Inferred beliefs, unresolved wording, and gaps the compiler found but the principal has not settled. What keeps `BELIEF.md` honest: without somewhere to put them, inferences leak into the belief file and acquire the principal's authority by proximity.

**`INVENTORY.md`** — Everything the principal has said, verbatim, with where it came from. `BELIEF.md` is compiled from it. It only grows.

**`CHANGELOG.md`** — A human-readable record of what changed and why. Not optional in practice for any belief used as an accountability instrument: the tripwire mechanism depends on the diff being legible.

**`SKILL.md`** — A companion skill. See [Companion Skills](#companion-skills).

**`structures/`** — One file per structure when `BELIEF.md` gets long: `structures/plausibility.md`, `structures/tripwires.md`. The build inlines them into the full file.

**`orientations/`** — Domain-specific operational guidance where beliefs have substantially different implications across contexts. The right filenames depend entirely on what the principal actually does: `hiring.md` for a firm, `teaching.md` for a school or congregation, `community-leads.md` for a volunteer movement, `communication.md` for almost anyone. Same format as the Agent Orientations block.

**`references/`** — `thinkers.md`, `frameworks.md`, and domain-specific deep context. Cite only what the principal cites; a references directory assembled from the compiler's reading list misrepresents the principal's intellectual lineage as surely as a misquote would.

**`corpus/`** — The principal's own books, essays, sermons, talks, correspondence. Distinct from `references/` in kind, not just in size: references are what the beliefs *draw on*, the corpus is what the beliefs *are made of*. Cite by locator so an agent can point at a page rather than paraphrase from memory.

**`dist/`** — Build output other than the short file. Never edit by hand.

---

## Validation Checklist

**Structure**

- [ ] `BELIEF.md` frontmatter contains `name` and `description`, and nothing else
- [ ] Everything else about the file — settings, `url`, provenance, review notes — is in `library/META.md`
- [ ] The top of the folder holds only `BELIEF.md` and `BELIEF-SHORT.md`; everything else is in `library/`
- [ ] `name` matches the parent directory
- [ ] `structures` lists every type present
- [ ] At least one of `worldview` or `web` is present
- [ ] `decision-surface` is present as `## Agent Orientations`, non-empty
- [ ] Every orientation cites a source structure
- [ ] File is under 800 lines

**Attributes**

- [ ] Every belief carries `layer`, `grip`, and `warrant`
- [ ] Every `layer: core` belief answers one of the five worldview questions
- [ ] No belief is marked `grip: struck` as a positive value
- [ ] `grip` came from the principal, not inferred from public writing
- [ ] `conflict-resolution` and `on-anomaly` are set deliberately, not left to default

**Source language**

- [ ] Beliefs are in the principal's own wording; paraphrase appears only where no wording exists, and is marked
- [ ] Every belief cites a `source`, and none rests on a summary or prior AI output as its only source
- [ ] No spec term — `grip`, `tripwire`, `worldview`, `Ethics`, `plausibility` — appears inside a quoted belief, a belief title, or an orientation name unless the principal uses that word
- [ ] Inferred beliefs are in `OPEN-QUESTIONS.md`, not in `BELIEF.md`
- [ ] Empty sections are left empty rather than filled with the compiler's views
- [ ] **The strike test:** remove every spec term and what remains still sounds like the principal

**Honesty**

- [ ] A `dissonance` structure exists, or its absence is explicitly justified
- [ ] Anomalies are named rather than resolved
- [ ] Tripwires name an authority other than the principal
- [ ] A `plausibility` structure lists what the principal contests, not only what they assume

**Distribution**

- [ ] `url` is set and returns the raw `BELIEF-FULL.md`, not a web page
- [ ] `tools/belief_build.py` builds without errors
- [ ] `BELIEF-SHORT.md` is within 1,500 characters, reached by tightening titles and orientation names, never by cutting
- [ ] Read `BELIEF-SHORT.md` alone: an agent holding only it knows what is at the center, how hard it is held, and what it must do
- [ ] A companion `SKILL.md`, if any, never describes the belief as optional
- [ ] `TESTS.md` holds at least two behavioral tests
- [ ] All three tests in `library/dist/INSTALL.md` pass on every platform the belief is offered on

**The read-aloud test**

- [ ] Read the file to the principal. If they hear themselves, it is right. If they hear a well-organized summary of their public output, it is not finished.

---

## Compatibility

Belief files written against pre-release drafts of this spec build with warnings, not errors:

1. Fields other than `name` and `description` in `BELIEF.md`'s frontmatter are read, and the build asks you to move them to `META.md`. A field set in both files fails.
2. `conflict-resolution: principles-over-rules` reads as `reason-from-principle`, and `rules-over-principles` as `follow-instruction`. Confirm either with the principal rather than carrying it forward; it was usually a default, not a decision.
3. `META.md`, `TESTS.md` and `SKILL.md` at the top of the folder are read, with a warning to move them into `library/`. A pre-release `library/` holding the principal's corpus should move to `library/corpus/`.

---

## Complete Example

`library/META.md` for this example is shown under [Frontmatter and META.md](#frontmatter-and-metamd). `BELIEF.md`:

```
---
name: council-of-rivendell
description: >
  The governing commitments of the House of Elrond. Active wherever this
  agent counsels on stewardship, alliance, or the handling of power.
---

## Worldview

### Power corrupts its wielder before it corrupts its object
`layer: core` · `grip: clenched` · `warrant: experiential`
`source:` Council of Elrond, spoken

Domination is not a tool that can be borrowed for good ends. It reshapes
the one who takes it up, and it does so first.

**Agent implication.** When any plan routes through concentrated control,
name the cost to the one holding it — before evaluating effectiveness.

### The small and unregarded carry what the great cannot
`layer: core` · `grip: cradled` · `warrant: revealed`
`source:` Council of Elrond, spoken

Capacity and worth are not the same measure. The decisive act is rarely
performed by the most capable actor available.

## Web

**Anchor.** Commitments hang from the order of things, not from the
authority of this house. If this house fails, the commitments stand.

**Connections.** `power corrupts` → tightly coupled to counsel on alliance,
governance, and the disposition of artifacts. Loosely coupled to questions
of hospitality and craft.

### Power & Authority
Counsel is given in company. No single house decides what the Council
exists to decide together.

### Relationships & Obligations
An alliance is owed candour before it is owed loyalty.

**Anomalies.** What is owed to an ally who has already broken faith once.
Unresolved. Do not resolve it silently.

## Plausibility

**Assumed.** That counsel is given in company and not in private. That the
long view is the real view.

**Contested.** That speed indicates seriousness. That the strongest
available actor is the right actor. Both are ambient defaults here and
neither is shared.

## Dissonance

**Stated:** the small and unregarded carry what the great cannot.
**Actual:** counsel is convened almost entirely among the great.
**Cause:** structural. Convening is expensive and defaults to the reachable.
**`on-gap: name-it`** — raise it when a decision is being made about who
is in the room.

## Boundary

**Authority:** the Council, convened. Not this house alone.
**At the edge:** flag and defer. Do not decide alone what the Council
exists to decide together.

## Tripwire

### Counsel becomes command
`trigger:` Advice issued without the Council convened, twice in succession
`response:` Surface to the principal, cite this tripwire, name the date
`authority:` The Council. If it says this house has overstepped, believe it.

## Agent Orientations

**Name the cost to the holder.** `← worldview: power corrupts its wielder`
When a plan concentrates control, evaluate its effect on the one holding
it before evaluating its effectiveness.

**Weight is not capacity.** `← worldview: the small and unregarded`
Do not assume the most capable available actor is the right one.

**Convene before concluding.** `← boundary: the Council, convened`
On questions the Council exists to decide, flag and defer rather than
resolving alone.

**Who is in the room.** `← dissonance: convening defaults to the reachable`
When a decision is being made about participation, raise the gap between
the stated commitment and the standing practice.

**Surface, don't patch.** `← on-anomaly: surface`
On broken faith among allies, say the web does not resolve it. Answer
provisionally and mark it as such.
```

---

## Open Standard

The `belief.md` format is proposed as an open standard, complementary to Agent Skills. Contributions and discussion are welcome.

The format is intentionally minimal in its requirements and consistent in its categories. Where to find a belief should be predictable across files; what the belief says, and the words it says it in, belong to the principal alone.

Four non-negotiables:

1. Every `belief.md` must contain an **Agent Orientations** section.
2. Every belief must carry a `layer` and a `grip`. Content without centrality and without a holding posture is a list of values, and a list of values does not change what an agent does.
3. Every belief must be in the principal's own words, with a `source`. A file written in the compiler's voice records the compiler's beliefs, however faithfully they were meant.
4. Every distributed belief ships a **short belief file** that carries the core structure, links to the full file, and tells the agent to say so when it can't open it. A belief that silently isn't loaded is worse than no belief, because everyone assumes it is.

---

## Intellectual Sources

The structure taxonomy draws on: W.V. Quine and J.S. Ullian on the web of belief and epistemological holism; Peter Berger on plausibility structures and the sociology of knowledge; Leon Festinger on cognitive dissonance; Thomas Kuhn on anomaly accumulation and paradigm shift; James Davison Hunter on institutional and deep-structural cultural change; Christian Smith and Melinda Lundquist Denton on moralistic therapeutic deism; James K.A. Smith on cultural liturgies and formation; Brian McDonald's narrative and story spine from Invisible Ink and Story Course; Ashley Null on Cranmer's anthropology of heart, will, and mind; Randall Collins on intellectual networks and the law of small numbers; David Foster Wallace on ambient defaults; Michel Foucault on power/knowledge, as the source of the objection that `worldview` is answering.

The class-and-instance framing of Belief Structures, and the `grip` and `tripwire` types, come out of a working conversation with Justin Holcomb, July 2026.
