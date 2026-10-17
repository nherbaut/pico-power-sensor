"""Write a scratch copy of a KiCad 9 board with numeric (net N) references
rewritten as (net "name"), for copper_guards.py (which reads KiCad 10 syntax).
Geometry is unchanged. Usage: python3 netnames_for_guard.py IN.kicad_pcb OUT.kicad_pcb
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
t = open(src).read()
table = dict(re.findall(r'\(net (\d+) "([^"]*)"\)', t[:t.index('(footprint')]))
if not table:
    sys.exit("no net table found")
open(dst, "w").write(re.sub(r'\(net (\d+)\)', lambda m: '(net "%s")' % table[m.group(1)], t))
print(len(table), "nets")
