#!/bin/sh
# Copy finished chapters into the deliverables folder as they land, so the viewer can start early.
# usage: sh tools/publish_chapters.sh "DEST_DIR"
# A chapter is copied when out/chNN.mp4 is newer than its chapter script (so stale renders are skipped)
# and newer than the copy already delivered. The file name is "NN Title.mp4", taken from Chapter(num, title).
cd "$(dirname "$0")/.."
D="$1"; [ -n "$D" ] || { echo "usage: publish_chapters.sh DEST_DIR"; exit 1; }
mkdir -p "$D"
for f in out/ch[0-9][0-9].mp4; do
  [ -f "$f" ] || continue
  n=$(basename "$f" .mp4); num=${n#ch}
  src="chapters/$n.py"
  title=$(sed -n "s/^ch = Chapter([0-9]*, *['\"]\(.*\)['\"]).*/\1/p" "$src" | head -1 | tr -d ':/\\?*"<>|')
  g="$D/$num $title.mp4"
  if [ "$f" -nt "$src" ] && { [ ! -f "$g" ] || [ "$f" -nt "$g" ]; }; then
    cp "$f" "$g" && echo "published $num"
  fi
done
