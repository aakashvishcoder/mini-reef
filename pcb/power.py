"""Stage 2: inner-layer planes, and a via for every power/ground SMD pad. Run from pcb/work."""
import pcbnew,math,sys,json
sys.path.insert(0,'..'); from place import X0,Y0,X1,Y1,FX,FY,HOLES,PLANES
MM=pcbnew.FromMM; mm=pcbnew.ToMM
def V(x,y): return pcbnew.VECTOR2I(MM(x),MM(y))
# power class clearance 0.15 so 0.4 mm tracks can leave the 0.5 mm-pitch QFN pins
p=json.load(open('mini-reef.kicad_pro'))
for c in p['net_settings']['classes']:
    if c['name']=='Power': c['clearance']=0.15
json.dump(p,open('mini-reef.kicad_pro','w'),indent=2)
b=pcbnew.LoadBoard('stage1.kicad_pcb')
# ---------------- In2 power regions (rectangles; later entries win)
R18=[(100.5,100.5,142,113.9),(116.5,113.9,142,118.5),(116.5,118.5,140,123.5),(116.5,123.5,137.5,127.5),      # main: U2, HyperRAM, bank 35
     (139,FY-5.5,FX+3.5,FY-3.5),(FX+2.5,FY-3.5,FX+3.5,FY-1.5),(FX+1.5,FY-1.5,FX+3.5,FY+3.5)]                 # strip round to VCCAUX
R10=[(100.5,114.1,116.5,127.6),(114.5,121,120,134),(114.5,128,133.2,134),(132,FY+0.5,FX-3.4,FY+2.5),         # U1 + corridor
     (FX-3.5,FY-3.5,FX+1.5,FY+2.5),(FX+1.5,FY-3.5,FX+2.5,FY-2.5)]                                            # VCCINT/VCCBRAM block
def inr(rs,x,y): return any(a<=x<=c and e<=y<=d for a,e,c,d in rs)
def region(x,y): return '+1V0' if inr(R10,x,y) else '+1V8' if inr(R18,x,y) else '+3V3'
def region_ok(net,x,y,m=0.36):
    return net=='GND' or all(region(x+dx,y+dy)==net for dx in (-m,m) for dy in (-m,m))
def poly(rects):
    ps=pcbnew.SHAPE_POLY_SET()
    for r in rects:
        q=pcbnew.SHAPE_POLY_SET(); q.NewOutline()
        for x,y in ((r[0],r[1]),(r[2],r[1]),(r[2],r[3]),(r[0],r[3])): q.Append(MM(x),MM(y))
        ps.BooleanAdd(q)
    return ps
def zone(net,layer,ps,prio,name):
    z=pcbnew.ZONE(b); z.SetLayer(layer); z.SetNetCode(b.GetNetcodeFromNetname(net)); z.SetZoneName(name)
    z.Outline().BooleanAdd(ps)
    z.SetAssignedPriority(prio); z.SetLocalClearance(MM(0.15)); z.SetMinThickness(MM(0.15))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL); z.SetThermalReliefGap(MM(0.2)); z.SetThermalReliefSpokeWidth(MM(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS); b.Add(z); return z
FULL=[(X0-1,Y0-1,X1+1,Y1+1)]
p10=poly(R10); p18=poly(R18); p18.BooleanSubtract(p10); p33=poly(FULL)
zone('GND',pcbnew.In1_Cu,poly(FULL),0,'GND plane')
zone('+3V3',pcbnew.In2_Cu,p33,0,'3V3 plane'); zone('+1V8',pcbnew.In2_Cu,p18,1,'1V8 plane'); zone('+1V0',pcbnew.In2_Cu,p10,2,'1V0 plane')
# ---------------- obstacle model
pads=[]      # (x0,y0,x1,y1,net,ref)
for f in b.GetFootprints():
    for q in f.Pads():
        bb=q.GetBoundingBox(); pads.append((mm(bb.GetLeft()),mm(bb.GetTop()),mm(bb.GetRight()),mm(bb.GetBottom()),q.GetNetname(),f.GetReference(),q))
vias=[]      # (x,y,r,net)
def rdist(r,x,y):
    dx=max(r[0]-x,0,x-r[2]); dy=max(r[1]-y,0,y-r[3]); return math.hypot(dx,dy)
def via_ok(x,y,r,net,own):
    if not (X0+0.7<=x<=X1-0.7 and Y0+0.7<=y<=Y1-0.7): return False
    if any(math.hypot(x-hx,y-hy)<3.6+r for hx,hy in HOLES): return False
    for pd in pads:
        if pd[6] is own: continue
        d=rdist(pd,x,y)
        if d < r+(0.1 if pd[4]==net else 0.16): return False
    for vx,vy,vr,vn in vias:
        if math.hypot(x-vx,y-vy) < r+vr+(0.15 if vn==net else 0.2): return False
    return True
def seg_ok(a,c,w,net,own):
    n=max(2,int(math.hypot(c[0]-a[0],c[1]-a[1])/0.1))
    for i in range(n+1):
        x=a[0]+(c[0]-a[0])*i/n; y=a[1]+(c[1]-a[1])*i/n
        for pd in pads:
            if pd[6] is own or pd[4]==net: continue
            if rdist(pd,x,y)<w/2+0.15: return False
    return True
def add_via(x,y,d,h,net):
    v=pcbnew.PCB_VIA(b); v.SetPosition(V(x,y)); v.SetWidth(pcbnew.F_Cu,MM(d)); v.SetDrill(MM(h)); v.SetNetCode(b.GetNetcodeFromNetname(net))
    v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); vias.append((x,y,d/2,net))
def add_track(a,c,w,net,layer=pcbnew.F_Cu):
    t=pcbnew.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNetCode(b.GetNetcodeFromNetname(net)); b.Add(t)
orph=[]
# ---------------- BGAs: dog-bone vias on the diagonal grid
def bga(ref,d,h,force={},forbid=()):
    f=b.FindFootprintByReference(ref); taken=set(forbid)
    todo=[q for q in f.Pads() if q.GetNetname() in PLANES]
    todo.sort(key=lambda q:(q.GetNumber() not in force,q.GetNetname()=='GND'))      # rails first (fewer legal cells), GND last
    for q in todo:
        net=q.GetNetname(); x,y=mm(q.GetPosition().x),mm(q.GetPosition().y)
        c=[force[q.GetNumber()]] if q.GetNumber() in force else [(round(x+dx,3),round(y+dy,3)) for dx,dy in ((-.5,-.5),(.5,-.5),(-.5,.5),(.5,.5))]
        c=[k for k in c if k not in taken and (q.GetNumber() in force or region_ok(net,*k)) and via_ok(k[0],k[1],d/2,net,q)]
        if not c: orph.append((ref,q.GetNumber(),net)); continue
        k=c[0]; taken.add(k); add_via(k[0],k[1],d,h,net); add_track((x,y),k,0.2,net)
g=lambda dx,dy:(round(FX+dx,3),round(FY+dy,3))
# two rail balls sit inside another rail's region: G8 (VCCADC, +1V8) and E7 (CFGBVS, +3V3). Link them on the bottom layer.
bga('U4',0.45,0.2,force={'G8':g(0,-1),'G10':g(2,-1),'E7':g(-1,-4),'C10':g(1,-6),'E9':g(0,-3),'F9':g(0,-2),'G9':g(1,-2),'E10':g(1,-3)},forbid=[g(1,-1),g(0,-4),g(1,-4),g(1,-5)])
add_track(g(0,-1),g(2,-1),0.2,'+1V8',pcbnew.B_Cu)
add_track(g(-1,-4),g(1,-4),0.2,'+3V3',pcbnew.B_Cu); add_track(g(1,-4),g(1,-6),0.2,'+3V3',pcbnew.B_Cu)
bga('U5',0.45,0.2)
# ---------------- regulators: ground pins straight into the thermal pad
for ref in ('U1','U2','U3'):
    f=b.FindFootprintByReference(ref); cx,cy=mm(f.GetPosition().x),mm(f.GetPosition().y)
    for q in f.Pads():
        if q.GetNetname()=='GND' and q.GetNumber() in ('6','7','8','15','16'):
            x,y=mm(q.GetPosition().x),mm(q.GetPosition().y); add_track((x,y),(x,cy+(0.5 if y>cy else -0.5)),0.2,'GND')
# ---------------- everything else: a via beside each power/ground pad
done=set(); nvia=0
for f in b.GetFootprints():
    ref=f.GetReference()
    if ref in ('U4','U5'): continue
    cx,cy=mm(f.GetPosition().x),mm(f.GetPosition().y)
    for q in f.Pads():
        net=q.GetNetname()
        if net not in PLANES or q.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD or not q.GetNumber(): continue
        if ref in ('U1','U2','U3') and (q.GetNumber()=='17' or net=='GND'): continue
        x,y=mm(q.GetPosition().x),mm(q.GetPosition().y); key=(round(x,2),round(y,2),net)
        if key in done: continue
        done.add(key)
        bb=q.GetBoundingBox(); hx,hy=mm(bb.GetWidth())/2,mm(bb.GetHeight())/2
        want=2 if hx*hy*4>=1.2 else 1; r=0.25; got=0
        ox,oy=x-cx,y-cy
        cand=[]
        for ex in (0.1,0.5,1.0):
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
                px=x+dx*(hx+ex+r) if dx else x; py=y+dy*(hy+ex+r) if dy else y
                if dx and dy: px,py=x+dx*(hx+ex*0.5+r*0.8),y+dy*(hy+ex*0.5+r*0.8)
                cand.append((-(dx*ox+dy*oy)/(math.hypot(dx,dy))+ex*2,px,py))      # prefer pointing away from the part centre, and close
        for _,px,py in sorted(cand):
            w=min(0.3,2*min(hx,hy))
            if region_ok(net,px,py) and via_ok(px,py,r,net,q) and seg_ok((x,y),(px,py),w,net,q):
                add_via(px,py,0.5,0.3,net); add_track((x,y),(px,py),w,net); got+=1; nvia+=1
                if got==want: break
        if not got: orph.append((ref,q.GetNumber(),net))
print('vias placed:',len(vias),'| pads without a plane via:',orph)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard('stage2.kicad_pcb',b)
