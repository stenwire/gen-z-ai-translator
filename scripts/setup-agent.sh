#!/bin/bash

# Navigate to the agent directory
# cd "$(dirname "$0")/../agent" || exit 1

# # Create virtual environment if it doesn't exist
# if [ ! -d ".venv" ]; then
#   uv venv .venv
# fi

# # Activate the virtual environment
# source .venv/bin/activate

# # Install requirements using uv
# uv pip install -r requirements.txt

#!/bin/bash
set -e  # Exit immediately if a command fails

# Navigate to the agent directory
cd "$(dirname "$0")/../agent" || exit 1

# Ensure uv is installed, or fall back to venv + pip
if ! command -v uv &> /dev/null; then
  echo "⚙️  'uv' not found. Installing it..."
  pip install uv || {
    echo "⚠️ Failed to install 'uv', falling back to python venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    exit 0
  }
fi

# Create virtual environment using uv if it doesn’t exist
if [ ! -d ".venv" ]; then
  uv venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies using uv
uv pip install -r requirements.txt
