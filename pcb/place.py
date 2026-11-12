"""Stage 1: design rules, rounded outline, mounting holes, placement. Run from pcb/work."""
import pcbnew,math,json,shutil
MM=pcbnew.FromMM
def V(x,y): return pcbnew.VECTOR2I(MM(x),MM(y))
X0,Y0,X1,Y1=100.0,100.0,172.0,162.0      # board: 72 x 62 mm
FX,FY=141.0,127.0                        # FPGA centre
HOLES=[(104,104),(168,104),(104,158),(168,158)]
PLANES={'GND','+3V3','+1V8','+1V0'}
if __name__=='__main__':
    # ---- project rules / net classes (JLC 4-layer capabilities)
    p=json.load(open('pro.orig'))
    r=p.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{}); p.setdefault('net_settings',{})
    r.update(min_clearance=0.127,min_track_width=0.127,min_via_diameter=0.45,min_through_hole_diameter=0.2,min_via_annular_width=0.1,
             min_hole_clearance=0.2,min_hole_to_hole=0.25,min_copper_edge_clearance=0.3)
    base=dict(bus_width=12,diff_pair_gap=0.2,diff_pair_via_gap=0.25,diff_pair_width=0.2,line_style=0,microvia_diameter=0.3,microvia_drill=0.1,
              pcb_color="rgba(0, 0, 0, 0.000)",schematic_color="rgba(0, 0, 0, 0.000)",tuning_profile="",wire_width=6)
    def nc(name,prio,cl,w,vd,vh): return dict(base,name=name,priority=prio,clearance=cl,track_width=w,via_diameter=vd,via_drill=vh)
    p['net_settings']['classes']=[nc('Default',2147483647,0.15,0.15,0.5,0.3),nc('Plane',0,0.15,0.2,0.5,0.3),nc('Power',1,0.2,0.4,0.6,0.3),nc('USB',2,0.15,0.2,0.5,0.3)]
    p['net_settings']['netclass_patterns']=[dict(netclass='Plane',pattern=n) for n in sorted(PLANES)]+\
       [dict(netclass='Power',pattern=n) for n in ('+5V','VBUS','Net-(L1-Pad1)','Net-(L2-Pad1)','Net-(L3-Pad1)')]+[dict(netclass='USB',pattern='USB_D*')]
    json.dump(p,open('mini-reef.kicad_pro','w'),indent=2)
    shutil.copy('stage0.kicad_pcb','mini-reef.kicad_pcb')
    b=pcbnew.LoadBoard('mini-reef.kicad_pcb')
    b.SetCopperLayerCount(4)
    b.GetDesignSettings().SetBoardThickness(MM(1.6))
    # ---- outline with rounded corners (3 mm)
    R=3.0
    def seg(a,c):
        s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*c)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); b.Add(s)
    def arc(cx,cy,a0):
        s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC)
        pt=lambda a:(cx+R*math.cos(math.radians(a)),cy+R*math.sin(math.radians(a)))
        s.SetArcGeometry(V(*pt(a0)),V(*pt(a0+45)),V(*pt(a0+90))); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); b.Add(s)
    seg((X0+R,Y0),(X1-R,Y0)); seg((X1,Y0+R),(X1,Y1-R)); seg((X1-R,Y1),(X0+R,Y1)); seg((X0,Y1-R),(X0,Y0+R))
    arc(X0+R,Y0+R,180); arc(X1-R,Y0+R,270); arc(X1-R,Y1-R,0); arc(X0+R,Y1-R,90)
    for i,(x,y) in enumerate(HOLES):
        fp=pcbnew.FootprintLoad('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/MountingHole.pretty','MountingHole_3.2mm_M3')
        fp.SetReference(f'H{i+1}'); fp.SetPosition(V(x,y)); fp.SetAttributes(pcbnew.FP_BOARD_ONLY|pcbnew.FP_EXCLUDE_FROM_BOM|pcbnew.FP_EXCLUDE_FROM_POS_FILES); b.Add(fp)
    P={}
    def put(ref,x,y,rot=0): P[ref]=(round(x,3),round(y,3),rot)
    # ---- FPGA + HyperRAM (left of the FPGA's bank 35 corner)
    import os
    HR_ROT=int(os.environ.get('HR_ROT','90')); HR_DY=float(os.environ.get('HR_DY','-5.0'))      # chosen by search.sh for matched HyperBus lengths
    put('U4',FX,FY,0); put('U5',FX-(14.9 if HR_ROT%180 else 13.9),FY+HR_DY,HR_ROT)
    for i,r_ in enumerate(('C57','C58','C59','C60')): put(r_,123.7+1.6*i,115.7,90)
    # ---- buck regulators: inductor left of the chip, input caps right, output cap at the far end
    def buck(ux,uy,U,L,Cin,C100,Css,Cout,Rt,Rb,Rpg=None):
        put(U,ux,uy); put(L,ux-5.2,uy-0.4); put(Cout,ux-9.7,uy-0.2,90); put(Cin,ux+3.6,uy-0.4,90); put(C100,ux+2.2,uy-3.0)
        put(Css,ux+3.2,uy+2.8); put(Rt,ux-2.4,uy+3.0); put(Rb,ux-0.3,uy+3.0)
        if Rpg: put(Rpg,ux-5.2,uy+3.0)
    buck(118.4,105.5,'U2','L2','C5','C6','C7','C8','R7','R8','R6')     # +1V8, top-left
    buck(111.4,119.0,'U1','L1','C1','C2','C3','C4','R3','R4','R5')     # +1V0, left
    buck(111.4,134.0,'U3','L3','C9','C10','C11','C12','R9','R10')      # +3V3, left
    # ---- FPGA decoupling: small caps in a ring just outside the BGA, grouped by rail
    RR=10.9
    def ring(ref,side,d):
        if side=='T': put(ref,FX+d,FY-RR,90)
        if side=='B': put(ref,FX+d,FY+RR,90)
        if side=='L': put(ref,FX-RR,FY+d,0)
        if side=='R': put(ref,FX+RR,FY+d,0)
    for i,r_ in enumerate(('C27','C24','C25','C26','C53','C54','C55','C56')): ring(r_,'T',-11.2+1.4*i)   # +1V8 rails
    put('C21',128.5,107.0); put('C50',128.5,110.0); put('C22',134.0,107.0); put('C23',134.0,109.6); put('C51',138.2,107.0); put('C52',138.2,109.6)
    for r_,d in (('C16',1.6),('C17',3.0),('C18',4.4),('C20',5.8)): ring(r_,'L',d)                      # +1V0 rails
    put('C14',126.6,129.3); put('C15',126.6,131.9); put('C13',122.0,129.5); put('C19',122.0,132.3); put('TP3',117.6,125.6)
    ring('C39','T',8.2); ring('C40','R',-8.2); ring('C41','R',-2.4); ring('C42','R',-1.0)             # VCCO_15
    put('C37',154.4,119.6,90); put('C38',154.4,123.5,90); put('C36',157.2,124.6,90)
    ring('C32','R',3.2); ring('C33','R',4.6); ring('C34','B',3.4); ring('C35','B',4.8)                 # VCCO_14
    put('C30',154.4,130.6,90); put('C31',148.6,140.9); put('C29',153.6,140.9)
    ring('C46','L',8.2); ring('C47','B',-8.2); ring('C48','B',-3.4); ring('C49','B',-2.0)             # VCCO_34
    put('C44',128.0,137.4); put('C45',128.0,139.6); put('C43',129.6,145.8)
    put('C28',143.5,140.9)                                                                           # VCCO_0
    # ---- right side: test-host header, LEDs, button, flash, oscillator
    put('J3',166.3,115.65,0)
    for i,(rr,dd) in enumerate((('R19','D2'),('R20','D3'),('R11','D1'))): put(rr,151.6,105.6+2.2*i); put(dd,155.2,105.6+2.2*i)
    put('SW1',159.8,116.3); put('R21',160.5,121.3)
    put('U7',161.5,134.5); put('C64',168.4,133.2,90)
    for i,r_ in enumerate(('R16','R17','R18')): put(r_,158.2+1.9*i,139.2,90)
    put('X1',160.0,144.2); put('C65',164.0,144.2,90)
    # ---- bottom: CH347, crystal, USB-C, headers
    put('U6',121.0,144.5,180); put('Y1',118.5,151.5); put('C62',114.2,151.5,90); put('C63',122.9,151.5,90)
    put('C61',116.2,142.4,90); put('R12',124.6,139.6); put('R13',116.2,145.4,90)
    put('J1',103.7,148.3,270); put('F1',112.0,144.6); put('R1',110.6,151.2); put('R2',110.6,152.9)
    put('TP1',110.6,147.7); put('TP2',113.6,147.7); put('JP1',112.0,158.6,90)
    put('J4',126.65,156.3,90); put('J2',147.65,158.6,90)
    put('R14',138.0,141.3,90); put('R15',139.6,141.3,90)
    put('TP4',127.0,103.0); put('TP5',144.8,102.8); put('TP6',147.8,102.8); put('TP7',165.5,150.0)
    missing=[f.GetReference() for f in b.GetFootprints() if f.GetReference() not in P and not f.GetReference().startswith('H')]
    assert not missing,missing
    for ref,(x,y,rot) in P.items():
        fp=b.FindFootprintByReference(ref); fp.SetPosition(V(x,y)); fp.SetOrientationDegrees(rot)
    # ---- orientation: for 2-pin parts and the HyperRAM, pick the rotation with the shortest connections
    def padpos():
        d={}
        for f in b.GetFootprints():
            for q in f.Pads():
                n=q.GetNetname()
                if n and not n.startswith('unconnected'): d.setdefault(n,[]).append((f.GetReference(),q.GetPosition().x,q.GetPosition().y))
        return d
    def cost(fp,d):
        c=0
        for q in fp.Pads():
            n=q.GetNetname()
            if not n or n=='GND' or (n in PLANES and fp.GetReference()!='U5'): continue
            o=[math.hypot(q.GetPosition().x-x,q.GetPosition().y-y) for r_,x,y in d.get(n,[]) if r_!=fp.GetReference()]
            if o: c+=min(o)
        return c
    for rnd in range(2):
        d=padpos()
        for fp in b.GetFootprints():
            ref=fp.GetReference(); n=len([q for q in fp.Pads() if q.GetNumber()])
            if ref=='U5': continue
            if n==2 and ref[0] in 'CRLDFY': rots=(P[ref][2],P[ref][2]+180)
            else: continue
            best=min(rots,key=lambda a:(fp.SetOrientationDegrees(a),cost(fp,d))[1]); fp.SetOrientationDegrees(best)
    # ---- report
    j=b.FindFootprintByReference('J1'); bb=j.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print('J1 courtyard x %.2f..%.2f y %.2f..%.2f'%tuple(map(pcbnew.ToMM,(bb.GetLeft(),bb.GetRight(),bb.GetTop(),bb.GetBottom()))),'pad A6 x %.2f'%pcbnew.ToMM(j.FindPadByNumber('A6').GetPosition().x))
    items=[]
    for f in b.GetFootprints():
        c=f.GetCourtyard(pcbnew.F_CrtYd)
        bb=c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
        items.append((f.GetReference(),pcbnew.ToMM(bb.GetLeft()),pcbnew.ToMM(bb.GetTop()),pcbnew.ToMM(bb.GetRight()),pcbnew.ToMM(bb.GetBottom())))
    ov=[]
    for i,a in enumerate(items):
        if a[1]<X0-0.6 or a[3]>X1+0.01 or a[2]<Y0 or a[4]>Y1: print('OUTSIDE',a[0],[round(v,2) for v in a[1:]])
        for c in items[i+1:]:
            w=min(a[3],c[3])-max(a[1],c[1]); h=min(a[4],c[4])-max(a[2],c[2])
            if w>0.01 and h>0.01: ov.append((a[0],c[0],round(w,2),round(h,2)))
    print('courtyard overlaps:',len(ov)); [print(' ',o) for o in ov]
    pcbnew.SaveBoard('mini-reef.kicad_pcb',b); pcbnew.SaveBoard('stage1.kicad_pcb',b)
