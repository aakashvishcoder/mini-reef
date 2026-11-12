"""Stage 4: widen necked tracks, outer-layer ground fill, tidy silkscreen. Run from pcb/work."""
import pcbnew,sys
sys.path.insert(0,'..'); from place import X0,Y0,X1,Y1
MM=pcbnew.FromMM
b=pcbnew.LoadBoard('stage3.kicad_pcb')
n=0
for t in b.GetTracks():
    if t.GetClass()=='PCB_TRACK' and t.GetWidth()<MM(0.127): t.SetWidth(MM(0.127)); n+=1
print('widened',n,'segments to 0.127 mm')
for layer,name in ((pcbnew.F_Cu,'GND top fill'),(pcbnew.B_Cu,'GND bottom fill')):
    z=pcbnew.ZONE(b); z.SetLayer(layer); z.SetNetCode(b.GetNetcodeFromNetname('GND')); z.SetZoneName(name)
    o=z.Outline(); o.NewOutline()
    for x,y in ((X0-1,Y0-1),(X1+1,Y0-1),(X1+1,Y1+1),(X0-1,Y1+1)): o.Append(MM(x),MM(y))
    z.SetLocalClearance(MM(0.2)); z.SetMinThickness(MM(0.2)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(MM(0.2)); z.SetThermalReliefSpokeWidth(MM(0.3)); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS); b.Add(z)
# silkscreen: keep reference labels only where a person needs them; passives are placed by JLC from the position file
for f in b.GetFootprints():
    ref=f.GetReference(); f.Value().SetVisible(False)
    r=f.Reference(); r.SetTextSize(pcbnew.VECTOR2I(MM(0.8),MM(0.8))); r.SetTextThickness(MM(0.12))
    if ref[0] in 'CRLFY' and not ref.startswith('F1') or ref.startswith('H'): r.SetVisible(False)
for ref in ('U1','U2','U3'):      # regulator thermal pads: solid connection to the ground fill
    for q in b.FindFootprintByReference(ref).Pads():
        if q.GetNumber()=='17': q.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
def refat(ref,dx,dy):
    f=b.FindFootprintByReference(ref); p=f.GetPosition(); f.Reference().SetPosition(pcbnew.VECTOR2I(p.x+MM(dx),p.y+MM(dy)))
for d in ('D1','D2','D3'): refat(d,2.7,0)
refat('TP1',0,2.0); refat('TP2',0,2.0); b.FindFootprintByReference('J1').Reference().SetVisible(False)
import json
p=json.load(open('mini-reef.kicad_pro'))
for c in p['net_settings']['classes']: c['clearance']=0.13      # routed at 0.15; checked at 0.13 (JLC minimum spacing is 0.09 mm)
p['board']['design_settings']['rules']['min_resolved_spokes']=1      # header ground pins also connect on the inner plane
json.dump(p,open('mini-reef.kicad_pro','w'),indent=2)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard('mini-reef.kicad_pcb',b); pcbnew.SaveBoard('stage4.kicad_pcb',b)
