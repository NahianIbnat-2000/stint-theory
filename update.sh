#!/usr/bin/env bash
# Update STINT THEORY from the newest zip in Downloads.
# Keeps .cache/, data/raw/, data/processed/ and .git/ untouched.
set -e
PROJECT="$HOME/Desktop/stint-theory"
ZIP=$(ls -t "$HOME"/Downloads/stint-theory*.zip 2>/dev/null | head -1)
if [ -z "$ZIP" ]; then echo "No stint-theory*.zip found in Downloads"; exit 1; fi
echo "Using: $ZIP"

TMP=$(mktemp -d)
python -c "import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$ZIP" "$TMP"

# copy new files over the project (overwrite, never delete your data)
cp -rf "$TMP/stint-theory/." "$PROJECT/"
rm -rf "$TMP"

# remove a leftover nested copy from earlier manual extractions
rm -rf "$PROJECT/stint-theory"

cd "$PROJECT"
python -m pytest -q
