#!/bin/sh
# Render the given chapters one after another; per-chapter logs in logs/.
cd "$(dirname "$0")"
mkdir -p logs
for c in "$@"; do
  echo "$(date +%T) start $c"
  python -u make.py "$c" --render --sheet > "logs/$c.log" 2>&1 && echo "$(date +%T) done $c" || echo "$(date +%T) FAILED $c"
done
