"""Korak 1: QSPI RP2040 <-> W25Q16 (ručno). Desni red flash-a direktno na F.Cu, levi red preko B.Cu sa 3 via."""
from rucno_alat import *
import rucni_vodovi

b = ploca()
U8 = lambda n: ('U8', str(n))
U7 = lambda n: ('U7', str(n))
W = 0.2
V = list(rucni_vodovi.RUCNI)
V = [v for v in V if v[0] not in ('QSCLK', 'QSD0', 'QSD1', 'QSD2', 'QSD3', 'QSS')]
# desni red flash-a -> pinovi 51-53 (F.Cu): prava linija + jedan kosi segment 45°
V.append(vod('QSCLK', 'F', W, [U8(6), U7(52)], b))
V.append(vod('QSD3', 'F', W, [U8(7), (110.6, 136.73), (111.47, 137.6), U7(51)], b))
V.append(vod('QSD0', 'F', W, [U8(5), (110.6, 139.27), (111.47, 138.4), U7(53)], b))
# levi red flash-a: via ispod tela -> B.Cu ugneždeni L vodovi -> via ispod pinova 54-56 -> kratko F.Cu
for net, pin, y, (xv, yv), _, cilj in [
        ('QSS', 1, 135.46, (112.6, 140.9), (112.6, 140.2), 56),
        ('QSD1', 2, 136.73, (111.5, 140.3), None, 55),
        ('QSD2', 3, 138.0, (110.6, 139.95), None, 54)]:
    V.append(vod(net, 'F', W, [U8(pin), (103.4, y)], b))
    V.append(via(net, (103.4, y)))
    if net == 'QSS':
        V.append(vod(net, 'B', W, [(103.4, y), (111.8, y), (112.6, 136.26), (112.6, 140.9)], b))
        V.append(vod(net, 'F', W, [(112.6, 140.9), (112.6, 140.2), (113.2, 139.6), U7(56)], b))
    elif net == 'QSD1':
        V.append(vod(net, 'B', W, [(103.4, y), (110.9, y), (111.5, 137.33), (111.5, 140.3)], b))
        V.append(vod(net, 'F', W, [(111.5, 140.3), (112.6, 139.2), U7(55)], b))
    else:
        V.append(vod(net, 'B', W, [(103.4, y), (110.2, y), (110.6, 138.4), (110.6, 139.95)], b))
        V.append(vod(net, 'F', W, [(110.6, 139.95), (111.75, 138.8), U7(54)], b))
    V.append(via(net, (xv, yv)))
ok, r = primeni(None, V, 'korak 1: QSPI RP2040 <-> flash')
if ok:
    slika(r, (100, 130, 124, 146))
