"""Povezuje izolovana ostrva GND površine sa glavnom masom preko via (posle finish_pcb.py).

Rasterizuje izlivenu GND masu (F i B), GND vodove, padove i via na mreži 0,1 mm, nalazi povezane celine preko slojeva
(via i THT padovi spajaju slojeve). Za svako ostrvo traži tačku gde je u krugu 0,35 mm i na jednom sloju ostrvo, a na
drugom glavna masa – via tu ne može da dodirne tuđu mrežu (izlivanje već drži razmak). Dodaje via, ponovo izliva, ponavlja.
"""
import os
import sys

import numpy as np
import pcbnew
from matplotlib.path import Path
from scipy import ndimage

OVDE = os.path.dirname(os.path.abspath(__file__))
IME = os.path.join(OVDE, 'apollo_module.kicad_pcb')
G = 0.1
T = pcbnew.ToMM


def rasteri(b):
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0, x1, y1 = T(bb.GetLeft()), T(bb.GetTop()), T(bb.GetRight()), T(bb.GetBottom())
    W, H = int((x1 - x0) / G) + 1, int((y1 - y0) / G) + 1
    xs, ys = np.meshgrid(x0 + np.arange(W) * G, y0 + np.arange(H) * G)
    tacke = np.column_stack([xs.ravel(), ys.ravel()])
    L = np.zeros((2, H, W), bool)
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != 'GND':
            continue
        for li, lay in ((0, pcbnew.F_Cu), (1, pcbnew.B_Cu)):
            if not z.IsOnLayer(lay):
                continue
            ps = z.GetFilledPolysList(lay)
            for oi in range(ps.OutlineCount()):
                o = ps.Outline(oi)
                m = Path([(T(o.CPoint(k).x), T(o.CPoint(k).y)) for k in range(o.PointCount())]).contains_points(tacke)
                for hi in range(ps.HoleCount(oi)):
                    h = ps.Hole(oi, hi)
                    m &= ~Path([(T(h.CPoint(k).x), T(h.CPoint(k).y)) for k in range(h.PointCount())]).contains_points(tacke)
                L[li] |= m.reshape(H, W)
    spoj = np.zeros((H, W), bool)

    def disk(cx, cy, r):
        return (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r
    for t in b.GetTracks():
        if t.GetNetname() != 'GND':
            continue
        if t.GetClass() == 'PCB_VIA':
            d = disk(T(t.GetPosition().x), T(t.GetPosition().y), T(t.GetWidth(pcbnew.F_Cu)) / 2)
            L[0] |= d; L[1] |= d; spoj |= d
        else:
            li = 0 if t.GetLayer() == pcbnew.F_Cu else 1
            a, c = t.GetStart(), t.GetEnd()
            ax, ay, cx, cy = T(a.x), T(a.y), T(c.x), T(c.y)
            dx, dy = cx - ax, cy - ay
            l2 = dx * dx + dy * dy or 1e-9
            tt = np.clip(((xs - ax) * dx + (ys - ay) * dy) / l2, 0, 1)
            L[li] |= (xs - ax - tt * dx) ** 2 + (ys - ay - tt * dy) ** 2 <= (T(t.GetWidth()) / 2) ** 2
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != 'GND':
                continue
            pb = p.GetBoundingBox()
            m = (xs >= T(pb.GetLeft())) & (xs <= T(pb.GetRight())) & (ys >= T(pb.GetTop())) & (ys <= T(pb.GetBottom()))
            if p.IsOnLayer(pcbnew.F_Cu):
                L[0] |= m
            if p.IsOnLayer(pcbnew.B_Cu):
                L[1] |= m
            if p.IsOnLayer(pcbnew.F_Cu) and p.IsOnLayer(pcbnew.B_Cu):
                spoj |= m
    return L, spoj, x0, y0


def celine(L, spoj):
    lab = np.zeros(L.shape, np.int32)
    n = 0
    for li in (0, 1):
        lab[li], k = ndimage.label(L[li], structure=np.ones((3, 3)))
        lab[li][lab[li] > 0] += n
        n += k
    rod = list(range(n + 1))

    def nadji(a):
        while rod[a] != a:
            rod[a] = rod[rod[a]]
            a = rod[a]
        return a
    m = spoj & (lab[0] > 0) & (lab[1] > 0)
    for a, c in set(zip(lab[0][m].tolist(), lab[1][m].tolist())):
        ra, rc = nadji(a), nadji(c)
        if ra != rc:
            rod[ra] = rc
    kor = np.array([nadji(i) for i in range(n + 1)])
    return np.where(lab > 0, kor[lab], 0)


def main():
    b = pcbnew.LoadBoard(IME)
    gnd = b.FindNet('GND')
    dodato = 0
    for krug in range(6):
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        L, spoj, x0, y0 = rasteri(b)
        C = celine(L, spoj)
        ids, broj = np.unique(C[C > 0], return_counts=True)
        if len(ids) <= 1:
            break
        glavna = ids[np.argmax(broj)]
        r = int(np.ceil(0.35 / G))
        st = np.hypot(*np.mgrid[-r:r + 1, -r:r + 1]) * G <= 0.35
        novo = 0
        for k in ids:
            if k == glavna:
                continue
            for li in (0, 1):
                ostrvo = ndimage.binary_erosion(C[li] == k, structure=st)
                glav = ndimage.binary_erosion(C[1 - li] == glavna, structure=st)
                kand = np.argwhere(ostrvo & glav)
                if len(kand):
                    i, j = kand[len(kand) // 2]
                    v = pcbnew.PCB_VIA(b)
                    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(float(x0 + j * G)), pcbnew.FromMM(float(y0 + i * G))))
                    v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6))
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(gnd)
                    b.Add(v)
                    novo += 1
                    break
        print('krug %d: celina %d, dodato via %d' % (krug, len(ids), novo))
        dodato += novo
        if not novo:
            break
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(IME, b)
    print('ukupno via za ostrva:', dodato)


if __name__ == '__main__':
    main()
