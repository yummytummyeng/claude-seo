#!/usr/bin/env bash
set -euo pipefail

# Instagram Extension Installer for Claude SEO
# Wraps everything in main() to prevent partial execution on network failure

main() {
    SKILL_DIR="${HOME}/.claude/skills/seo-social"
    AGENT_DIR="${HOME}/.claude/agents"
    SEO_SKILL_DIR="${HOME}/.claude/skills/seo"
    STATE_DIR="${HOME}/.claude/instagram"

    echo "════════════════════════════════════════"
    echo "║  Instagram - SEO Extension           ║"
    echo "║  For Claude SEO                      ║"
    echo "════════════════════════════════════════"
    echo ""

    # Check prerequisites
    if [ ! -d "${SEO_SKILL_DIR}" ]; then
        echo "✗ Claude SEO is not installed."
        echo "  Install it first: curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-seo/main/install.sh | bash"
        exit 1
    fi
    echo "✓ Claude SEO detected"

    if ! command -v python3 >/dev/null 2>&1; then
        echo "✗ Python 3.8+ is required but not installed."
        exit 1
    fi
    if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo "✗ Python 3.8+ required (found $(python3 -V 2>&1))."
        exit 1
    fi
    echo "✓ $(python3 -V 2>&1) detected"

    # Determine script directory (works for both ./install.sh and repo-relative paths)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    if [ -f "${SCRIPT_DIR}/skills/seo-social/SKILL.md" ]; then
        SOURCE_DIR="${SCRIPT_DIR}"
    elif [ -f "${SCRIPT_DIR}/extensions/instagram/skills/seo-social/SKILL.md" ]; then
        SOURCE_DIR="${SCRIPT_DIR}/extensions/instagram"
    else
        echo "✗ Cannot find extension source files."
        echo "  Run this script from the claude-seo repo: ./extensions/instagram/install.sh"
        exit 1
    fi

    # Install skill with scripts, data, references and templates for ${CLAUDE_SKILL_DIR} resolution
    echo "→ Installing seo-social skill..."
    mkdir -p "${SKILL_DIR}/scripts" "${SKILL_DIR}/data" "${SKILL_DIR}/references" "${SKILL_DIR}/templates"
    cp "${SOURCE_DIR}/skills/seo-social/SKILL.md" "${SKILL_DIR}/SKILL.md"
    cp "${SOURCE_DIR}/skills/seo-social/scripts/"*.py "${SKILL_DIR}/scripts/"
    cp "${SOURCE_DIR}/skills/seo-social/references/"*.md "${SKILL_DIR}/references/"
    cp "${SOURCE_DIR}/skills/seo-social/templates/"*.md "${SKILL_DIR}/templates/"
    cp "${SOURCE_DIR}/NOTICE.md" "${SKILL_DIR}/NOTICE.md"

    # Keep a user-edited lexicon across reinstalls
    for f in "${SOURCE_DIR}/skills/seo-social/data/"*.json; do
        dest="${SKILL_DIR}/data/$(basename "${f}")"
        if [ "$(basename "${f}")" = "slop.json" ] && [ -f "${dest}" ] && ! cmp -s "${f}" "${dest}"; then
            echo "  ℹ  Keeping your edited data/slop.json (upstream copy saved as slop.json.new)"
            cp "${f}" "${dest}.new"
        else
            cp "${f}" "${dest}"
        fi
    done

    # Install agent
    echo "→ Installing seo-social agent..."
    mkdir -p "${AGENT_DIR}"
    cp "${SOURCE_DIR}/agents/seo-social.md" "${AGENT_DIR}/seo-social.md"

    # User state directory (voice profile, swipe file, plan, log)
    mkdir -p "${STATE_DIR}"
    if [ ! -f "${STATE_DIR}/voice.md" ]; then
        cp "${SOURCE_DIR}/skills/seo-social/templates/voice.md" "${STATE_DIR}/voice.md"
        echo "→ Created ${STATE_DIR}/voice.md (fill it in: every mode reads it)"
    fi

    # Smoke test (exit 0/1 is a score verdict; anything else is a broken install)
    rc=0
    python3 "${SKILL_DIR}/scripts/hookscore.py" --hook "I lost \$18,000 because of one missing contract." --json >/dev/null || rc=$?
    if [ "${rc}" -le 1 ]; then
        echo "✓ Scripts verified"
    else
        echo "⚠  hookscore.py smoke test failed (exit ${rc}). Check: python3 ${SKILL_DIR}/scripts/hookscore.py --hook \"test\""
    fi

    echo ""
    echo "✓ Instagram extension installed successfully!"
    echo ""
    echo "Usage:"
    echo "  1. Start Claude Code:  claude"
    echo "  2. Run commands:"
    echo "     /seo social reel \"How we cut proposal time from 5 hours to 20 minutes\""
    echo "     /seo social caption \"<paste caption>\""
    echo "     /seo social profile \"<paste name field and bio>\""
    echo "     /seo social human \"<paste draft>\""
    echo "     /seo social plan"
    echo ""
    echo "Full docs: extensions/instagram/README.md"
    echo "To uninstall: ./extensions/instagram/uninstall.sh"
}

main "$@"
