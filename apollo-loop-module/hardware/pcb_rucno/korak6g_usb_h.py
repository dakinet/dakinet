"""USB par do letvice: R34 okrenut (DM_H pad uz DP_H), USB_DM prilagođen, VIN van oblasti USB otpornika."""
from rucno_alat import *
import rucni_vodovi
def vin_ovde(v):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return v[0] == 'VIN' and pts and any(103.0 <= x <= 112.5 and 124.0 <= y <= 137.5 for x, y in pts)
V = [v for v in rucni_vodovi.RUCNI if not vin_ovde(v) and v[0] not in ('USB_DM', 'DM_H')]
print('uklonjeno:', len(rucni_vodovi.RUCNI) - len(V))
ok, b = primeni({'R34': (108.6, 131.6, 180)}, V, 'R34 okrenut (DM_H uz DP_H); VIN van USB oblasti')
if not ok:
    raise SystemExit(1)
b = ploca()
V = list(__import__('importlib').reload(rucni_vodovi).RUCNI)
def v33_ovde(v):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return v[0] == '+3V3' and pts and all(104.0 <= x <= 111.9 and 131.0 <= y <= 133.6 for x, y in pts)
print('uklonjeno +3V3 kod R34:', sum(1 for v in V if v33_ovde(v)))
V = [v for v in V if not v33_ovde(v)]
V.append(vod('USB_DM', 'F', 0.2, [('U7', '46'), (109.4, 135.6), (109.4, 132.3), ('R34', '1')], b))
ok, b = primeni(None, V, 'USB_DM do R34 (okrenut)')
if ok:
    ok, r = ruter_korak([('DM_H', [0.2], dict(prioritet=2, cena_B=1.2, cena_via=0.8)),
                         ('+3V3', [0.4, 0.3, 0.25], dict(prioritet=2, cena_B=1.8))], 'DM_H uz DP_H do letvice; +3V3')
if ok:
    ok, r = ruter_korak([('VIN', [0.8, 0.6], dict(prioritet=2, cena_B=1.5, cena_via=1.0))], 'VIN zaobilazno (van USB oblasti)',
                        skupi_prstenovi=[((103.0, 124.0, 112.5, 137.5), (0, 0, 0, 0), 25.0)])
if ok:
    slika(r, (100, 100, 176, 154), mreze_oznake=False)
