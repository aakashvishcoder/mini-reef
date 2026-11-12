"""Stage 3b: import the autorouter session, refill zones, save stage3. Run from pcb/work."""
import pcbnew,sys
b=pcbnew.LoadBoard('mini-reef.kicad_pcb')
print('ses import ok:',pcbnew.ImportSpecctraSES(b,sys.argv[1] if len(sys.argv)>1 else 'route.ses'))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard('mini-reef.kicad_pcb',b); pcbnew.SaveBoard('stage3.kicad_pcb',b)
print('tracks',len([t for t in b.GetTracks() if t.GetClass()=='PCB_TRACK']),'vias',len([t for t in b.GetTracks() if t.GetClass()=='PCB_VIA']))
