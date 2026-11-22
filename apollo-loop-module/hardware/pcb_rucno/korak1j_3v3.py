"""+3V3 pinovi 48/49 (levo) i 22 (desno); desna strana: DVDD via gore, XOUT duže desno, +3V3 via između."""
from rucno_alat import *
import rucni_vodovi
b = ploca()
def u(v, x0, y0, x1, y1):
    pts = [(s[1], s[2]) for s in v[1]] + list(v[2])
    return pts and all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in pts)
V = []
for v in rucni_vodovi.RUCNI:
    if v[0] == 'DVDD' and u(v, 120.4, 134.5, 123.0, 142.0):          # stari DVDD desno (via, stub, B, veze ka C41/C33)
        continue
    if v[0] == 'DVDD' and v[1] and v[1][0][0] == 'B' and any(abs(s[3] - 121.5) < 0.01 and abs(s[4] - 136.4) < 0.01 for s in v[1]):
        continue                                                      # stara B magistrala koja silazi na (121.5,136.4)
    if v[0] == 'XOUT':
        continue
    V.append(v)
print('uklonjeno:', len(rucni_vodovi.RUCNI) - len(V))
# DVDD: magistrala sa vrha -> via (121.6,135.7) -> pin 23; dalje B po x=122.3 do via (122.3,140.8) -> C41, C33
V.append(vod('DVDD', 'B', 0.25, [(111.8, 133.7), (120.6, 133.7), (121.6, 134.7), (121.6, 135.7)], b)); V.append(via('DVDD', (121.6, 135.7)))
V.append(vod('DVDD', 'F', 0.2, [('U7', '23'), (120.95, 136.4), (121.6, 135.75)], b))
V.append(vod('DVDD', 'B', 0.25, [(121.6, 135.7), (122.3, 136.4), (122.3, 140.8)], b)); V.append(via('DVDD', (122.3, 140.8)))
V.append(vod('DVDD', 'F', 0.25, [(122.3, 140.8), ('C41', '1')], b))
V.append(vod('DVDD', 'F', 0.25, [(122.3, 140.8), ('C33', '1')], b))
# XOUT: duže desno pa gore do R32
V.append(vod('XOUT', 'F', 0.2, [('U7', '21'), (122.0, 137.2), (122.75, 136.45), (122.75, 135.95), ('R32', '1')], b))
# +3V3 pin 22: via između DVDD i XOUT, B ispod čipa do C28 (pin 10)
V.append(vod('+3V3', 'F', 0.2, [('U7', '22'), (121.55, 136.8), (121.55, 136.62)], b)); V.append(via('+3V3', (121.55, 136.62)))
V.append(vod('+3V3', 'B', 0.25, [(121.55, 136.62), (121.55, 140.3), (120.4, 141.45), (119.6, 141.45)], b)); V.append(via('+3V3', (119.6, 141.45)))
V.append(vod('+3V3', 'F', 0.25, [(119.6, 141.45), ('C28', '1')], b))
# +3V3 pinovi 48/49: via na spojnom vodu, B ispod leve strane čipa do čvora C31 (pin 1)
V.append(via('+3V3', (112.62, 136.6)))
V.append(vod('+3V3', 'B', 0.25, [(112.62, 136.6), (112.62, 140.3), (113.4, 141.0)], b)); V.append(via('+3V3', (113.4, 141.0)))
V.append(vod('+3V3', 'F', 0.25, [(113.4, 141.0), ('C31', '1')], b))
ok, r = primeni(None, V, '+3V3 pinovi 48/49 i 22 povezani (via + kratko donjim slojem ispod čipa)')
if ok:
    slika(r, (104, 130, 128, 146))
