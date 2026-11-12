"""Summarise a kicad-cli DRC json: python3 drcsum.py drc.json [show-types...]"""
import json,collections,sys,re
d=json.load(open(sys.argv[1])); show=sys.argv[2:]
print('violations',collections.Counter(v['type'] for v in d['violations']).most_common())
un=d.get('unconnected_items',[]); c=collections.Counter()
for u in un:
    m=re.search(r'\[([^\]]+)\]',u['items'][0]['description']); c[m.group(1) if m else '?']+=1
print('unconnected',len(un),'nets',len(c),[(k,v) for k,v in c.items() if k in('GND','+3V3','+1V8','+1V0')])
for v in d['violations']:
    if v['type'] in show: print(' ',v['type'],'|',v['description'][:70],'|',' ; '.join(i['description'][:60]+' @%.2f,%.2f'%(i['pos']['x'],i['pos']['y']) for i in v['items']))
if 'unconnected' in show:
    for u in un: print('  UNC',' | '.join(i['description'][:70] for i in u['items']))
