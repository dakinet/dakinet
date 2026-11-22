"""Razmiče komponente iz make_pcb.POZ tako da se courtyard-i ne preklapaju i da su unutar ivice ploče.

Pomera samo manje delove, na najbliže slobodno mesto (mreža 0,05 mm); veliki/kritični delovi (FIKSNO) ostaju.
Ispisuje nove POZ redove za delove koji su pomereni.  Pokretanje:  python razmakni.py [--upisi]
(--upisi direktno zamenjuje koordinate u make_pcb.py)
"""
import math
import re
import sys

import make_pcb as m
import pcbnew

FIKSNO = {'U1', 'L1', 'D2', 'C36', 'C3', 'C4', 'C5', 'C2', 'C9', 'C35', 'C8', 'R1', 'R2', 'R3', 'R4', 'C6', 'C7',
          'U2', 'C10', 'C37', 'C11', 'L2', 'C12', 'C13', 'J1', 'F1', 'D1', 'C1', 'Y1', 'C40', 'C26', 'C27', 'D3', 'U7', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C38', 'C39', 'C40', 'C41'}
RAZMAK = 0.0      # minimalni razmak između courtyard-a (mm)
KORAK = 0.05
MAX_R = 12.0


def kutije(b):
    out = {}
    for f in b.GetFootprints():
        x0, y0, x1, y1 = m.kutija(f)
        p = f.GetPosition()
        px, py = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        out[f.GetReference()] = (x0 - px, y0 - py, x1 - px, y1 - py)
    return out


def main():
    b, _ = m.napravi()
    rel = kutije(b)
    poz = {r: list(v) for r, v in m.POZ.items()}

    def box(r, x=None, y=None):
        x = poz[r][0] if x is None else x
        y = poz[r][1] if y is None else y
        a = rel[r]
        return x + a[0], y + a[1], x + a[2], y + a[3]

    def unutra(bx):
        return bx[0] >= m.X0 and bx[1] >= m.Y0 and bx[2] <= m.X1 and bx[3] <= m.Y1

    def sudar(b1, b2):
        return b1[0] < b2[2] + RAZMAK and b2[0] < b1[2] + RAZMAK and b1[1] < b2[3] + RAZMAK and b2[1] < b1[3] + RAZMAK

    def slobodno(r, x, y):
        bx = box(r, x, y)
        if not unutra(bx):
            return False
        return not any(sudar(bx, box(o)) for o in poz if o != r)

    # fiksni delovi koji vire preko ivice: uvuci ih minimalno
    for r in sorted(FIKSNO):
        x0, y0, x1, y1 = box(r)
        dx = max(0, m.X0 - x0) - max(0, x1 - m.X1)
        dy = max(0, m.Y0 - y0) - max(0, y1 - m.Y1)
        if dx or dy:
            poz[r][0] = round(poz[r][0] + dx + math.copysign(0.01, dx) * (dx != 0), 2)
            poz[r][1] = round(poz[r][1] + dy + math.copysign(0.01, dy) * (dy != 0), 2)

    def povrsina(r):
        a = rel[r]
        return (a[2] - a[0]) * (a[3] - a[1])

    pomereno = {}
    for _ in range(500):
        konflikti = [r for r in poz if r not in FIKSNO and not slobodno(r, *poz[r][:2])]
        if not konflikti:
            break
        konflikti.sort(key=povrsina)
        r = konflikti[0]
        x0, y0 = poz[r][:2]
        nadjeno = None
        n = int(MAX_R / KORAK)
        kandidati = sorted(((i * KORAK) ** 2 + (j * KORAK) ** 2, i, j) for i in range(-n, n + 1) for j in range(-n, n + 1)
                           if (i * KORAK) ** 2 + (j * KORAK) ** 2 <= MAX_R ** 2)
        for _, i, j in kandidati:
            x, y = round(x0 + i * KORAK, 2), round(y0 + j * KORAK, 2)
            if slobodno(r, x, y):
                nadjeno = (x, y)
                break
        if not nadjeno:
            print('NEMA MESTA za', r)
            FIKSNO.add(r)
            continue
        poz[r][0], poz[r][1] = nadjeno
        pomereno[r] = (x0, y0, *nadjeno)

    for r in sorted(poz):
        if tuple(poz[r]) != tuple(m.POZ[r]):
            print('%-4s %7.2f %7.2f -> %7.2f %7.2f' % (r, m.POZ[r][0], m.POZ[r][1], poz[r][0], poz[r][1]))
    ostalo = [r for r in poz if not slobodno(r, *poz[r][:2])]
    print('ostalo u konfliktu:', ostalo)

    if '--upisi' in sys.argv:
        s = open('make_pcb.py', encoding='utf-8').read()
        for r in poz:
            if tuple(poz[r]) != tuple(m.POZ[r]):
                s, k = re.subn(r"('%s': \()[-\d.]+, [-\d.]+(, -?\d+\))" % r,
                               lambda mo: '%s%g, %g%s' % (mo.group(1), poz[r][0], poz[r][1], mo.group(2)), s)
                assert k == 1, r
        open('make_pcb.py', 'w', encoding='utf-8', newline='\n').write(s)
        print('upisano u make_pcb.py')


if __name__ == '__main__':
    main()
