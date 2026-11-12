"""Parse a KiCad netlist (kicad-cli sch export netlist) into components and nets."""
import re
def parse(path):
    t=open(path).read()
    comps={}
    for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)\s*\(footprint "([^"]*)"\)(.*?)\(tstamps ((?:"[^"]+"\s*)+)\)',t,re.S):
        l=re.search(r'\(name "LCSC"\) "([^"]*)"',m.group(4))
        fields=dict(re.findall(r'\(field\s*\(name "([^"]+)"\)\s*"([^"]*)"\)',m.group(4)))
        comps[m.group(1)]=dict(value=m.group(2),fp=m.group(3),lcsc=l.group(1) if l else '',ts=re.findall(r'"([^"]+)"',m.group(5)),
                               fields=fields,nobom='(name "exclude_from_bom")' in m.group(4))
    nets={}; padnet={}
    for m in re.finditer(r'\(net\s*\(code "\d+"\)\s*\(name "([^"]+)"\)(.*?)(?=\n\t\t\(net\b|\Z)',t,re.S):
        for r,p in re.findall(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)',m.group(2)):
            padnet[(r,p)]=m.group(1); nets.setdefault(m.group(1),[]).append((r,p))
    return comps,nets,padnet
