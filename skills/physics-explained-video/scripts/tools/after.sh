#!/bin/sh
# usage: after.sh LOG CH  CHAPTERS...   wait until LOG says "done CH" or "FAILED CH", then render CHAPTERS
cd "$(dirname "$0")/.."
log=$1; ch=$2; shift 2
until grep -q "done $ch\|FAILED $ch" "$log"; do sleep 15; done
sh queue.sh "$@"
