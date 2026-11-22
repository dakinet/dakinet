"""Leva strana RP2040 posle novog flash-a: DVDD pin 50 preko via levo od C30, pinovi 48/49 -> C30, GND via C30/C34."""
from rucno_alat import *
import rucni_vodovi
b = ploca()
def stari_dvdd50(v):
    if v[0] != 'DVDD':
        return False
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return any(abs(x - 112.6) < 0.05 and 134.4 <= y <= 137.3 for x, y in pts) or \
        any(abs(x - 112.9) < 0.05 and abs(y - 137.2) < 0.05 for x, y in pts)
V = [v for v in rucni_vodovi.RUCNI if not stari_dvdd50(v)]
print('uklonjeno starih DVDD (pin 50):', len(rucni_vodovi.RUCNI) - len(V))
# DVDD pin 50 -> via levo od C30 -> B do DVDD magistrale (via iznad C34)
V.append(vod('DVDD', 'F', 0.2, [('U7', '50'), (109.4, 137.2), (109.4, 137.05)], b)); V.append(via('DVDD', (109.4, 137.05)))
V.append(vod('DVDD', 'B', 0.25, [(109.4, 137.05), (109.4, 133.7), (111.8, 133.7)], b))
# +3V3 pinovi 48/49 spojeni i na C30
V.append(vod('+3V3', 'F', 0.25, [('U7', '48'), (113.25, 136.4), (113.25, 136.8), ('U7', '49')], b))
V.append(vod('+3V3', 'F', 0.25, [(113.25, 136.6), ('C30', '1')], b))
# mase C30 i C34
V.append(vod('GND', 'F', 0.3, [('C30', '2'), (110.1, 136.6)], b)); V.append(via('GND', (110.1, 136.6)))
V.append(vod('GND', 'F', 0.3, [('C34', '2'), (110.0, 134.7)], b)); V.append(via('GND', (110.0, 134.7)))
ok, r = primeni(None, V, 'leva strana RP2040: DVDD pin 50, +3V3 48/49 na C30, mase C30/C34')
if ok:
    slika(r, (104, 130, 124, 142))
