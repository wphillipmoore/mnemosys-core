#!/usr/bin/env bash
set -euo pipefail

profile_file="standard-tooling.toml"

if [[ ! -f "$profile_file" ]]; then
  echo "ERROR: $profile_file not found" >&2
  exit 2
fi

failed=0

for key in repository-type versioning-scheme branching-model release-model primary-language; do
  value=$(grep -E "^${key}[[:space:]]*=" "$profile_file" | head -1 | sed 's/^[^=]*=[[:space:]]*//' | tr -d '"' || true)
  if [[ -z "$value" ]]; then
    echo "ERROR: missing required field '$key' in $profile_file" >&2
    failed=1
  fi
done

exit $failed
