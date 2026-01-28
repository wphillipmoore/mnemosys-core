#!/usr/bin/env bash
set -euo pipefail

files=()
while IFS= read -r file; do
  files+=("$file")
done < <(find docs -type f -name "*.md" -print)

if [[ -f README.md ]]; then
  files+=("README.md")
fi

if [[ -f CHANGELOG.md ]]; then
  files+=("CHANGELOG.md")
fi

if [[ ${#files[@]} -eq 0 ]]; then
  echo "ERROR: no markdown files found to lint." >&2
  exit 2
fi

failed=0

for file in "${files[@]}"; do
  awk -v file="$file" '
    BEGIN {
      in_code = 0
      toc_found = 0
      h1_count = 0
      last_level = 0
      errors = 0
    }
    function report(message) {
      printf "ERROR: %s (%s:%d)\n", message, file, NR > "/dev/stderr"
      errors = 1
    }
    {
      line = $0

      if (match(line, /^```/) || match(line, /^~~~/)) {
        in_code = !in_code
      }

      if (in_code) {
        next
      }

      if (line ~ /^## Table of Contents[[:space:]]*$/) {
        toc_found = 1
      }

      if (line ~ /^#{1,6} /) {
        level = length(substr(line, 1, match(line, / /) - 1))
        if (level == 1) {
          h1_count += 1
        }
        if (last_level > 0 && level > last_level + 1) {
          report("Heading level skips from " last_level " to " level)
        }
        last_level = level
      }
    }
    END {
      if (h1_count != 1) {
        printf "ERROR: expected exactly one H1 heading, found %d (%s)\n", h1_count, file > "/dev/stderr"
        errors = 1
      }
      if (toc_found != 1) {
        printf "ERROR: missing ## Table of Contents (%s)\n", file > "/dev/stderr"
        errors = 1
      }
      exit errors
    }
  ' "$file" || failed=1

done

exit $failed
