"""Desna grupa RP2040: PRAG/RUN/SWDIO/SWCLK stepenasto na via -> B; XOUT vodoravno na R32; kristal 1,1 mm niže."""
from rucno_alat import *
import rucni_vodovi
GR = {'PRAG', 'RUN', 'SWDIO', 'SWCLK', 'XOUT', 'XIN', 'XO'}
def kristal_gnd(v):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return v[0] == 'GND' and pts and all(122.5 <= x <= 129 and 136.5 <= y <= 145 for x, y in pts)
V = [v for v in rucni_vodovi.RUCNI if v[0] not in GR and not kristal_gnd(v)]
print('uklonjeno:', len(rucni_vodovi.RUCNI) - len(V))
poz = {'R32': (124.5, 137.3, 0), 'Y1': (125.0, 140.0, 0), 'C27': (128.2, 140.0, 270), 'C26': (123.7, 143.5, 270),
       'R31': (130.2, 143.6, 0)}
ok, b = primeni(poz, V, 'desna grupa RP2040: R32 dole, kristal niže, R31 ka letvici')
if not ok:
    raise SystemExit(1)
V = list(__import__('importlib').reload(rucni_vodovi).RUCNI)
W = 0.2
stepen = [('PRAG', 27, (121.4, 134.3)), ('RUN', 26, (122.2, 134.85)), ('SWDIO', 25, (123.0, 135.4)), ('SWCLK', 24, (123.8, 135.95))]
for net, pin, (xv, yv) in stepen:
    y = pad(b, 'U7', str(pin))[1]
    V.append(vod(net, 'F', W, [('U7', str(pin)), (xv, y), (xv, yv)], b))
    V.append(via(net, (xv, yv)))
V.append(vod('XOUT', 'F', W, [('U7', '21'), ('R32', '1')], b))
V.append(vod('XO', 'F', W, [('R32', '2'), (pad(b, 'Y1', '3')[0], pad(b, 'R32', '2')[1]), ('Y1', '3')], b))
V.append(vod('XO', 'F', W, [('Y1', '3'), ('C27', '1')], b))
V.append(vod('XIN', 'F', W, [('U7', '20'), (121.6, 137.6), (122.2, 138.2), (122.2, pad(b, 'Y1', '1')[1]), ('Y1', '1')], b))
V.append(vod('XIN', 'F', W, [('Y1', '1'), ('C26', '1')], b))
V.append(vod('GND', 'F', 0.3, [('Y1', '4'), ('Y1', '2')], b))
V.append(vod('GND', 'F', 0.3, [('Y1', '2'), ('C27', '2')], b))
x27, y27 = pad(b, 'C27', '2'); V.append(vod('GND', 'F', 0.3, [('C27', '2'), (x27, y27 + 0.9)], b)); V.append(via('GND', (x27, y27 + 0.9)))
x26, y26 = pad(b, 'C26', '2'); V.append(vod('GND', 'F', 0.3, [('C26', '2'), (x26, y26 + 0.9)], b)); V.append(via('GND', (x26, y26 + 0.9)))
ok, r = primeni(None, V, 'desna grupa: stepenasti izlazi PRAG/RUN/SWDIO/SWCLK, XOUT na R32, kristal')
if ok:
    slika(r, (116, 130, 134, 148))
