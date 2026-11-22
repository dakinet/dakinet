"""Desna strana RP2040: DVDD (23) i +3V3 (22) kroz tented via ispod tela čipa; spolja ostaju SWD/RUN/XOUT."""
from rucno_alat import *
import rucni_vodovi
b = ploca()
V = [v for v in rucni_vodovi.RUCNI if v[0] not in ('DP_H', 'DM_H') and not (v[0] in ('DVDD', '+3V3') and v[1] and any(
     s[0] == 'B' and (118.9 <= s[1] <= 123.2 or 118.9 <= s[3] <= 123.2) and (133.0 <= s[2] <= 141.6) for s in v[1])
     and not any(abs(s[1] - 111.8) < 0.01 for s in v[1]))]
# DVDD: pin 23 -> via (119.2,136.25) ispod tela; B: od magistrale (120.6,133.7) i dalje do C41/C33
V.append(vod('DVDD', 'F', 0.2, [('U7', '23'), (119.75, 136.4), (119.2, 136.25)], b)); V.append(via('DVDD', (119.2, 136.25)))
V.append(vod('DVDD', 'B', 0.25, [(111.8, 133.7), (120.6, 133.7), (119.2, 135.1), (119.2, 136.25)], b))
V.append(vod('DVDD', 'B', 0.25, [(119.2, 136.25), (120.4, 136.25), (121.0, 136.85), (121.0, 140.3), (121.5, 140.8), (122.3, 140.8)], b))
V.append(via('DVDD', (122.3, 140.8)))
V.append(vod('DVDD', 'F', 0.25, [(122.3, 140.8), ('C41', '1')], b))
V.append(vod('DVDD', 'F', 0.25, [(122.3, 140.8), ('C33', '1')], b))
# +3V3 pin 22 -> via (119.3,137.25) ispod tela -> B do via kod C28 (119.6,141.45)
V.append(vod('+3V3', 'F', 0.2, [('U7', '22'), (119.75, 136.8), (119.3, 137.25)], b)); V.append(via('+3V3', (119.3, 137.25)))
V.append(vod('+3V3', 'B', 0.25, [(119.3, 137.25), (119.3, 141.15), (119.6, 141.45)], b))
ok, r = primeni(None, V, 'DVDD i +3V3 desno kroz tented via ispod tela RP2040')
if ok:
    slika(r, (110, 130, 130, 146))
