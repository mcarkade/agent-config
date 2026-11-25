#!/bin/sh
# Render the given chapters one after another; per-chapter logs in logs/.
cd "$(dirname "$0")"
logdir=logs
mkdir -p "$logdir"
status=0
for c in "$@"; do
  echo "$(date +%T) start $c"
  if python -u make.py "$c" --render --sheet > "$logdir/$c.log" 2>&1; then
    echo "$(date +%T) done $c"
  else
    echo "$(date +%T) FAILED $c; see $logdir/$c.log"
    status=1
  fi
done
exit "$status"
