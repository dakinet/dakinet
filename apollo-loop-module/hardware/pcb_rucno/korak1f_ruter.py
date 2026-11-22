"""Korak 1f: USB i DVDD kroz zbijeni levi kanal – geometriju nalazi moj ruter (motor.py) po mojim pravilima,
rezultat se prepisuje u rucni_vodovi.py (zaključano) i prolazi zaštitu (preklapanja + širine + DRC)."""
import os
import sys
from rucno_alat import *
import rucni_vodovi
sys.path.insert(0, os.path.join(OVDE, '../../../../tools/ruter'))
from motor import Ruter  # noqa: E402

ok, b = True, None
if not ok:
    raise SystemExit(1)
MREZE = [
         ('DVDD', [0.2], dict(prioritet=2, cena_B=2.5))]
r = Ruter(os.path.join(OVDE, 'apollo_module.kicad_pcb'), pregled=URL, visoki=list(VISOKI))
neuspele = r.izvrsi(MREZE)
T = pcbnew.ToMM
novi = []
for t in r.b.GetTracks():
    if t.IsLocked() or t.GetNetname() not in {m_[0] for m_ in MREZE}:
        continue
    if t.GetClass() == 'PCB_VIA':
        novi.append((t.GetNetname(), [], [(round(T(t.GetPosition().x), 4), round(T(t.GetPosition().y), 4))]))
    else:
        novi.append((t.GetNetname(), [('F' if t.GetLayer() == pcbnew.F_Cu else 'B', round(T(t.GetStart().x), 4),
                                       round(T(t.GetStart().y), 4), round(T(t.GetEnd().x), 4), round(T(t.GetEnd().y), 4),
                                       round(T(t.GetWidth()), 3))], []))
log('ruter je dao %d elemenata za %s; neuspele: %s' % (len(novi), ', '.join(m_[0] for m_ in MREZE), neuspele or 'nema'))
ok, rez = primeni(None, list(rucni_vodovi.RUCNI) + novi, 'korak 1f: DVDD oko tela čipa (ruter po mojim pravilima)')
if ok:
    slika(rez, (100, 127, 130, 146))
