"""Korak 2b: analogni deo boost-a prati redosled pinova (COMP | FB | FREQ), SS kratko preko via."""
from rucno_alat import *
import rucni_vodovi
ANALOG = {'BFB', 'COMP', 'CC', 'FREQ', 'SS'}
V = [v for v in rucni_vodovi.RUCNI if v[0] not in ANALOG]
# ukloni GND via/vodove rutera kod analognih delova (biće ponovo napravljeni uz nova mesta)
def u_oblasti(v):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return v[0] == 'GND' and pts and all(113.0 <= x <= 121.9 and 110.0 <= y <= 121.5 for x, y in pts)
V = [v for v in V if not u_oblasti(v)]
poz = {'R4': (115.2, 116.2, 0), 'C7': (115.2, 117.8, 0), 'C6': (115.2, 119.4, 0),
       'R2': (118.3, 116.2, 0), 'R1': (118.3, 117.8, 180), 'R3': (120.6, 116.6, 270)}
ok, b = primeni(poz, V, 'korak 2b: analogni deo boost-a po redosledu pinova COMP | FB | FREQ')
if ok:
    # SS: via tik iznad SS pina (između AGND i VIN), donjim slojem do C8 levo
    V2 = list(__import__('rucni_vodovi').RUCNI)
    V2.append(vod('SS', 'F', 0.2, [('U1', '5'), (120.35, 106.4)], b)); V2.append(via('SS', (120.35, 106.4)))
    V2.append(vod('SS', 'B', 0.2, [(120.35, 106.4), (118.2, 106.4), (118.2, 112.6), (118.2, 112.9)], b)); V2.append(via('SS', (118.2, 112.9)))
    V2.append(vod('SS', 'F', 0.2, [(118.2, 112.9), ('C8', '1')], b))
    ok, b = primeni(None, V2, 'korak 2b: SS kratko (via uz pin, donji sloj ispod analogne polovine U1)')
if ok:
    ok, r = ruter_korak([(n, [0.2], dict(prioritet=1)) for n in ('BFB', 'COMP', 'CC', 'FREQ')],
                        'korak 2b: FB, COMP, CC, FREQ', gnd_refs=['R2', 'R3', 'C6', 'C7', 'C8'])
    if ok:
        slika(r, (108, 100, 132, 124))
