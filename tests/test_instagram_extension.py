"""Tests for the Instagram extension (extensions/instagram).

Runs every script as a subprocess, the way the skill invokes it, and checks
JSON output, verdict semantics, data-path resolution after the move from the
upstream layout, and that the router skill and references stay consistent.

Usage:
    python -m pytest tests/test_instagram_extension.py
"""

import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "extensions", "instagram", "skills", "seo-social")
SCRIPTS = os.path.join(EXT, "scripts")
SKILL = os.path.join(EXT, "SKILL.md")

MODES = ["reel", "viral", "caption", "carousel", "story", "profile", "plan",
         "human", "comment", "reply", "dm", "repurpose", "audit"]

SLOP_DRAFT = (
    "Stop scrolling — this is a game-changer. "
    "It’s not just SEO, it’s a journey.​ "
    "Let’s delve into the ever-evolving landscape. Follow for more!"
)


def run(script, *args, stdin=None, cwd=None):
    """Run a script in isolated mode from an unrelated cwd, return (rc, stdout, stderr)."""
    p = subprocess.run(
        [sys.executable, "-I", os.path.join(SCRIPTS, script), *args],
        input=stdin, capture_output=True, text=True, encoding="utf-8",
        cwd=cwd or os.path.expanduser("~"), timeout=60,
    )
    return p.returncode, p.stdout, p.stderr


# ---------------------------------------------------------------- data files

@pytest.mark.parametrize("name", ["hooks.json", "slop.json", "rubric.json"])
def test_data_files_parse(name):
    with open(os.path.join(EXT, "data", name), encoding="utf-8") as fh:
        assert json.load(fh)


def test_hooks_has_26_formulas_with_valid_regex():
    with open(os.path.join(EXT, "data", "hooks.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    assert len(data["hooks"]) == 26
    ids = {h["id"] for h in data["hooks"]}
    for h in data["hooks"]:
        re.compile(h["match"])
    assert set(data["classify_order"]) <= ids


def test_rubric_totals_100():
    with open(os.path.join(EXT, "data", "rubric.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    assert len(data["items"]) == 12
    weights = [i.get("points", i.get("weight", 0)) for i in data["items"]]
    assert sum(weights) == data["total"] == 100


# ---------------------------------------------------------------- hookscore

def test_hookscore_rejects_greeting():
    rc, out, _ = run("hookscore.py", "--hook", "Hey guys, today I wanted to talk about SEO", "--json")
    assert rc == 0
    d = json.loads(out)
    assert d["verdict"] == "WEAK"
    assert d["score"] < 50
    assert d["flags"]
    assert set(d["checks"]) == {"LENGTH", "SPECIFICITY", "STAKES", "FRONTLOAD", "ADDRESS"}


def test_hookscore_ranks_concrete_hook_above_greeting():
    hooks = "Hey guys, today I wanted to talk about content\nI lost $18,000 because of one missing contract.\n"
    rc, out, _ = run("hookscore.py", "-", "--json", stdin=hooks)
    assert rc == 0
    scores = {d["hook"]: d["score"] for d in json.loads(out)}
    assert scores["I lost $18,000 because of one missing contract."] >= 70
    assert scores["I lost $18,000 because of one missing contract."] > scores[
        "Hey guys, today I wanted to talk about content"]


def test_hookscore_text_mode_exit_code_is_verdict():
    rc, _, _ = run("hookscore.py", "--hook", "Hey guys, today I wanted to talk")
    assert rc == 1


def test_hookscore_empty_input():
    rc, _, err = run("hookscore.py", "-", stdin="\n\n")
    assert rc == 2
    assert "nothing to score" in err


# ---------------------------------------------------------------- beats

def test_beats_timing_and_target():
    script = ("I lost $18,000 because of one missing contract.\n"
              "Here is the clause I now put in every contract.\n"
              "Payment on delivery, not on approval.\n"
              "That one change is worth $18,000 to me.\n")
    rc, out, _ = run("beats.py", "-", "--target", "30", "--json", stdin=script)
    assert rc == 0
    d = json.loads(out)
    assert d["wpm"] == 165 and d["target"] == 30
    assert len(d["beats"]) == 4
    assert d["beats"][0]["start"] == 0.0
    total = sum(b["dur"] for b in d["beats"])
    assert abs(total - d["total_seconds"]) < 0.1


# ---------------------------------------------------------------- caption

def test_caption_hashtag_cap_and_keywords():
    tags = " ".join(f"#tag{i}" for i in range(8))
    caption = f"I lost $18,000 on one missing contract clause.\n\nComment CLAUSE for the template.\n\n{tags}"
    rc, out, _ = run("caption.py", "-", "--keywords", "client contracts", "--json", stdin=caption)
    d = json.loads(out)
    assert d["verdict"] != "READY"
    assert rc == 1
    blob = json.dumps(d).lower()
    assert "hashtag" in blob and "client contracts" in blob


# ---------------------------------------------------------------- humanizer

def test_humanize_strips_fingerprint():
    rc, out, _ = run("humanize.py", "-", "--json", stdin=SLOP_DRAFT)
    assert rc == 0
    text = json.loads(out)["text"]
    for ch in ("—", "’", "​"):
        assert ch not in text
    assert "game-changer" not in text.lower()


def test_detect_scores_improve_after_humanize(tmp_path):
    before = tmp_path / "before.txt"
    after = tmp_path / "after.txt"
    before.write_text(SLOP_DRAFT, encoding="utf-8")
    _, out, _ = run("humanize.py", str(before), "--json")
    after.write_text(json.loads(out)["text"], encoding="utf-8")

    rc, out, _ = run("detect.py", str(before), str(after), "--json")
    assert rc == 0
    a, b = json.loads(out)
    assert a["verdict"] == "FLAGGED"
    assert b["human_score"] > a["human_score"]
    assert set(a["checks"]) == {"BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"}


def test_custom_lexicon_flag(tmp_path):
    lex = tmp_path / "slop.json"
    with open(os.path.join(EXT, "data", "slop.json"), encoding="utf-8") as fh:
        lex.write_text(fh.read(), encoding="utf-8")
    rc, out, _ = run("humanize.py", "-", "--json", "--lexicon", str(lex), stdin="plain words")
    assert rc == 0 and json.loads(out)["text"].strip() == "plain words"


# ---------------------------------------------------------------- swipe

def test_swipe_ranks_by_outlier_and_classifies(tmp_path):
    tsv = ("account\tfollowers\tviews\thook\n"
           "@big\t2000000\t400000\tin this video I am going to show you my morning routine\n"
           "@small\t4000\t400000\tnobody tells you that your first 30 reels are supposed to flop\n")
    out_md = tmp_path / "nested" / "swipe.md"
    rc, out, err = run("swipe.py", "-", "--json", "--out", str(out_md), stdin=tsv)
    assert rc == 0, err
    assert "not found" not in err and "not importable" not in err
    assert out_md.exists()
    blob = json.loads(out)
    rows = blob["rows"] if isinstance(blob, dict) and "rows" in blob else blob
    assert "@small" in json.dumps(rows)
    assert "Nobody Tells You" in json.dumps(blob)


def test_swipe_bad_input():
    rc, _, err = run("swipe.py", "-", stdin="a\tb\n")
    assert rc == 2 and "no usable rows" in err


# ---------------------------------------------------------------- skill wiring

def test_router_skill_references_exist_and_under_limits():
    with open(SKILL, encoding="utf-8") as fh:
        skill = fh.read()
    assert len(skill.splitlines()) < 500
    for mode in MODES:
        ref = os.path.join(EXT, "references", f"{mode}.md")
        assert f"references/{mode}.md" in skill
        with open(ref, encoding="utf-8") as fh:
            body = fh.read()
        assert len(body.splitlines()) < 200, ref
        assert not body.startswith("---"), f"{ref} still has frontmatter"
        assert "/ig-" not in body, f"{ref} has an upstream /ig- link"


def test_references_point_at_files_that_exist():
    pat = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/((?:scripts|data|templates)/[\w.-]+)")
    for mode in MODES:
        with open(os.path.join(EXT, "references", f"{mode}.md"), encoding="utf-8") as fh:
            for rel in pat.findall(fh.read()):
                assert os.path.exists(os.path.join(EXT, rel)), f"{mode}.md -> {rel}"


def test_plugin_manifest_registers_extension():
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    assert "extensions/instagram/skills/seo-social/SKILL.md" in manifest["skills"]
    assert "extensions/instagram/agents/seo-social.md" in manifest["agents"]
    for path in manifest["skills"] + manifest["agents"]:
        assert os.path.exists(os.path.join(ROOT, path)), path
