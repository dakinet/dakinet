"""Korak 1b: flash – QSS pull-up (R29) i BOOT (R30), blokada C25 tik uz VCC, GND via uz pin 4 i C25."""
from rucno_alat import *
import rucni_vodovi

b = ploca()
V = [v for v in rucni_vodovi.RUCNI if not (v[0] in ('QSS', 'GND', '+3V3') and v[1] and v[1][0][0] == 'F' and
                                          any(abs(s[1] - 102.0) < 0.3 and s[2] < 135 for s in v[1]))]
# QSS: pin 1 flash-a -> R29 (pull-up na 3V3) i sa via (103.4, 135.46) -> R30 (BOOT)
V.append(vod('QSS', 'F', 0.2, [('U8', '1'), (102.0, 134.2), ('R29', '1')], b))
V.append(vod('QSS', 'F', 0.2, [(103.4, 135.46), (105.4, 133.46), ('R30', '1')], b))
# VCC flash-a -> C25 (100 nF) tik iznad; masa C25 i pin 4 flash-a kroz via na donju GND površinu
V.append(vod('+3V3', 'F', 0.25, [(108.9, 135.46), (108.9, 133.4)], b))
V.append(vod('GND', 'F', 0.3, [('C25', '2'), (110.5, 132.4)], b))
V.append(via('GND', (110.5, 132.4)))
V.append(vod('GND', 'F', 0.3, [('U8', '4'), (103.4, 139.27)], b))
V.append(via('GND', (103.4, 139.27)))
ok, r = primeni(None, V, 'korak 1b: flash pull-up, BOOT, blokada i masa')
if ok:
    slika(r, (100, 130, 124, 146))
