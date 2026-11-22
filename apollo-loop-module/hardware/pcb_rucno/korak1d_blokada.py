"""Korak 1d: blokada RP2040 (gore/dole) i kristal – ručno nacrtani vodovi i GND via."""
from rucno_alat import *
import rucni_vodovi

postavi({'C27': (127.8, 138.8, 270)})          # XO pad prema kristalu
b = ploca()
V = list(rucni_vodovi.RUCNI)
W3, WG, WS = 0.25, 0.3, 0.2
# gornji red: IOVDD 42 i 33, levi ugao AVDD 43 i VREG_IN 44 (1 uF)
V.append(vod('+3V3', 'F', W3, [('C38', '1'), ('U7', '42')], b))
V.append(vod('+3V3', 'F', W3, [('C29', '1'), ('U7', '33')], b))
V.append(vod('+3V3', 'F', W3, [('C39', '1'), (113.2, 134.4), ('U7', '43')], b))
V.append(vod('+3V3', 'F', W3, [('C32', '1'), (111.95, 134.2), (112.55, 134.8), ('U7', '44')], b))
for c, x in (('C32', 111.95), ('C39', 113.2), ('C38', 114.4), ('C29', 118.0)):
    V.append(vod('GND', 'F', WG, [(c, '2'), (x, 130.55)], b))
    V.append(via('GND', (x, 130.55)))
# donji red: IOVDD 1 i 10
V.append(vod('+3V3', 'F', W3, [('U7', '1'), (114.4, 141.1), ('C31', '1')], b))
V.append(vod('+3V3', 'F', W3, [('U7', '10'), (118.0, 141.2), ('C28', '1')], b))
for c, x in (('C31', 113.4), ('C28', 118.7)):
    V.append(vod('GND', 'F', WG, [(c, '2'), (x, 143.6)], b))
    V.append(via('GND', (x, 143.6)))
# kristal: XIN direktno, XOUT preko R32 na XO; C26 (XIN) i C27 (XO)
V.append(vod('XIN', 'F', WS, [('U7', '20'), (121.6, 137.6), (122.4, 138.4), (122.4, 139.65), ('Y1', '1')], b))
V.append(vod('XIN', 'F', WS, [('Y1', '1'), ('C26', '1')], b))
V.append(vod('XOUT', 'F', WS, [('U7', '21'), (121.5, 137.2), (122.75, 135.95), ('R32', '1')], b))
V.append(vod('XO', 'F', WS, [('R32', '2'), (125.9, 136.6), ('Y1', '3')], b))
V.append(vod('XO', 'F', WS, [('Y1', '3'), ('C27', '1')], b))
# masa kristala: dijagonala ispod kućišta između GND padova, via ispod; masa C26 i C27
V.append(vod('GND', 'F', WG, [('Y1', '4'), ('Y1', '2')], b))
V.append(vod('GND', 'F', WG, [('Y1', '2'), ('C27', '2')], b))          # masa kristala deli viju C27
V.append(vod('GND', 'F', WG, [('C26', '2'), (123.7, 144.0)], b)); V.append(via('GND', (123.7, 144.0)))
V.append(vod('GND', 'F', WG, [('C27', '2'), (127.8, 140.7)], b)); V.append(via('GND', (127.8, 140.7)))
ok, r = primeni(None, V, 'korak 1d: blokada RP2040 (gore/dole) i kristal povezani')
if ok:
    slika(r, (108, 128, 130, 146))
