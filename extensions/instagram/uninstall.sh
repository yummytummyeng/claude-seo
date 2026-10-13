#!/usr/bin/env bash
set -euo pipefail

main() {
    echo "→ Uninstalling Instagram extension..."

    # Remove skill (includes copied scripts, data, references and templates)
    rm -rf "${HOME}/.claude/skills/seo-social"

    # Remove agent
    rm -f "${HOME}/.claude/agents/seo-social.md"

    # User content is never deleted automatically
    if [ -d "${HOME}/.claude/instagram" ]; then
        echo "  ℹ  Kept ~/.claude/instagram/ (your voice profile, swipe file, plan and log)."
        echo "  ℹ  Delete it manually if you no longer need it."
    fi

    echo "✓ Instagram extension uninstalled."
}

main "$@"
