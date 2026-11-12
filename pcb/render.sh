#!/bin/sh
# usage: render.sh <board.kicad_pcb> <layers> <out.png>   (run from pcb/work)
set -e
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export svg --layers "$2" --page-size-mode 2 --exclude-drawing-sheet -o r.svg "$1" >/dev/null 2>&1
rm -f r.svg.png; qlmanage -t -s 2000 -o . r.svg >/dev/null 2>&1; mv r.svg.png "$3"
