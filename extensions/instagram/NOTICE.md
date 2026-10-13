# Third-Party Notice

The Instagram extension (`extensions/instagram/`) is adapted from
**instagram-agent-skill** by Jake Schincariol:
https://github.com/Jakeschincariol/instagram-agent-skill
(commit d03c56b, 2026-09-13), used under the MIT License reproduced below.

The unmodified upstream source is tracked as a git submodule at
`extension/instagram` (pinned to the same commit) for diffing against future
upstream releases. It is not loaded by the plugin. Fetch it with
`git submodule update --init extension/instagram`.

## Changes from upstream

- The 13 `skills/ig-*/SKILL.md` files became `references/<mode>.md`, each loaded on
  demand by a single `seo-social` router skill (`/seo social <mode>`). The
  frontmatter was removed and cross-links were rewritten from `/ig-<mode>` to
  `/seo social <mode>`.
- The scripts moved to `skills/seo-social/scripts/` and the data files
  (`hooks.json`, `slop.json`, `rubric.json`) to `skills/seo-social/data/`.
  Paths in `detect.py`, `humanize.py` and `swipe.py` were changed to match.
  There are no other code changes.
- Added: `skills/seo-social/SKILL.md`, `agents/seo-social.md` (site-side social
  audit), installers, and tests.

## Upstream license

```
MIT License

Copyright (c) 2026 Jake Schincariol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
