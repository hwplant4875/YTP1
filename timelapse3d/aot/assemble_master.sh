#!/usr/bin/env bash
# EP1 master one-take assembly (silent concat of renders/g1..g8). Extra args go to aot/assemble_master.py.
#   bash aot/assemble_master.sh --missing-ok --seamcheck     partial preview now (slates for missing segments)
#   bash aot/assemble_master.sh --check                      verify files / durations / seam times only
#   bash aot/assemble_master.sh                              strict: all 8 segments must exist
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python "$HERE/assemble_master.py" "$@"
