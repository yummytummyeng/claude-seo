# Instagram Extension for Claude SEO

Thirteen Instagram modes and five offline Python tools: Reels with scored hooks
and timed beat sheets, caption linting, carousels, stories, profile scoring,
weekly plans, comment/reply/DM drafting, repurposing, post-mortems, a viral
swipe file, and a humanizer that strips AI-writing tells. Plus a site-side
audit agent that checks how the website links to its Instagram entity.

Adapted from [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
by Jake Schincariol (MIT). See [NOTICE.md](NOTICE.md).

**Nothing gets posted.** Every mode writes drafts. The user posts.

## Prerequisites

- **Claude SEO** installed (`~/.claude/skills/seo/`)
- **Python 3.8+** (stdlib only; no packages, no network, no API key)

## Installation

```bash
./extensions/instagram/install.sh
```

The installer:
1. Verifies Claude SEO and Python
2. Installs the `seo-social` skill (router, references, scripts, data) to `~/.claude/skills/seo-social/`
3. Installs the `seo-social` audit agent to `~/.claude/agents/`
4. Creates `~/.claude/instagram/voice.md` from the template if missing
5. Smoke-tests `hookscore.py`

Then fill in `~/.claude/instagram/voice.md`, or send Claude three of your reels
and say "write my voice.md from these". Every mode reads it.

## Commands

| Command | What it does |
|---------|-------------|
| `/seo social reel <idea>` | Three hooks from 26 formulas, scored; script, on-screen text, timed beat sheet |
| `/seo social viral <niche>` | Finds outlier reels in the niche, ranks by multiple over each account's median, writes swipe file |
| `/seo social caption <text>` | Lints the caption; shows the ~125 characters the feed shows before "... more" |
| `/seo social carousel <idea>` | Cover, slide copy, 1080x1350 files |
| `/seo social story <goal>` | Daily story sequence, sticker jobs, DM funnel |
| `/seo social profile <bio>` | Scores the profile on a 12-part rubric out of 100, rewrites fix-first |
| `/seo social plan` | The week: what to post, format, timing, 10 accounts to engage with |
| `/seo social human <text>` | Humanizes a draft and scores it on five checks |
| `/seo social comment <post>` | Comments on others' posts, nine types |
| `/seo social reply <thread>` | Sorts and answers comments under your own post |
| `/seo social dm <context>` | Keyword delivery, first message, collab pitch, two follow-ups |
| `/seo social repurpose <source>` | One video, podcast or newsletter into a week of posts |
| `/seo social audit` | Post-mortem ranked by outlier multiple and sends per reach |

## Tools

All take a file or `-` (stdin) and support `--json`.

```bash
S=~/.claude/skills/seo-social/scripts
python3 $S/hookscore.py hooks.txt                     # rank hooks, one per line
python3 $S/beats.py script.txt --target 30            # timed beat sheet
python3 $S/caption.py caption.txt --keywords "a,b"    # caption lint + feed preview
python3 $S/humanize.py draft.txt --report             # clean, show every change
python3 $S/detect.py before.txt after.txt             # five-check score + delta
python3 $S/swipe.py captured.tsv --out ~/.claude/instagram/swipe.md
```

`data/slop.json` is the humanizer lexicon and is meant to be edited. The
installer keeps your edited copy on reinstall and saves the new upstream
version as `slop.json.new`.

## Audit Integration

During `/seo audit`, if this extension is installed, the `seo-social` agent runs
alongside the core subagents. It reads the **website only**:

- Instagram URL in `Organization`/`Person` `sameAs`, handle consistency
- Header/footer profile links
- Open Graph / Twitter card completeness for share previews
- Instagram embed count and above-fold embeds (LCP/INP cost), facade advice
- Link-in-bio landing page: indexability, UTM tagging, mobile performance

It never fetches instagram.com, never logs in, never posts.

## Limits

- `hookscore.py` catches bad hooks well (AUC 0.83 against deliberately bad
  hooks in upstream testing) but does not pick winners between decent hooks
  (AUC 0.56). Use it as a filter, then trust the retention graph.
- The `viral` mode browses at human pace in a session the user already has
  open. No scraping, no credentials. Instagram's Terms remain the user's
  responsibility.

## Uninstallation

```bash
./extensions/instagram/uninstall.sh
```

Removes the skill and agent. `~/.claude/instagram/` (your voice profile, swipe
file, plan, log) is kept.
