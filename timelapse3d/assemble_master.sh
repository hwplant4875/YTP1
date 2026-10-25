#!/usr/bin/env bash
# EP1 full master re-assembly (agent G). Run when the segments have landed:
#   bash assemble_master.sh            check segments -> (re)render connectors C1/C2/C3 if missing -> assemble preview
#   FORCE_CONNECTORS=1 bash assemble_master.sh       re-render the connectors even if their frames exist (seam keys moved)
#   CHECK=1 bash assemble_master.sh    only print the master table / seams / what is missing
# Output: E:/YTP2/3D Timelapse/renders/master/master_preview.mp4 + master_contact.jpg (+ master_timeline.json)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
python "$HERE/aot/master_timeline.py" --fps 15 | tee "/e/YTP2/3D Timelapse/renders/master/master_timeline.txt"
[ -n "$CHECK" ] && exit 0
B="E:/YTP2/3D Timelapse/renders/master/bridges"
need=""
for c in C1:shig C2:interlude C2:march C3:march; do
  id=${c%%:*}; w=${c##*:}
  n=$(ls "$B/$id"/br_*.png 2>/dev/null | wc -l)
  exp=$(python -c "import sys; sys.path.insert(0, r'$HERE/aot'); import master_timeline as M; print(len(M.bridge_frames(M.SEG['$id'], 15)))")
  if [ -n "$FORCE_CONNECTORS" ] || [ "$n" -lt "$exp" ]; then case " $need " in *" $w "*) ;; *) need="$need $w";; esac; fi
done
if [ -n "$need" ]; then
  echo "== rendering connectors in:$need"
  [ -n "$FORCE_CONNECTORS" ] && rm -rf "$B/C1" "$B/C2" "$B/C3" "$B/keys"
  WORLDS="$need" bash "$HERE/render_bridge.sh"
fi
python "$HERE/assemble_master.py" --fps 15
