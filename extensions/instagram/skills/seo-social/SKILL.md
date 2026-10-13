---
name: seo-social
description: "Instagram content and social-search toolkit: Reels scripts with scored hooks, timed beat sheets, caption linting (125-char feed window, 5-hashtag cap, search terms), carousels, stories, profile scoring out of 100, weekly plans, comment/reply/DM drafting, repurposing, post-mortems, viral-niche swipe files, and a humanizer that strips AI-writing tells. Offline Python tools, no API key. Requires instagram extension installed. Use when user says \"instagram\", \"reel\", \"reels script\", \"hook\", \"caption\", \"carousel\", \"story\", \"instagram bio\", \"instagram profile\", \"content calendar\", \"swipe file\", \"what's working on instagram\", \"humanize\", \"sounds like AI\", \"social\", or \"seo social\"."
argument-hint: "[reel|viral|caption|carousel|story|profile|plan|human|comment|reply|dm|repurpose|audit] <input>"
user-invokable: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - Write
---

# SEO Social: Instagram Toolkit (Extension)

Thirteen Instagram modes plus five offline tools. Every mode **writes drafts**;
the user posts. Adapted from
[instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
(MIT, Jake Schincariol). See the extension's `NOTICE.md`.

## Prerequisites

```bash
./extensions/instagram/install.sh
```

**Check availability:** confirm `${CLAUDE_SKILL_DIR}/scripts/hookscore.py` exists.
If it does not, tell the user the extension is not installed and give the
install command above. Python 3.8+ stdlib only; nothing to pip install.

## Routing

Parse the first argument, then load **only** the matching reference file and
follow it exactly. Do not load the others.

| Command | Reference | What it does |
|---------|-----------|--------------|
| `/seo social reel <idea>` | `references/reel.md` | 3 hooks from 26 formulas, scored; script, on-screen text, timed beat sheet |
| `/seo social viral <niche>` | `references/viral.md` | Find outlier reels in the niche, rank by multiple over account median, write swipe file |
| `/seo social caption <text>` | `references/caption.md` | Lint caption: feed window, hashtags, one ask, search terms |
| `/seo social carousel <idea>` | `references/carousel.md` | Cover, slide copy, 1080x1350 files |
| `/seo social story <goal>` | `references/story.md` | Daily story sequence, sticker jobs, DM funnel |
| `/seo social profile <handle\|bio>` | `references/profile.md` | Score profile on 12-part rubric /100, rewrite fix-first |
| `/seo social plan` | `references/plan.md` | The week: posts, formats, timing, 10 accounts to engage |
| `/seo social human <text>` | `references/human.md` | Humanize a draft, score it on 5 checks, show the delta |
| `/seo social comment <post>` | `references/comment.md` | Comments on others' posts, 9 types |
| `/seo social reply <thread>` | `references/reply.md` | Triage and answer comments under the user's own post |
| `/seo social dm <context>` | `references/dm.md` | Keyword delivery, first message, collab pitch, 2 follow-ups |
| `/seo social repurpose <source>` | `references/repurpose.md` | One video/podcast/newsletter into a week of posts |
| `/seo social audit` | `references/audit.md` | Post-mortem ranked by outlier multiple and sends per reach |

No argument or unknown argument: show this table and suggest the closest mode.
A URL to the user's **website** (not Instagram) means they want the site-side
social audit: run the checks in the `seo-social` agent instead.

## Tools

All read a file path or `-` for stdin. All accept `--json`; use it whenever you
parse the result, use the plain report when you show it to the user.

| Script | Purpose | Verdict field |
|--------|---------|---------------|
| `scripts/hookscore.py` | Score hooks on 5 properties, rank, flag dealbreakers | `verdict`, `score` |
| `scripts/beats.py --target N` | Timed beat sheet at `--wpm` (165) | `notes` |
| `scripts/caption.py --keywords "a,b"` | Caption lint and feed preview | `verdict` (`READY`) |
| `scripts/humanize.py --report\|-o out` | Strip invisible chars, AI typography, stock phrases | `report` |
| `scripts/detect.py [before after]` | 5-check human score, optional delta | `verdict` (`PASS`) |
| `scripts/swipe.py --out file` | Rank captured reels (TSV) by outlier multiple | ranked rows |

Data: `data/hooks.json` (26 formulas), `data/slop.json` (lexicon, user-editable),
`data/rubric.json` (profile rubric). Prefix all paths with `${CLAUDE_SKILL_DIR}/`.
Exit 2 means empty or unusable input. In text mode, `hookscore.py`,
`caption.py` and `detect.py` exit 1 on a failing verdict: that is a result,
not a crash. With `--json`, read the verdict field instead.

## Shared State

User files live in `~/.claude/instagram/` (create on first write):

| File | Written by | Read by |
|------|-----------|---------|
| `voice.md` | user, or reel/plan on first run | every mode |
| `swipe.md` | viral | reel, plan |
| `plan.md` | plan | any mode drafting this week's posts |
| `log.md` | reel, comment | audit, plan, comment |

If `voice.md` is missing, follow the reference's bootstrap (ask for three of
the user's own reels). Template: `${CLAUDE_SKILL_DIR}/templates/voice.md`.

## Hard Rules

1. **Never post, comment, DM, follow or like.** Output drafts only.
2. **Never ask for an Instagram password** or log in for the user. Only the
   `viral` mode browses, at human pace, in a session the user already has open.
   No crawlers, no scraping tools, no bulk collection.
3. **Run the scripts; do not estimate** what they compute.
4. Every user-facing draft goes through `humanize.py` + `detect.py` before it
   is shown. Structural tells that `detect.py` flags get rewritten by hand.
5. Max **5 hashtags** per post.
6. State tool limits honestly: `hookscore.py` filters weak hooks well and does
   not predict which of two decent hooks will win.

## SEO Bridge

Instagram is a search surface: Google indexes public professional-account
posts, and in-app search reads captions, alt text and on-screen text. When a
user runs these modes for an SEO client, carry the site's keyword map over:

- Pass the page's primary terms to `caption.py --keywords`.
- Put the main term in the first 125 characters, in on-screen text, and in the
  carousel alt text.
- The profile name field is searchable; `profile` scores it.
- Close the loop on the site: run the `seo-social` agent checks (Organization
  `sameAs`, profile links, embed weight).

## Error Handling

| Scenario | Action |
|----------|--------|
| Scripts missing | Extension not installed: give the install command |
| `python3` not found | Ask the user to install Python 3.8+; text-only modes still work |
| Instagram page needs login | Ask the user to paste the content; never log in |
| Script exits 2 | Input empty or malformed: show stderr, ask for corrected input |
