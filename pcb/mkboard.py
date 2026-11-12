"""Stage 0: empty board + every footprint from the netlist, with nets assigned. Run from pcb/work."""
import pcbnew,sys,os
sys.path.insert(0,'..'); import nl
comps,nets,padnet=nl.parse('board.net')
KL='/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
b=pcbnew.LoadBoard('mini-reef.kicad_pcb')
b.SetCopperLayerCount(4)
ni={}
for n in nets:
    it=pcbnew.NETINFO_ITEM(b,n); b.Add(it); ni[n]=it
x=20
for ref in sorted(comps):
    c=comps[ref]; lib,name=c['fp'].split(':')
    path=os.path.abspath('mini-reef.pretty') if lib=='mini-reef' else KL+lib+'.pretty'
    fp=pcbnew.FootprintLoad(path,name); assert fp,c['fp']
    fp.SetReference(ref); fp.SetValue(c['value']); fp.SetFPID(pcbnew.LIB_ID(lib,name))
    fp.SetPath(pcbnew.KIID_PATH('/'+c['ts'][0]))
    for k,v in c['fields'].items():                      # keep footprint fields identical to the symbol's
        if k in ('Footprint','Reference','Value'): continue
        fp.SetField(k,v); fp.GetField(k).SetVisible(False)
    if c['nobom']: fp.SetAttributes(fp.GetAttributes()|pcbnew.FP_EXCLUDE_FROM_BOM)
    for pad in fp.Pads():
        n=padnet.get((ref,pad.GetNumber()))
        if n: pad.SetNet(ni[n])
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(250))); x+=3
    b.Add(fp)
pcbnew.SaveBoard('stage0.kicad_pcb',b)
print(len(b.GetFootprints()),'footprints',b.GetNetCount(),'nets')
