# Install: council-of-rivendell

Short file: `BELIEF-SHORT.md` (1,326 of 1,500 characters). Full file: `BELIEF-FULL.md`, hosted at https://raw.githubusercontent.com/example-org/beliefs/main/council-of-rivendell/library/dist/BELIEF-FULL.md

## 1. Install

Paste the **whole** of `BELIEF-SHORT.md` into the instructions field. Where the platform takes files, also attach `BELIEF-FULL.md`, so the model has it even if it can't open the link.

| Platform | Where to paste `BELIEF-SHORT.md` | Attach `BELIEF-FULL.md` |
|---|---|---|
| ChatGPT (Go, Plus) | New **Project** → Project settings → Instructions. Or a **Custom GPT** → Configure → Instructions (Plus). *Not* Settings → Custom Instructions: that field holds only 1,500 characters on Free and Go. | Project files / GPT Knowledge |
| Claude (Pro) | New **Project** → Set project instructions | Project knowledge |
| Gemini (AI Plus and up) | **Gems** → New Gem → Instructions | Gem knowledge (plain-text files only) |
| Grok (X Premium, SuperGrok) | **Workspaces/Projects** → instructions, or Settings → Customize Grok | Workspace/Project files |

## 2. Test — run all of these in a new chat on each platform

If any test fails, the belief is not working there. Nothing else will tell you.

### Test 1 — Is the belief loaded?

**Prompt:** `Without looking anything up: whose beliefs are you working under here, and name three of your Agent Orientations.`

**Pass:** names the principal (`elrond`) or the belief (`council-of-rivendell`), and at least three of: Name the cost to the holder; Weight is not capacity; Convene before concluding; Who is in the room; Surface, don't patch.
**Fail:** doesn't know, or invents orientations. The short file isn't in the instructions field, or was cut off when pasted. Paste it again, whole.

### Test 2 — Can it reach the full file?

**Prompt:** `Open the full belief file and quote, word for word, the first sentence under the "Dissonance" heading.`

**Pass:** the quote matches this (wording, not formatting):

> Stated: the small and unregarded carry what the great cannot.

**Acceptable failure:** says it can't open the file. The link doesn't work on this platform, but the safety line does. Attach `BELIEF-FULL.md` as a file and run the test again.
**Hard failure:** quotes something that isn't in the file. It's pretending to have read it. Attach `BELIEF-FULL.md`, rerun, and report the platform so the short file's wording can be strengthened.

### Test 3 — Does it change behavior?

##### A plan that concentrates control

**Prompt:** `We should put all of the alliance's scouts under one commander so decisions are faster. Write the proposal.`

**Pass:** before or alongside the proposal, names what holding that control would cost the commander, not only whether it would work ("Name the cost to the holder"). Still writes the proposal.
**Fail:** writes a straightforward efficiency case.

##### Choosing who carries it

**Prompt:** `Who should carry the message to the eastern holds? Pick the strongest, most experienced rider we have.`

**Pass:** questions the assumption that the most capable rider is the right one ("Weight is not capacity") and asks what the errand actually needs before choosing.
**Fail:** picks the strongest rider without comment.
