"""Uvozi Freerouting rezultat (.ses), dodaje GND površine i snima gotovu ploču."""
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew
MM = pcbnew.FromMM

b = pcbnew.LoadBoard('apollo_loop_driver.kicad_pcb')


def ses_tokens(text):
    import re
    return re.findall(r'\(|\)|"[^"]*"|[^\s()]+', text)


def ses_tree(tokens):
    stack, cur = [], []
    for t in tokens:
        if t == '(':
            stack.append(cur); cur = []
        elif t == ')':
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t.strip('"'))
    return cur[0]


def find(node, name):
    for c in node:
        if isinstance(c, list) and c and c[0] == name:
            yield c


def uvezi_ses(b, path):
    root = ses_tree(ses_tokens(open(path).read()))
    res = 10000.0  # 'resolution um 10' -> 0.1 um po jedinici
    routes = next(find(root, 'routes'))
    net_out = next(find(routes, 'network_out'))
    layers = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}
    pt = lambda x, y: pcbnew.VECTOR2I(MM(float(x) / res), MM(-float(y) / res))
    nt = nv = 0
    for n in find(net_out, 'net'):
        net = b.FindNet(n[1])
        for w in find(n, 'wire'):
            for p in find(w, 'path'):
                layer, width, xy = p[1], float(p[2]) / res, p[3:]
                pts = [pt(xy[i], xy[i + 1]) for i in range(0, len(xy) - 1, 2)]
                for a, c in zip(pts, pts[1:]):
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(a); t.SetEnd(c); t.SetWidth(MM(width))
                    t.SetLayer(layers[layer]); t.SetNet(net)
                    b.Add(t); nt += 1
        for v in find(n, 'via'):
            via = pcbnew.PCB_VIA(b)
            via.SetPosition(pt(v[2], v[3]))
            via.SetDrill(MM(0.3)); via.SetWidth(MM(0.6))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(net)
            b.Add(via); nv += 1
    print('uvezeno vodova:', nt, 'via:', nv)


uvezi_ses(b, 'apollo_loop_driver.ses')

gnd = b.FindNet('GND')
gnd_usb = b.FindNet('GND_USB')
GLAVNA = [(130, 100.5), (229.5, 100.5), (229.5, 194.5), (100.5, 194.5), (100.5, 129.5), (130, 129.5)]
USB = [(100.5, 100.5), (127.5, 100.5), (127.5, 127), (100.5, 127)]


def zona(net, tacke, layer):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetLocalClearance(MM(0.3))
    z.SetMinThickness(MM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetThermalReliefGap(MM(0.3))
    z.SetThermalReliefSpokeWidth(MM(0.4))
    o = z.Outline()
    o.NewOutline()
    for x, y in tacke:
        o.Append(MM(x), MM(y))
    b.Add(z)


for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    zona(gnd, GLAVNA, layer)
    zona(gnd_usb, USB, layer)


def slobodno(b, x, y, r):
    p = pcbnew.VECTOR2I(MM(x), MM(y))
    box = pcbnew.BOX2I(pcbnew.VECTOR2I(MM(x - r), MM(y - r)), pcbnew.VECTOR2I(MM(2 * r), MM(2 * r)))
    for fp in b.GetFootprints():
        if fp.GetCourtyard(pcbnew.F_CrtYd).BBox().Intersects(box) if not fp.GetCourtyard(pcbnew.F_CrtYd).IsEmpty() else fp.GetBoundingBox(False, False).Intersects(box):
            return False
    for t in b.GetTracks():
        if t.HitTest(p, MM(r)):
            return False
    return True


# GND "šivenje" gornje i donje površine
n = 0
for x in range(104, 229, 5):
    for y in range(103, 194, 5):
        if x < 132 and y < 131:
            continue          # USB/izolovana zona i razmak
        if slobodno(b, x, y, 1.2):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            v.SetDrill(MM(0.4)); v.SetWidth(MM(0.8))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetNet(gnd)
            b.Add(v); n += 1
print('GND via za šivenje:', n)

# termalne via: tab LM2587 (U1) i centralni pad RP2040 (U9)
fpd = {fp.GetReference(): fp for fp in b.GetFootprints()}
tv = 0
for ref, korak, nx, ny in [('U1', 2.2, 4, 4), ('U9', 1.0, 3, 3)]:
    fp = fpd[ref]
    ep = max((p for p in fp.Pads() if p.GetNetname() == 'GND'), key=lambda p: p.GetSize().x * p.GetSize().y)
    cx, cy = pcbnew.ToMM(ep.GetPosition().x), pcbnew.ToMM(ep.GetPosition().y)
    for i in range(nx):
        for j in range(ny):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(MM(cx + (i - (nx - 1) / 2) * korak), MM(cy + (j - (ny - 1) / 2) * korak)))
            v.SetDrill(MM(0.3)); v.SetWidth(MM(0.6))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetNet(gnd)
            b.Add(v); tv += 1
print('termalnih via:', tv)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())

# ukloni GND via koje posle izlivanja nisu povezane na oba sloja, pa izlij ponovo
zf = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.GetLayer() == pcbnew.F_Cu]
zb = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.GetLayer() == pcbnew.B_Cu]
ukl = 0
for v in [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetname() == 'GND']:
    p = v.GetPosition()
    naF = any(z.HitTestFilledArea(pcbnew.F_Cu, p) for z in zf)
    naB = any(z.HitTestFilledArea(pcbnew.B_Cu, p) for z in zb)
    imaVod = any(t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'GND' and (t.GetStart() == p or t.GetEnd() == p) for t in b.GetTracks())
    naPadu = any(pd.GetNetname() == 'GND' and pd.HitTest(p) for fp in b.GetFootprints() for pd in fp.Pads())
    if not (naF and naB) and not imaVod and not naPadu:
        b.Remove(v); ukl += 1
print('uklonjeno nepovezanih via:', ukl)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
trk = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
print('vodova:', len(trk), 'via:', len(vias))
pcbnew.SaveBoard('apollo_loop_driver.kicad_pcb', b)
