"""Donji GPIO izlazi RP2040 kao ugnežđena L slova: najdesniji pin skreće prvi (gore), najlevlji ide najdublje."""
from rucno_alat import *
import rucni_vodovi
b = ploca()
GP = ['TX', 'RX', 'NIVO', 'EN_N', 'BIT', 'OC_RST', 'OCP', 'DP_H', 'DM_H']
def c28_gnd(v):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return v[0] == 'GND' and pts and all(abs(x - 118.7) < 0.05 and 142.5 <= y <= 143.7 for x, y in pts)
V = [v for v in rucni_vodovi.RUCNI if v[0] not in GP and not c28_gnd(v)]
print('uklonjeno:', len(rucni_vodovi.RUCNI) - len(V))
pass  # C28 GND via već postoji
traka = {'OCP': 143.4, 'OC_RST': 144.0, 'BIT': 144.6, 'EN_N': 145.2, 'NIVO': 145.8, 'RX': 146.4, 'TX': 147.0}
pin = {'TX': 2, 'RX': 3, 'NIVO': 4, 'EN_N': 5, 'BIT': 6, 'OC_RST': 7, 'OCP': 8}
for n, y in traka.items():
    x = pad(b, 'U7', str(pin[n]))[0]
    V.append(vod(n, 'F', 0.2, [('U7', str(pin[n])), (x, y), (120.3, y)], b))
ok, r = primeni(None, V, 'GPIO trake ispod RP2040 (ugneždeno, korak 0,6 mm)')
if ok:
    slika(r, (108, 132, 132, 150))
