"""Korak 1e: DVDD (VREG_OUT 45 sa 1 uF C34) ručno, +3V3 pin 44 preko pina 43; C30 dole levo."""
from rucno_alat import *
import rucni_vodovi

postavi({'C34': (111.3, 134.7, 180), 'C30': (112.0, 142.25, 270)})
b = ploca()
V = [v for v in rucni_vodovi.RUCNI if not (v[0] == '+3V3' and v[1] and abs(v[1][0][1] - 111.95) < 0.01)]   # stari kosi vod C32
V.append(vod('+3V3', 'F', 0.25, [('C32', '1'), (111.95, 133.0), (113.2, 133.0)], b))     # C32 se spaja na vod C39
V.append(vod('+3V3', 'F', 0.25, [(113.2, 134.4), (113.2, 134.8), ('U7', '44')], b))      # pin 44 preko pina 43
V.append(vod('DVDD', 'F', 0.25, [('C34', '1'), (111.78, 135.2), ('U7', '45')], b))       # VREG_OUT -> 1 uF tik uz pin
V.append(vod('GND', 'F', 0.3, [('C34', '2'), (110.5, 132.4)], b))                         # masa C34 na viju C25
V.append(vod('+3V3', 'F', 0.25, [('C30', '1'), ('C31', '1')], b))          # C30 na isti čvor kao C31 (pin 1)
V.append(vod('GND', 'F', 0.3, [('C30', '2'), (112.0, 143.6)], b)); V.append(via('GND', (112.0, 143.6)))
ok, r = primeni(None, V, 'korak 1e: VREG_OUT 1 uF (C34) i +3V3 levi ugao')
if ok:
    slika(r, (108, 128, 130, 146))
