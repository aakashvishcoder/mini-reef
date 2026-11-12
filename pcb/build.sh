#!/bin/sh
# Rebuild the PCB from the schematic: footprints -> placement -> planes -> autoroute -> finish -> DRC.
# Output: pcb/work/mini-reef.kicad_pcb (+ .kicad_pro). Copy both to the project root with KiCad closed.
set -e
cd "$(dirname "$0")"; W=${WORK:-work}; mkdir -p "$W"; cd "$W"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
[ -f pro.orig ] || cp ../../mini-reef.kicad_pro pro.orig
cp ../../fp-lib-table ../../sym-lib-table . ; ln -sfn ../../mini-reef.pretty mini-reef.pretty
$K sch export netlist -o board.net ../../mini-reef.kicad_sch >/dev/null 2>&1
printf '(kicad_pcb (version 20260206) (generator "pcbnew") (generator_version "10.0")\n)\n' > mini-reef.kicad_pcb
run() { $PY "$@" 2>&1 | grep -v wxApp || true; }
run ../mkboard.py; run ../place.py; run ../power.py
cp stage2.kicad_pcb mini-reef.kicad_pcb; run ../dsn.py
rm -f route.ses
java -jar ../freerouting.jar -de route.dsn -do route.ses -mp 25 -inc Plane --gui.enabled=false > fr.log 2>&1
grep 'Auto-routing stage completed' fr.log | sed 's/.*final score/autorouter: final score/'
run ../ses.py; run ../finish.py
$K pcb drc --severity-all --schematic-parity --format json -o drc.json mini-reef.kicad_pcb >/dev/null 2>&1 || true
python3 ../drcsum.py drc.json clearance track_width shorting_items unconnected starved_thermal
run ../lens.py
