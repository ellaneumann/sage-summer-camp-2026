#!/bin/bash
# Downloads the actual JPEGs listed in manifest.csv, using Sage credentials.
# Run once you have a working Sage username/token:
#   SAGE_USER=youruser SAGE_TOKEN=yourtoken ./download.sh
#
# It skips rows with no image_url (cameras that weren't reporting).

set -euo pipefail
cd "$(dirname "$0")"

if [[ -z "${SAGE_USER:-}" || -z "${SAGE_TOKEN:-}" ]]; then
  echo "Set SAGE_USER and SAGE_TOKEN environment variables first." >&2
  exit 1
fi

tail -n +2 manifest.csv | while IFS=, read -r filename node location date time reporting url; do
  if [[ -n "$url" ]]; then
    echo "Downloading $filename ..."
    curl -sL -u "${SAGE_USER}:${SAGE_TOKEN}" "$url" -o "$filename"
  fi
done
