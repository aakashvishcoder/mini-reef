"""Report HyperBus / USB lengths and a matching score for the board in the current work dir."""
import pcbnew,collections
b=pcbnew.LoadBoard('mini-reef.kicad_pcb')
L=collections.Counter(); V=collections.Counter()
for t in b.GetTracks():
    if t.GetClass()=='PCB_VIA': V[t.GetNetname()]+=1
    else: L[t.GetNetname()]+=pcbnew.ToMM(t.GetLength())
# a via adds ~1.6 mm of board thickness to the path
E_=lambda n:L[n]+1.6*(V[n]//2*2>0)*0+ (1.6 if V[n] else 0)
dq=[E_(f'/HR_DQ{i}') for i in range(8)]+[E_('/HR_RWDS')]
ck=abs(E_('/HR_CK')-E_('/HR_CK_N')); spread=max(dq)-min(dq); ckd=abs((E_('/HR_CK')+E_('/HR_CK_N'))/2-sum(dq)/len(dq))
usb=abs(L['USB_DP']-L['USB_DN'])
print('SCORE %.1f | CK/CK# skew %.1f mm | DQ+RWDS spread %.1f mm (%.1f..%.1f) | clock-to-data %.1f mm | USB %.1f/%.1f mm'%(3*ck+spread+0.5*ckd+2*usb+0.2*max(L['USB_DP'],L['USB_DN']),ck,spread,min(dq),max(dq),ckd,L['USB_DP'],L['USB_DN']))
