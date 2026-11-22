"""Korak 1 (ponovo): QSPI svih 6 vodova na F.Cu, bez via. Flash dole-levo okrenut 90°.
Gornji red flash-a (VCC, QSD3, QSCLK, QSD0) penje se u pinove 51-53; donji red (QSS, QSD1, QSD2) obilazi ispod
flash-a i ulazi odozdo u pinove 54-56 (ugneždeno: QSD2 unutra, QSS spolja – bez ukrštanja)."""
from rucno_alat import *
import rucni_vodovi
ok, b = primeni({'U8': (108.0, 142.75, 90), 'C25': (106.1, 136.5, 90), 'R29': (103.6, 145.2, 270), 'R30': (103.6, 148.6, 270)},
                None, 'flash 0,15 mm niže; C25 iznad VCC; R29/R30 uz QSS')
if not ok:
    raise SystemExit(1)
W = 0.2
U8 = lambda n: ('U8', str(n))
U7 = lambda n: ('U7', str(n))
y8 = pad(b, 'U8', '7')[1]           # gornji red
yb = pad(b, 'U8', '2')[1]           # donji red
V = list(rucni_vodovi.RUCNI)
# gornji red -> 51, 52, 53
V.append(vod('QSD3', 'F', W, [U8(7), (pad(b, 'U8', '7')[0], 137.6), U7(51)], b))
V.append(vod('QSCLK', 'F', W, [U8(6), (pad(b, 'U8', '6')[0], 138.0), U7(52)], b))
V.append(vod('QSD0', 'F', W, [U8(5), (pad(b, 'U8', '5')[0], 138.4), U7(53)], b))
# donji red -> 54, 55, 56 (obilazak ispod flash-a)
for net, pin, y_ispod, x_gore, cilj, y_cilj in (('QSD2', 3, yb + 1.25, 111.55, 54, 138.8),
                                                ('QSD1', 2, yb + 1.7, 112.0, 55, 139.2),
                                                ('QSS', 1, yb + 2.15, 112.45, 56, 139.6)):
    x = pad(b, 'U8', str(pin))[0]
    V.append(vod(net, 'F', W, [U8(pin), (x, y_ispod), (x_gore, y_ispod), (x_gore, y_cilj), U7(cilj)], b))
# VCC flash-a -> C25 tik iznad; masa C25 i pina 4 kroz via
V.append(vod('+3V3', 'F', 0.25, [U8(8), ('C25', '1')], b))
V.append(vod('GND', 'F', 0.3, [('C25', '2'), (106.1, 134.8)], b)); V.append(via('GND', (106.1, 134.8)))
V.append(vod('GND', 'F', 0.3, [U8(4), (110.95, 145.4)], b)); V.append(via('GND', (110.95, 145.4)))
ok, r = primeni(None, V, 'korak 1: QSPI svih 6 vodova na F.Cu, bez via')
if ok:
    slika(r, (100, 130, 124, 152))
