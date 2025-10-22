#!/bin/bash

# Navigate to the agent directory
cd "$(dirname "$0")/../agent" || exit 1

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  uv venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install requirements using uv
uv pip install -r requirements.txt