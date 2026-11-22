"""GPIO izlazi sa donjeg reda RP2040: C40 van prolaza, uklanjanje ruterovih vodova iz pojasa, ručni vertikalni izlazi."""
from rucno_alat import *
import rucni_vodovi
b = ploca()
UKLONI = {'BIT', 'DP_H', 'OC_RST', 'RUN', 'TX', 'RX', 'NIVO', 'EN_N', 'OCP', 'SWCLK', 'SWDIO', 'DM_H'}
def u_pojasu(v):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return any(112.8 <= x <= 136 and 143.3 <= y <= 148.7 for x, y in pts)
V = [v for v in rucni_vodovi.RUCNI if v[0] not in UKLONI and not (v[0] == '+3V3' and v[1] and v[1][0][5] >= 0.4 and u_pojasu(v))]
print('uklonjeno:', len(rucni_vodovi.RUCNI) - len(V))
ok, b = primeni({'C40': (119.2, 131.85, 90)}, V, 'C40 uz C29; GPIO pojas ispod RP2040 očišćen')
if not ok:
    raise SystemExit(1)
import importlib, rucni_vodovi as _rv
importlib.reload(_rv)
def u_prolazu(v):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return any(114.6 <= x <= 117.5 and 140.9 <= y <= 143.6 for x, y in pts)
V = [v for v in _rv.RUCNI if not (v[0] == '+3V3' and u_prolazu(v))]
print('uklonjeno +3V3 iz prolaza:', len(_rv.RUCNI) - len(V))
V.append(vod('+3V3', 'F', 0.25, [('C40', '1'), ('C29', '1')], b))
V.append(vod('GND', 'F', 0.3, [('C40', '2'), (119.2, 130.55)], b)); V.append(via('GND', (119.2, 130.55)))
# ručni izlazi: pinovi 2-8 pravo nadole do y = 143.2 (korak 0,4 mm, 0,2 mm vodovi)
for pin, net in ((2, 'TX'), (3, 'RX'), (4, 'NIVO'), (5, 'EN_N'), (6, 'BIT'), (7, 'OC_RST'), (8, 'OCP')):
    x, y = pad(b, 'U7', str(pin))
    V.append(vod(net, 'F', 0.2, [('U7', str(pin)), (x, 143.2)], b))
ok, r = primeni(None, V, 'ručni GPIO izlazi sa donjeg reda RP2040')
if ok:
    slika(r, (110, 132, 146, 154))
