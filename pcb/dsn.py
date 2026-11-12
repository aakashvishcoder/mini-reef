"""Stage 3a: export a Specctra DSN for the autorouter. Run from pcb/work."""
import pcbnew
b=pcbnew.LoadBoard('mini-reef.kicad_pcb')
b.SetLayerType(pcbnew.In1_Cu,pcbnew.LT_POWER); b.SetLayerType(pcbnew.In2_Cu,pcbnew.LT_POWER)
pcbnew.SaveBoard('mini-reef.kicad_pcb',b)
print('dsn export ok:',pcbnew.ExportSpecctraDSN(b,'route.dsn'))
