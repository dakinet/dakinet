"""Korak 1g: DVDD bez kruga oko čipa – kratka B magistrala; QSS/QSD1 donji vodovi pomereni da pin 50 dobije via."""
from rucno_alat import *
import rucni_vodovi
b = ploca()
V = [v for v in rucni_vodovi.RUCNI if v[0] != 'DVDD' or (v[1] and abs(v[1][0][1] - 111.78) < 0.01 and v[1][0][5] == 0.25)]
# QSS i QSD1: novi donji (B) vodovi i QSD1 via/F ulaz
V = [v for v in V if not (v[0] in ('QSS', 'QSD1') and (
    (v[1] and v[1][0][0] == 'B') or (v[1] and v[0] == 'QSD1' and v[1][0][0] == 'F' and abs(v[1][0][1] - 111.5) < 0.01) or
    (not v[1] and v[2] and v[0] == 'QSD1' and abs(v[2][0][0] - 111.5) < 0.01)))]
V.append(vod('QSS', 'B', 0.2, [(103.4, 135.46), (111.95, 135.46), (111.95, 140.25), (112.6, 140.9)], b))
V.append(vod('QSD1', 'B', 0.2, [(103.4, 136.73), (110.7, 136.73), (111.3, 137.33), (111.3, 140.3)], b))
V.append(via('QSD1', (111.3, 140.3)))
V.append(vod('QSD1', 'F', 0.2, [(111.3, 140.3), (112.4, 139.2), ('U7', '55')], b))
# DVDD
V.append(vod('DVDD', 'F', 0.2, [('U7', '50'), (112.9, 137.2), (112.6, 137.0)], b)); V.append(via('DVDD', (112.6, 137.0)))
V.append(vod('DVDD', 'F', 0.25, [('C34', '1'), (111.8, 133.7)], b)); V.append(via('DVDD', (111.8, 133.7)))
V.append(vod('DVDD', 'B', 0.25, [(112.6, 137.0), (112.6, 134.5), (111.8, 133.7)], b))
V.append(vod('DVDD', 'B', 0.25, [(111.8, 133.7), (120.6, 133.7), (121.5, 134.6), (121.5, 136.4)], b)); V.append(via('DVDD', (121.5, 136.4)))
V.append(vod('DVDD', 'F', 0.2, [('U7', '23'), (121.5, 136.4)], b))
V.append(vod('DVDD', 'B', 0.25, [(121.5, 136.4), (121.45, 140.9)], b)); V.append(via('DVDD', (121.45, 140.9)))
V.append(vod('DVDD', 'F', 0.25, [(121.45, 140.9), ('C41', '1')], b))
V.append(vod('DVDD', 'F', 0.25, [(121.45, 140.9), ('C33', '1')], b))
ok, r = primeni(None, V, 'DVDD preko kratke B magistrale (bez kruga oko čipa)')
if ok:
    slika(r, (100, 127, 130, 146))
