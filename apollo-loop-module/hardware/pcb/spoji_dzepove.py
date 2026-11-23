"""Spaja izolovane džepove mase (GND padovi zatvoreni vodovima) sa glavnom masom kratkim GND vodom.

Izvor: ispuna džepa oko izolovanog pada (+ džepovi na drugom sloju povezani njegovim via).
Cilj:  ispuna mase koja pripada glavnoj grupi povezanosti.  Put traži motor rutera (razmaci i via po pravilima).
Pokretanje posle finish_pcb.py:  RUTER_CPU=1 python spoji_dzepove.py   (pa ponovo DRC)
"""
import os
import sys

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(OVDE, '../../../../tools/ruter'))
import numpy as np  # noqa: E402
import pcbnew  # noqa: E402
from motor import Ruter, _np  # noqa: E402

IME = os.path.join(OVDE, 'apollo_module.kicad_pcb')
VISOKI = ['+34V', 'SW', 'NE', 'NB', 'U3OUT', 'LOOP_DRV', 'LOOP_OUT', 'LOOP_IN', 'PE']
T = pcbnew.ToMM


def grupe_gnd(b):
    b.BuildConnectivity()
    c = b.GetConnectivity()
    pads = [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == 'GND']
    uid = {p.m_Uuid.AsString(): i for i, p in enumerate(pads)}
    ostalo, gr = set(range(len(pads))), []
    for i, p in enumerate(pads):
        if i in ostalo:
            povez = c.GetConnectedItems(p)
            g = {i} | {uid[x.m_Uuid.AsString()] for x in povez if x.m_Uuid.AsString() in uid}
            ostalo -= g
            gr.append((g, povez))
    gr.sort(key=lambda t: len(t[0]), reverse=True)
    return pads, gr


def poligoni_sa(b, tacke):
    """(sloj, SHAPE_POLY_SET) GND ispuna koje sadrže bar jednu od tačaka (x, y, sloj ili None)."""
    out = []
    for z in b.Zones():
        if z.GetNetname() != 'GND':
            continue
        for L in (pcbnew.F_Cu, pcbnew.B_Cu):
            if not z.IsOnLayer(L):
                continue
            fp = z.GetFilledPolysList(L)
            for i in range(fp.OutlineCount()):
                o = fp.Outline(i)
                if any((sl is None or sl == L) and o.PointInside(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
                       for x, y, sl in tacke):
                    out.append((L, pcbnew.SHAPE_POLY_SET(o)))
    return out


def maska(r, polys, okvir=None):
    """Ćelije unutar poligona; okvir=(x0, y0, x1, y1) ograničava pretragu (brzina)."""
    m = np.zeros((2, r.H, r.W), bool)
    for L, ps in polys:
        l = 0 if L == pcbnew.F_Cu else 1
        bb = ps.BBox()
        x0, y0, x1, y1 = T(bb.GetLeft()), T(bb.GetTop()), T(bb.GetRight()), T(bb.GetBottom())
        if okvir:
            x0, y0, x1, y1 = max(x0, okvir[0]), max(y0, okvir[1]), min(x1, okvir[2]), min(y1, okvir[3])
            if x0 >= x1 or y0 >= y1:
                continue
        (si, sj), xs, ys = r._prozor(x0, y0, x1, y1)
        for ii, i in enumerate(range(si.start, si.stop)):
            for jj, j in enumerate(range(sj.start, sj.stop)):
                if ps.Contains(pcbnew.VECTOR2I(pcbnew.FromMM(float(xs[0, jj])), pcbnew.FromMM(float(ys[ii, 0])))):
                    m[l, i, j] = True
    return m


def main():
    b = pcbnew.LoadBoard(IME)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pads, gr = grupe_gnd(b)
    if len(gr) == 1:
        print('masa je jedna celina')
        return
    glavni = gr[0][1]
    tacke_gl = [(T(x.GetPosition().x), T(x.GetPosition().y), None) for x in glavni if x.Type() == pcbnew.PCB_VIA_T]
    tacke_gl += [(T(pads[j].GetPosition().x), T(pads[j].GetPosition().y), pcbnew.F_Cu) for j in gr[0][0]
                 if pads[j].IsOnLayer(pcbnew.F_Cu)]
    cilj_polys = poligoni_sa(b, tacke_gl)
    izol = [pads[j] for g, _ in gr[1:] for j in g]
    xs_ = [T(q.GetPosition().x) for q in izol]
    ys_ = [T(q.GetPosition().y) for q in izol]
    okvir = (min(xs_) - 6, min(ys_) - 6, max(xs_) + 6, max(ys_) + 6)
    r = Ruter(IME, visoki=VISOKI)
    r.b = b
    r._rasterizuj()
    kod = b.FindNet('GND').GetNetCode()
    cilj_m = maska(r, cilj_polys, okvir)
    w = float(os.environ.get('SIRINA', 0.25))
    RAZMAK = float(os.environ.get('RAZMAK', 0.2))
    ok, via_ok, cena = r._dozvole(kod, w, RAZMAK, 1.5, True)
    okh = _np(ok)
    uspeh = 0
    for g, povez in gr[1:]:
        p = pads[next(iter(g))]
        ime = '%s.%s' % (p.GetParentFootprint().GetReference(), p.GetNumber())
        izv_t = [(T(pads[j].GetPosition().x), T(pads[j].GetPosition().y), pcbnew.F_Cu) for j in g]
        izv_t += [(T(x.GetPosition().x), T(x.GetPosition().y), None) for x in povez if x.Type() == pcbnew.PCB_VIA_T]
        izv_m = maska(r, poligoni_sa(b, izv_t), okvir)
        for j in g:                                   # i sam pad
            q = pads[j]
            bb = q.GetBoundingBox()
            r.boji_pravougaonik(0, T(bb.GetLeft()), T(bb.GetTop()), T(bb.GetRight()), T(bb.GetBottom()), 1, izv_m.view(np.int8))
        izv = izv_m & okh & ~cilj_m
        cilj = cilj_m & okh
        if not izv.any() or not cilj.any():
            print('  %s: nema dozvoljenih ćelija (izvor %d, cilj %d)' % (ime, izv.sum(), cilj.sum()))
            continue
        put = r._trazi(izv, cilj, cena, via_ok, 1.5)
        if put is None:
            print('  %s: nema puta do glavne mase' % ime)
            continue
        r._crtaj('GND', kod, w, put)
        uspeh += 1
        print('  %s: spojen (%d ćelija puta)' % (ime, len(put)))
        r._rasterizuj()
        ok, via_ok, cena = r._dozvole(kod, w, RAZMAK, 1.5, True)
        okh = _np(ok)
    for t in b.GetTracks():                      # GND vodovi su fiksni: ruter (dopuna) ne sme da ih ukloni
        if t.GetNetname() == 'GND':
            t.SetLocked(True)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(IME, b)
    _, gr2 = grupe_gnd(b)
    print('spojeno džepova: %d, grupa mase sada: %d' % (uspeh, len(gr2)))


if __name__ == '__main__':
    main()
