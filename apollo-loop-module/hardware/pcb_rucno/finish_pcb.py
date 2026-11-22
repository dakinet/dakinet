"""Uvozi Freerouting rezultat (.ses), dodaje GND površine na oba sloja i šivene via, snima ploču.
SES parser je isti kao u apollo-loop-driver/hardware/pcb/finish_pcb.py."""
import os
import sys
sys.path.append('/usr/lib/python3/dist-packages')
OVDE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(OVDE, '../../../apollo-loop-driver/hardware/pcb')   # NE ide u sys.path (i on ima make_pcb.py)
sys.path.insert(0, OVDE)
import pcbnew
MM = pcbnew.FromMM
IME = 'apollo_module'
from make_pcb import X0, Y0, X1, Y1, POZ  # dimenzije ploče (60 x 45 mm) iz izvora istine (modulov make_pcb)

# uvezi_ses iz mastera (modul na uvozu odmah ucitava apollo plocu, pa se funkcija cita iz izvornog teksta)
_src = open(os.path.join(MASTER, 'finish_pcb.py'), encoding='utf-8').read()
_ns = {'pcbnew': pcbnew, 'MM': MM}
exec(_src[_src.index('def ses_tokens'):_src.index("uvezi_ses(b, 'apollo")], _ns)
uvezi_ses = _ns['uvezi_ses']

b = pcbnew.LoadBoard(IME + '.kicad_pcb')
if os.path.exists(IME + '.ses'):                 # Freerouting tok; ručni ruter (rutiraj.py) upisuje vodove direktno
    uvezi_ses(b, IME + '.ses')
gnd = b.FindNet('GND')
# Freerouting ne poštuje razmak do ivice ploče: GND vodove bliže od 0,35 mm ivici brišemo (masu povezuju površine)
uk = 0
for t in [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'GND']:
    pts = [t.GetStart(), t.GetEnd()]
    w2 = pcbnew.ToMM(t.GetWidth()) / 2
    if any(min(pcbnew.ToMM(q.x) - X0, X1 - pcbnew.ToMM(q.x), pcbnew.ToMM(q.y) - Y0, Y1 - pcbnew.ToMM(q.y)) - w2 < 0.35 for q in pts):
        b.Remove(t); uk += 1
print('GND vodova uz ivicu uklonjeno:', uk)
OKVIR = [(X0 + 0.25, Y0 + 0.25), (X1 - 0.25, Y0 + 0.25), (X1 - 0.25, Y1 - 0.25), (X0 + 0.25, Y1 - 0.25)]


def zona(net, tacke, layer, prioritet=0):
    z = pcbnew.ZONE(b)
    z.SetAssignedPriority(prioritet) if hasattr(z, 'SetAssignedPriority') else z.SetPriority(prioritet)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetLocalClearance(MM(0.25))
    z.SetMinThickness(MM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)   # mala ploča, montaža reflow: puna veza, bez „starved thermal“
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetThermalReliefGap(MM(0.25))
    z.SetThermalReliefSpokeWidth(MM(0.3))
    o = z.Outline()
    o.NewOutline()
    for x, y in tacke:
        o.Append(MM(x), MM(y))
    b.Add(z)


for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    zona(gnd, OKVIR, layer)

# Q1 (MJD122) hlađenje: +34V bakar ispod taba (kolektor) na oba sloja + termalne via kroz tab.
# Disipacija (34 - 24,2) V x 150 mA ~ 1,5 W kontinualno -> treba površina na F i B sloju.
qx, qy = POZ['Q1'][:2]
tx, ty = qx + 1.26, qy            # centar taba (pad 2) u TO-252-2 footprintu
HLAD = [(tx - 3.7, Y0 + 0.4), (min(tx + 4.3, X1 - 0.4), Y0 + 0.4), (min(tx + 4.3, X1 - 0.4), qy + 4.3), (tx - 3.7, qy + 4.3)]
v34 = b.FindNet('+34V')
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    zona(v34, HLAD, layer, prioritet=1)
for i in (-2, -1, 0, 1, 2):
    for j in (-1.6, 0, 1.6):
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(MM(tx + 0.4 + i * 1.2), MM(ty + j)))
        v.SetDrill(MM(0.3)); v.SetWidth(MM(0.6))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(v34)
        b.Add(v)


ZABRANE_VIA = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]


def slobodno(x, y, r):
    p = pcbnew.VECTOR2I(MM(x), MM(y))
    if min(x - X0, X1 - x, y - Y0, Y1 - y) < 1.0:          # ne uz samu ivicu (traka 0,35 + razmak 0,3)
        return False
    for z in ZABRANE_VIA:                                     # nikad u zoni bez via
        if z.Outline().Contains(p) or z.Outline().Collide(p, MM(r)):
            return False
    box = pcbnew.BOX2I(pcbnew.VECTOR2I(MM(x - r), MM(y - r)), pcbnew.VECTOR2I(MM(2 * r), MM(2 * r)))
    for fp in b.GetFootprints():
        c = fp.GetCourtyard(pcbnew.F_CrtYd)
        bb = c.BBox() if not c.IsEmpty() else fp.GetBoundingBox(False, False)
        if bb.Intersects(box):
            return False
    for t in b.GetTracks():
        if t.HitTest(p, MM(r)):
            return False
    return True


n = 0
for i in range(0, int((X1 - X0) / 2.0)):          # šivenje na mreži 2 mm (dovoljno za 2 sloja, bez šume via)
    for j in range(0, int((Y1 - Y0) / 2.0)):
        x, y = X0 + 1.5 + i * 2.0, Y0 + 1.3 + j * 2.0
        if slobodno(x, y, 0.55):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            v.SetDrill(MM(0.3)); v.SetWidth(MM(0.6))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(gnd)
            b.Add(v); n += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
zf = [z for z in b.Zones() if z.GetLayer() == pcbnew.F_Cu]
zb = [z for z in b.Zones() if z.GetLayer() == pcbnew.B_Cu]
ukl = 0
for v in [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetname() == 'GND']:
    p = v.GetPosition()
    naF = any(z.HitTestFilledArea(pcbnew.F_Cu, p) for z in zf)
    naB = any(z.HitTestFilledArea(pcbnew.B_Cu, p) for z in zb)
    imaVod = any(t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'GND' and (t.GetStart() == p or t.GetEnd() == p) for t in b.GetTracks())
    naPadu = any(pd.GetNetname() == 'GND' and pd.HitTest(p) for fp in b.GetFootprints() for pd in fp.Pads())
    if not (naF and naB) and not imaVod and not naPadu:
        b.Remove(v); ukl += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
# ostrva: svaki deo GND površine bez via dobija via (ako ima slobodno mesto), pa ponovo izlivanje
ostrva = 0
gnd_via = [t.GetPosition() for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetname() == 'GND']
for z in [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']:
    lay = z.GetLayer()
    poly = z.GetFilledPolysList(lay)
    for oi in range(poly.OutlineCount()):
        jedan = pcbnew.SHAPE_POLY_SET()
        jedan.AddOutline(poly.Outline(oi))
        if any(jedan.Contains(v) for v in gnd_via):
            continue
        bb = poly.Outline(oi).BBox()
        nadjeno = False
        xx = pcbnew.ToMM(bb.GetLeft())
        while xx < pcbnew.ToMM(bb.GetRight()) and not nadjeno:
            yy = pcbnew.ToMM(bb.GetTop())
            while yy < pcbnew.ToMM(bb.GetBottom()) and not nadjeno:
                pt = pcbnew.VECTOR2I(MM(xx), MM(yy))
                if jedan.Contains(pt) and slobodno(xx, yy, 0.55):
                    v = pcbnew.PCB_VIA(b)
                    v.SetPosition(pt); v.SetDrill(MM(0.3)); v.SetWidth(MM(0.6))
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(gnd)
                    b.Add(v); gnd_via.append(pt); ostrva += 1; nadjeno = True
                yy += 0.25
            xx += 0.25
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print('GND via za šivenje:', n, 'uklonjeno nepovezanih:', ukl, 'via za ostrva:', ostrva)
print('vodova:', len([t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']),
      'via:', len([t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']))
# U1 TPS55340PWP (TI PWP0014K, crtež 4229706/B): izloženi pad kućišta najviše 2,6 x 2,59 mm; TI land pattern:
# bakar 3,4 x 5, otvor maske 2,6 x 2,59 (definisan maskom), pasta do 2,6 x 2,59. Footprint iz biblioteke ima masku
# 3,155 x 3,255 i pastu 2,9 x 2,89 (veće od pada) – svodi se na TI vrednosti (lokalne koordinate footprint-a).
u1 = b.FindFootprintByReference('U1')
for p in u1.Pads():
    if p.GetNumber() != '':
        continue
    lay = p.GetLayerSet()
    if lay.Contains(pcbnew.F_Mask):
        p.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(pcbnew.FromMM(2.6), pcbnew.FromMM(2.59)))
    elif lay.Contains(pcbnew.F_Paste):
        lp = p.GetFPRelativePosition()
        sx, sy = (1 if lp.x > 0 else -1), (1 if lp.y > 0 else -1)
        p.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.195)))
        p.SetFPRelativePosition(pcbnew.VECTOR2I(pcbnew.FromMM(0.7 * sx), pcbnew.FromMM(0.6975 * sy)))
print('U1 EP: maska 2,6 x 2,59, pasta 4 x 1,2 x 1,195 (TI PWP0014K)')
pcbnew.SaveBoard(IME + '.kicad_pcb', b)
