#!/bin/sh
# Make the JLCPCB order files in ../jlc: gerbers + drill (zipped), BOM.csv, CPL.csv.
set -e
cd "$(dirname "$0")/.."
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
rm -rf jlc; mkdir -p jlc/gerber
$K pcb export gerbers -o jlc/gerber/ --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
   --subtract-soldermask --no-x2 mini-reef.kicad_pcb >/dev/null 2>&1
$K pcb export drill -o jlc/gerber/ --format excellon --excellon-separate-th --excellon-units mm --drill-origin absolute mini-reef.kicad_pcb >/dev/null 2>&1
(cd jlc/gerber && zip -q ../mini-reef-gerbers.zip *)
$K pcb export pos -o jlc/pos.csv --format csv --units mm --side both mini-reef.kicad_pcb >/dev/null 2>&1
$K sch export netlist -o jlc/board.net mini-reef.kicad_sch >/dev/null 2>&1
python3 - <<'P'
import csv,sys,re,collections
sys.path.insert(0,'pcb'); import nl
comps,_,_=nl.parse('jlc/board.net')
key=lambda r:(re.match(r'[A-Z]+',r).group(),int(re.sub(r'\D','',r)))
placed={r:c for r,c in comps.items() if c['lcsc'] and not c['nobom']}        # JLC places every part that has an LCSC number
g=collections.defaultdict(list)
for r,c in placed.items(): g[(c['value'],c['fp'].split(':')[1],c['lcsc'])].append(r)
with open('jlc/BOM.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Comment','Designator','Footprint','LCSC Part #'])
    for (v,fp,l),refs in sorted(g.items(),key=lambda kv:key(sorted(kv[1],key=key)[0])): w.writerow([v,','.join(sorted(refs,key=key)),fp,l])
rows=[r for r in csv.DictReader(open('jlc/pos.csv')) if r['Ref'] in placed]
with open('jlc/CPL.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
    for r in sorted(rows,key=lambda r:key(r['Ref'])):
        w.writerow([r['Ref'],'%.4fmm'%float(r['PosX']),'%.4fmm'%float(r['PosY']),'Top' if r['Side']=='top' else 'Bottom','%g'%(float(r['Rot'])%360)])
assert {r['Ref'] for r in rows}==set(placed), set(placed)-{r['Ref'] for r in rows}      # every BOM part has a position
print('BOM lines',len(g),'| parts',len(placed),'| CPL rows',len(rows),'| not placed by JLC:',' '.join(sorted(set(comps)-set(placed),key=key)))
P
rm jlc/pos.csv jlc/board.net
ls jlc jlc/gerber
