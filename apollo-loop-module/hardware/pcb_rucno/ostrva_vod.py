"""Ostrva GND površine koja vija ne može da spoji: GND vod od ostrva do glavne mase (moj ruter, mapa sa izlivenom masom).
Novi vodovi se dopisuju u rucni_vodovi.py (zaključani), da ceo tok ostane ponovljiv."""
import os
import sys

import numpy as np
import pcbnew

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDE)
sys.path.insert(0, os.path.join(OVDE, '../../../../tools/ruter'))
import ostrva  # noqa: E402
from motor import Ruter, _np  # noqa: E402
import rucno_alat  # noqa: E402

b = pcbnew.LoadBoard(ostrva.IME)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
L, spoj, x0, y0 = ostrva.rasteri(b)
C = ostrva.celine(L, spoj)
ids, broj = np.unique(C[C > 0], return_counts=True)
glavna = ids[np.argmax(broj)]
r = Ruter(ostrva.IME, pregled=rucno_alat.URL, visoki=list(rucno_alat.VISOKI))
kod = r.kod['GND']
# izlivenu masu (0,1 mm mreža) prenesi u mapu rutera (0,05 mm): GND bakar
fak = int(round(ostrva.G / r.G))
Cv = np.kron(C, np.ones((1, fak, fak), np.int32))[:, :r.H, :r.W]
pad_h, pad_w = r.H - Cv.shape[1], r.W - Cv.shape[2]
Cv = np.pad(Cv, ((0, 0), (0, max(0, pad_h)), (0, max(0, pad_w))))
r.cu[(Cv > 0) & (r.cu == 0)] = kod
novi = []
for k in ids:
    if k == glavna:
        continue
    for w in (0.3, 0.25, 0.2):
        ok, via_ok, cena = r._dozvole(kod, w, 0.15, 1.5, False)
        okh = _np(ok)
        izv = (Cv == k) & okh
        cilj = (Cv == glavna) & okh
        if not izv.any() or not cilj.any():
            continue
        put = r._trazi(izv, cilj, cena, via_ok, 1.0)
        if put is None:
            continue
        pre = {t.m_Uuid.AsString() for t in r.b.GetTracks()}
        r._crtaj('GND', kod, w, put)
        for t in r.b.GetTracks():
            if t.m_Uuid.AsString() in pre:
                continue
            T = pcbnew.ToMM
            if t.GetClass() == 'PCB_VIA':
                novi.append(('GND', [], [(round(T(t.GetPosition().x), 4), round(T(t.GetPosition().y), 4))]))
            else:
                novi.append(('GND', [('F' if t.GetLayer() == pcbnew.F_Cu else 'B', round(T(t.GetStart().x), 4), round(T(t.GetStart().y), 4),
                                      round(T(t.GetEnd().x), 4), round(T(t.GetEnd().y), 4), w)], []))
        print('ostrvo %d povezano (%.2f mm, %d elemenata)' % (k, w, len(put)))
        break
    else:
        print('ostrvo %d: nema puta' % k)
import rucni_vodovi  # noqa: E402
rucno_alat.sacuvaj_vodove(list(rucni_vodovi.RUCNI) + novi)
print('dodato u rucni_vodovi.py:', len(novi))
