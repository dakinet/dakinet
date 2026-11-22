"""PRAG/RUN/SWDIO/SWCLK stepenasto na via (ručno), R32 1 mm desno, XOUT/XO ponovo; nastavci donjim slojem – ruter."""
from rucno_alat import *
import rucni_vodovi
V = [v for v in rucni_vodovi.RUCNI if v[0] not in ('PRAG', 'SWDIO', 'RUN', 'SWCLK', 'XOUT') and not (v[0] == 'XO' and any(
     s[1] < 125.3 for s in v[1]))]
ok, b = primeni({'R32': (124.4, 136.1, 0)}, V, 'R32 1 mm desno (mesto za SWD via)')
if not ok:
    raise SystemExit(1)
b = ploca()
V = list(__import__('importlib').reload(rucni_vodovi).RUCNI)
# DVDD donji sloj dublje ispod čipa (x = 120.2) da desna strana ostane slobodna; ukloni ostatak DVDD voda rutera
def dvdd_desno(v):
    if v[0] != 'DVDD':
        return False
    if any(s[0] == 'B' and abs(s[1] - 120.4) < 0.01 and abs(s[2] - 136.25) < 0.01 for s in v[1]):
        return True
    return any(s[0] == 'F' and (s[1] >= 120.9 or s[3] >= 120.9) and s[2] < 137.5 and s[4] < 137.5 for s in v[1])
V = [v for v in V if not dvdd_desno(v)]
V.append(vod('DVDD', 'B', 0.25, [(119.2, 136.25), (119.85, 136.25), (120.2, 136.6), (120.2, 140.0), (121.0, 140.8), (122.3, 140.8)], b))
W = 0.2
for net, pin, (xv, yv) in (('PRAG', 27, (121.45, 134.2)), ('RUN', 26, (122.15, 134.55)),
                           ('SWDIO', 25, (122.25, 135.75)), ('SWCLK', 24, (121.4, 136.65))):
    y = pad(b, 'U7', str(pin))[1]
    V.append(vod(net, 'F', W, [('U7', str(pin)), (xv, y), (xv, yv)], b))
    V.append(via(net, (xv, yv)))
V.append(vod('XOUT', 'F', W, [('U7', '21'), (122.0, 137.2), (122.9, 136.3), ('R32', '1')], b))
V.append(vod('XO', 'F', W, [('R32', '2'), (125.9, 136.8), ('Y1', '3')], b))
ok, b = primeni(None, V, 'SWD/RUN/PRAG stepenasti izlazi na via, XOUT/XO do R32')
if ok:
    pr = pravila()
    ok, r = ruter_korak([(n, [pr[n][1]], dict(prioritet=5, razmak=pr[n][2], cena_B=1.2, cena_via=1.0))
                         for n in ('PRAG', 'RUN', 'SWDIO', 'SWCLK', 'DM_H', 'VRET', 'FB')], 'nastavci SWD/RUN/PRAG, DM_H, VRET, FB')
    if ok:
        slika(r, (100, 100, 176, 154), mreze_oznake=False)
