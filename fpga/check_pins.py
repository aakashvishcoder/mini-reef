#!/usr/bin/env python3
"""Check the board's FPGA pinout against AMD's package pin file (xc7a15tftg256pkg.txt).

  kicad-cli sch export netlist -o /tmp/mini-reef.net mini-reef.kicad_sch
  python3 fpga/check_pins.py /tmp/mini-reef.net xc7a15tftg256pkg.txt [xc7a35tftg256pkg.txt]

This is a paper check of the rules Vivado's I/O planner enforces. It does not replace a Vivado build.
"""
import re, sys
def pkg(path):
    d = {}
    for line in open(path):
        f = line.split()
        if len(f) >= 8 and re.match(r'[A-T]\d+$', f[0]): d[f[0]] = dict(name=f[1], grp=f[2], bank=f[3], type=f[6], nc=f[7])
    return d
A = pkg(sys.argv[2])
t = open(sys.argv[1]).read()
board = {}        # ball -> (net, pin name in the KiCad symbol)
for m in re.finditer(r'\(net\s*\(code "\d+"\)\s*\(name "([^"]+)"\)(.*?)(?=\n\t\t\(net\b|\Z)', t, re.S):
    for n in re.finditer(r'\(node\s*\(ref "U4"\)\s*\(pin "([^"]+)"\)\s*\(pinfunction "([^"]+)"\)', m.group(2)):
        board[n.group(1)] = (m.group(1).lstrip('/'), re.sub(rf'_{n.group(1)}$', '', n.group(2)))
bad = []; ok = 0
def check(cond, msg):
    global ok
    if cond: ok += 1
    else: bad.append(msg)
check(set(board) == set(A), f'ball sets differ: {sorted(set(board) ^ set(A))[:10]}')
for ball, (net, name) in board.items(): check(A[ball]['name'] == name, f'{ball}: symbol says {name}, AMD says {A[ball]["name"]}')
# ---- supplies
RAIL = {'VCCINT': '+1V0', 'VCCBRAM': '+1V0', 'VCCAUX': '+1V8', 'VCCADC_0': '+1V8', 'GND': 'GND', 'GNDADC_0': 'GND', 'VCCBATT_0': 'GND',
        'VCCO_0': '+3V3', 'VCCO_14': '+3V3', 'VCCO_15': '+3V3', 'VCCO_34': '+3V3', 'VCCO_35': '+1V8'}
for ball, a in A.items():
    if a['name'] in RAIL: check(board[ball][0] == RAIL[a['name']], f'{ball} {a["name"]} is on {board[ball][0]}, expected {RAIL[a["name"]]}')
VCCO = {'14': 3.3, '15': 3.3, '34': 3.3, '35': 1.8, '0': 3.3}
sig = {net: ball for ball, (net, name) in board.items() if A[ball]['name'].startswith('IO_') and not net.startswith('unconnected') and net not in RAIL.values()}
for net, ball in sig.items(): check(A[ball]['nc'] == 'NA', f'{net} on {ball}: not bonded on this device')
# ---- HyperBus: one bank, one byte group, right pin types
hr = {n: b for n, b in sig.items() if n.startswith('HR_')}
check(len(hr) == 13, f'expected 13 HyperBus signals, found {len(hr)}')
check({A[b]['bank'] for b in hr.values()} == {'35'}, 'HyperBus not all in bank 35')
cap = [n for n in hr if n != 'HR_RST_N']
check({A[hr[n]]['grp'] for n in cap} == {'1'}, f'HyperBus capture pins not all in byte group T1: { {n: A[hr[n]]["grp"] for n in cap} }')
check('MRCC' in A[hr['HR_RWDS']]['name'] or 'SRCC' in A[hr['HR_RWDS']]['name'] or 'DQS' in A[hr['HR_RWDS']]['name'], 'RWDS is not on a clock- or strobe-capable pin')
p, n = A[hr['HR_CK']]['name'], A[hr['HR_CK_N']]['name']
check(re.sub(r'L(\d+)P', r'L\1N', p) == n, f'CK/CK# are not the P/N halves of one pair: {p} / {n}')
# ---- clock, config, strap pins
check(re.search(r'L\d+P_T\d_[MS]RCC', A[sig['CLK50']]['name']), f'CLK50 is not on the P side of a clock-capable pair: {A[sig["CLK50"]]["name"]}')
for net, key in (('FLASH_DQ0', 'D00_MOSI'), ('FLASH_DQ1', 'D01_DIN'), ('FLASH_DQ2', 'D02'), ('FLASH_DQ3', 'D03'), ('FLASH_CS_N', 'FCS_B')):
    check(key in A[sig[net]]['name'], f'{net} is on {A[sig[net]]["name"]}, needs the {key} pin')
byname = {a['name']: b for b, a in A.items()}
for name, want in (('M0_0', '+3V3'), ('M1_0', 'GND'), ('M2_0', 'GND'), ('CFGBVS_0', '+3V3'), ('CCLK_0', 'FLASH_CLK'), ('TCK_0', 'JTAG_TCK'), ('TMS_0', 'JTAG_TMS'),
                   ('TDI_0', 'JTAG_TDI'), ('TDO_0', 'JTAG_TDO'), ('PROGRAM_B_0', 'PROGRAM_B'), ('INIT_B_0', 'INIT_B')):
    check(board[byname[name]][0] == want, f'{name} is on {board[byname[name]][0]}, expected {want}')
pudc = [b for b, a in A.items() if 'PUDC_B' in a['name']][0]; check(board[pudc][0] == 'GND', 'PUDC_B is not tied low')
# ---- I/O standard vs bank supply (from the XDC)
xdc = open('fpga/mini-reef.xdc').read(); nx = 0
for m in re.finditer(r'^set_property -dict \{PACKAGE_PIN (\S+)\s+IOSTANDARD LVCMOS(\d\d)\}', xdc, re.M):
    nx += 1; check(float(m.group(2)) / 10 == VCCO[A[m.group(1)]['bank']], f'XDC: {m.group(1)} is LVCMOS{m.group(2)} but bank {A[m.group(1)]["bank"]} is {VCCO[A[m.group(1)]["bank"]]} V')
    check(m.group(1) in sig.values(), f'XDC: {m.group(1)} is not a signal ball on the board')
check(nx == 35, f'expected 35 active XDC pins, found {nx}')
# ---- drop-in device
if len(sys.argv) > 3:
    B = pkg(sys.argv[3]); diff = [b for b in A if (A[b]['name'], A[b]['bank'], A[b]['grp']) != (B.get(b, {}).get('name'), B.get(b, {}).get('bank'), B.get(b, {}).get('grp'))]
    check(not diff, f'pinout differs between the two devices at {diff[:8]}')
    check(all(B[b]['nc'] == 'NA' for b in sig.values()), 'a used signal ball is not bonded on the second device')
print(f'{ok} checks passed, {len(bad)} failed  ({len(board)} balls, {len(sig)} signals)')
for b_ in bad: print('  FAIL', b_)
print('HyperBus pins:', ', '.join(f'{n[3:]}={hr[n]}({A[hr[n]]["name"].replace("IO_","").replace("_35","")})' for n in sorted(hr)))
