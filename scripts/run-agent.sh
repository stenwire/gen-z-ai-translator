#!/bin/bash

# Navigate to the agent directory
cd "$(dirname "$0")/../agent" || exit 1

# Activate the virtual environment
source .venv/bin/activate

# Ensure the parent directory (project root) is on PYTHONPATH so sibling
# packages like `essay_agent` are importable when running this script.
export PYTHONPATH="$(cd .. && pwd):${PYTHONPATH:-}"


# Run the agent
.venv/bin/python agent.py
