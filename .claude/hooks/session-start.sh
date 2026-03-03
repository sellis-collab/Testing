#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code on the web sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install dependencies here as the project grows.
# Examples:
#   npm install
#   pip install -r requirements.txt
#   bundle install

echo "Session start hook complete."
