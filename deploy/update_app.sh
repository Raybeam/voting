#!/bin/bash
TARGET="${LC_COMMIT_HASH:-origin/master}"
APP_DIR=~/voting
cd "$APP_DIR"

echo "# Starting deployment."
echo "# Target commit: ${TARGET}"
set -e # Fail the script on any errors.

echo "# Stashing local changes to tracked files."
git stash
echo "# Fetching remote."
git fetch --all
echo "# Checking out the specified commit."
git checkout "${TARGET}"
echo "# Navigating to the backend directory."


echo "# Activating virtualenv."
set +e # The activate script might return non-zero even on success. 
. ~/venv/bin/activate
set -e

echo "# Installing pip requirements."
pip install -r requirements.txt

echo "# Restarting the voting service."
sudo systemctl restart voting

set +e
echo "# Deployment done!"