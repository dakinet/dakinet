"""Alat za ručni raspored i ručno crtanje vodova (pcb_rucno).

  postavi({'U7': (117, 137, 90), ...})      – upisuje POZ u make_pcb.py
  ploca()                                   – gradi ploču iz make_pcb.py (sa dosadašnjim ručnim vodovima)
  pad(b, 'U7', '52')                        – centar pada (x, y)
  vod('QSCLK', 'F', 0.2, [('U8','6'), (111.0, 137.4), ('U7','52')])   – polilinija od tačaka koje biram ja
  via('QSS', (111.2, 139.1))
  sacuvaj_vodove(lista)                     – upisuje rucni_vodovi.py
  drc(b)                                    – snima ploču, kicad-cli DRC, vraća sažetak (bez nepovezanih)
  prikazi(b)                                – šalje ploču u pregled http://127.0.0.1:8766
"""
import importlib
import json
import os
import re
import subprocess
import sys
import urllib.request

import numpy as np

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDE)
import pcbnew  # noqa: E402

CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
URL = 'http://127.0.0.1:8766'


def _m():
    import make_pcb
    import rucni_vodovi
    importlib.reload(rucni_vodovi)
    return importlib.reload(make_pcb)


def postavi(poz):
    p = os.path.join(OVDE, 'make_pcb.py')
    s = open(p, encoding='utf-8').read()
    for r, (x, y, a) in poz.items():
        s, k = re.subn(r"'%s': \([-\d.]+, [-\d.]+, -?\d+\)" % r, "'%s': (%g, %g, %d)" % (r, round(x, 3), round(y, 3), a), s)
        assert k == 1, r
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def ploca():
    m = _m()
    b, _ = m.napravi()
    return b


def pad(b, ref, br):
    for f in b.GetFootprints():
        if f.GetReference() == ref:
            for p in f.Pads():
                if p.GetNumber() == str(br):
                    q = p.GetPosition()
                    return round(pcbnew.ToMM(q.x), 4), round(pcbnew.ToMM(q.y), 4)
    raise KeyError((ref, br))


def vod(net, sloj, w, tacke, b=None):
    """Polilinija: tačka je (x, y) ili (ref, pin). Vraća stavku za RUCNI."""
    pts = [pad(b, *t) if isinstance(t[0], str) else t for t in tacke]
    segs = [(sloj, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], w) for i in range(len(pts) - 1)]
    return (net, segs, [])


def via(net, xy):
    return (net, [], [xy])


def sacuvaj_vodove(lista):
    with open(os.path.join(OVDE, 'rucni_vodovi.py'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('"""Moji ručno nacrtani vodovi: (mreža, [(sloj, x1, y1, x2, y2, širina)], [via]). Dodaje se na PREVODI."""\n')
        f.write('RUCNI = [\n')
        for net, segs, vias in lista:
            f.write('    (%r, %r, %r),\n' % (net, [tuple(round(v, 4) if isinstance(v, float) else v for v in s) for s in segs],
                                          [tuple(round(v, 4) for v in v_) for v_ in vias]))
        f.write(']\n')


def drc(b, ime='apollo_module'):
    # DRC na kandidat-ploči (logs/kandidat.kicad_pcb, sa istim .kicad_pro/.kicad_dru); glavna ploča se snima tek posle uspeha
    import shutil
    kand = os.path.join(OVDE, 'logs', 'kandidat.kicad_pcb')
    for ext in ('.kicad_pro', '.kicad_dru'):
        shutil.copy(os.path.join(OVDE, ime + ext), os.path.join(OVDE, 'logs', 'kandidat' + ext))
    pcbnew.SaveBoard(kand, b)
    rpt = os.path.join(OVDE, 'logs', 'drc_rucno.txt')
    subprocess.run([CLI, 'pcb', 'drc', '--severity-error', '-o', rpt, kand], capture_output=True)
    t = open(rpt, encoding='utf-8', errors='replace').read()
    greske = [blk for blk in t.split('\n[') if not blk.startswith('unconnected') and blk.split(']')[0] in (
        'clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'copper_edge_clearance', 'items_not_allowed',
        'hole_to_hole', 'track_width', 'via_diameter', 'drill_out_of_range', 'solder_mask_bridge')]
    return greske


def prikazi(b):
    T = pcbnew.ToMM
    padovi, vodovi, via_ = [], [], []
    delovi = []
    for f in b.GetFootprints():
        x, y = T(f.GetPosition().x), T(f.GetPosition().y)
        c = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd)
        bb = c.BBox() if not c.IsEmpty() else f.GetBoundingBox(False, False)
        pd = []
        for p in f.Pads():
            q = p.GetPosition()
            pb = p.GetBoundingBox()
            sl = 'FB' if (p.IsOnLayer(pcbnew.F_Cu) and p.IsOnLayer(pcbnew.B_Cu)) else ('F' if p.IsOnLayer(pcbnew.F_Cu) else 'B')
            krug = p.GetShape(pcbnew.F_Cu if 'F' in sl else pcbnew.B_Cu) in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL)
            pd.append([round(T(q.x) - x, 3), round(T(q.y) - y, 3), round(T(pb.GetWidth()), 3), round(T(pb.GetHeight()), 3),
                       'c' if krug else 'r', sl, p.GetNetname()])
        delovi.append(dict(ref=f.GetReference(), pads=pd, box=(T(bb.GetLeft()) - x, T(bb.GetTop()) - y, T(bb.GetRight()) - x,
                                                               T(bb.GetBottom()) - y), sloj='B' if f.IsFlipped() else 'F', x=x, y=y))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            via_.append(dict(x=T(t.GetPosition().x), y=T(t.GetPosition().y), d=T(t.GetWidth(pcbnew.F_Cu)), mreza=t.GetNetname()))
        else:
            vodovi.append(dict(sloj='F' if t.GetLayer() == pcbnew.F_Cu else 'B', x1=T(t.GetStart().x), y1=T(t.GetStart().y),
                               x2=T(t.GetEnd().x), y2=T(t.GetEnd().y), w=T(t.GetWidth()), mreza=t.GetNetname()))
    bb = b.GetBoardEdgesBoundingBox()

    def push(path, e):
        try:
            urllib.request.urlopen(urllib.request.Request(URL + path, data=json.dumps(e).encode('utf-8'),
                                                          headers={'Content-Type': 'application/json'}), timeout=3)
        except Exception as ex:
            print('pregled nedostupan:', ex)
    push('/reset', {})
    push('/push', [{'t': 'ploca', 'x0': T(bb.GetLeft()), 'y0': T(bb.GetTop()), 'x1': T(bb.GetRight()), 'y1': T(bb.GetBottom()),
                    'padovi': padovi, 'vodovi': vodovi, 'via': via_},
                   {'t': 'delovi', 'delovi': delovi}])


def log(tekst, nivo=''):
    try:
        urllib.request.urlopen(urllib.request.Request(URL + '/push', data=json.dumps({'t': 'log', 'tekst': tekst, 'nivo': nivo}).encode('utf-8'),
                                                      headers={'Content-Type': 'application/json'}), timeout=3)
    except Exception:
        pass
    print(tekst, flush=True)


def slika(b, oblast, ime='logs/oblast.png', mreze_oznake=True):
    """Uvećan crtež oblasti (x0, y0, x1, y1): padovi (F crveno-zlatno, B plavo), vodovi, via, oznake mreža i pinova."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    T = pcbnew.ToMM
    x0, y0, x1, y1 = oblast
    fig, ax = plt.subplots(figsize=(14, 14 * (y1 - y0) / (x1 - x0)))
    ax.set_facecolor('#0f3d22')
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            q = t.GetPosition()
            ax.add_patch(Circle((T(q.x), T(q.y)), T(t.GetWidth(pcbnew.F_Cu)) / 2, color='#e0c050', zorder=5))
            ax.add_patch(Circle((T(q.x), T(q.y)), 0.15, color='k', zorder=6))
        else:
            a, c = t.GetStart(), t.GetEnd()
            ax.plot([T(a.x), T(c.x)], [T(a.y), T(c.y)], color='#ff6a5a' if t.GetLayer() == pcbnew.F_Cu else '#5aa0ff',
                    lw=T(t.GetWidth()) * 72 / ((x1 - x0) / 14) * 0.95, solid_capstyle='round', alpha=.85, zorder=3)
    for f in b.GetFootprints():
        for p in f.Pads():
            q = p.GetPosition()
            px, py = T(q.x), T(q.y)
            if not (x0 - 2 < px < x1 + 2 and y0 - 2 < py < y1 + 2):
                continue
            bb = p.GetBoundingBox()
            boja = '#d8b04a' if p.IsOnLayer(pcbnew.F_Cu) else '#6a8fd8'
            ax.add_patch(Rectangle((T(bb.GetLeft()), T(bb.GetTop())), T(bb.GetWidth()), T(bb.GetHeight()), color=boja, alpha=.9, zorder=4))
            if mreze_oznake and x0 < px < x1 and y0 < py < y1:
                ax.text(px, py, '%s.%s\n%s' % (f.GetReference(), p.GetNumber(), p.GetNetname()[:7]), fontsize=5.5,
                        ha='center', va='center', color='k', zorder=7)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.set_aspect('equal')
    ax.grid(True, color='#ffffff22', lw=.4)
    ax.set_xticks(np.arange(int(x0), int(x1) + 1, 1)) if (x1 - x0) < 40 else None
    ax.set_yticks(np.arange(int(y0), int(y1) + 1, 1)) if (y1 - y0) < 40 else None
    ax.tick_params(labelsize=7)
    fig.savefig(os.path.join(OVDE, ime), dpi=110, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------- netlista i zaštita
# Zona za vodove oko procesora: 15 x 15 mm oko RP2040, unutra samo neophodni delovi (odluka korisnika)
ZONA_MCU = (109.5, 129.5, 124.5, 144.5)
PRSTEN_MCU = ((110.3, 130.3, 123.7, 143.7), (112.8, 132.8, 121.2, 141.2), 15.0)   # spoljni, unutrašnji (telo), cena
NEOPHODNI_MCU = {'U7', 'U8', 'C25', 'R29', 'R30', 'Y1', 'C26', 'C27', 'R32', 'R33', 'R34',
                 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C38', 'C39', 'C40', 'C41'}


def u_zoni_mcu(m, b):
    x0, y0, x1, y1 = ZONA_MCU
    out = []
    for f in b.GetFootprints():
        r = f.GetReference()
        if r in NEOPHODNI_MCU:
            continue
        a0, b0, a1, b1 = m.kutija(f)
        if a0 < x1 and x0 < a1 and b0 < y1 and y0 < b1:
            out.append(r)
    return out

VISOKI = {'+34V', 'SW', 'NE', 'NB', 'U3OUT', 'LOOP_DRV', 'LOOP_OUT', 'LOOP_IN', 'PE'}   # pravilo 0,3 mm (.kicad_dru)


def pravila(m=None):
    """Mreža -> (klasa, širina mm, razmak mm) iz KLASE u make_pcb.py (jedini izvor istine) + pravilo za 34 V."""
    m = m or _m()
    pr = {}
    for ime, mreze, w, c in m.KLASE:
        for n in mreze:
            pr[n] = (ime, w / 1000, c / 1000)
    sve = sorted({n for _, (_, _, pins) in m.P.items() for n in pins.values()})
    out = {}
    for n in sve:
        k, w, c = pr.get(n, ('default', 0.2, 0.15))
        if n in VISOKI:
            c = max(c, 0.3)
        if n == 'GND':
            k, w, c = 'masa', 0.3, 0.15
        out[n] = (k, w, c)
    return out


def _nepovezane(rpt):
    t = open(rpt, encoding='utf-8', errors='replace').read()
    nep = set()
    for blk in t.split('\n[unconnected_items]')[1:]:
        for ln in blk.split('\n')[1:4]:
            if '[' in ln and ']' in ln:
                nep.add(ln[ln.index('[') + 1:ln.index(']')])
    return nep


def posalji_netlistu(m, b):
    pr = pravila(m)
    pinova = {}
    for _, (_, _, pins) in m.P.items():
        for n in pins.values():
            pinova[n] = pinova.get(n, 0) + 1
    rpt = os.path.join(OVDE, 'logs', 'drc_rucno.txt')
    nep = _nepovezane(rpt) if os.path.exists(rpt) else set()
    rucne = {n for n, _, _ in __import__('rucni_vodovi').RUCNI}
    redovi = []
    for n, (k, w, c) in sorted(pr.items(), key=lambda x: (x[1][0], x[0])):
        stanje = 'nepovezana' if n in nep else ('povezana' if n not in ('GND',) else 'površina')
        redovi.append([n, k, w, c, pinova.get(n, 0), stanje, n in rucne])
    try:
        urllib.request.urlopen(urllib.request.Request(URL + '/push', data=json.dumps({'t': 'netlista', 'mreze': redovi}).encode('utf-8'),
                                                      headers={'Content-Type': 'application/json'}), timeout=3)
    except Exception:
        pass
    pov = sum(1 for r in redovi if r[5] == 'povezana')
    return pov, len(redovi), len(rucne)


def status(tekst):
    try:
        urllib.request.urlopen(urllib.request.Request(URL + '/push', data=json.dumps({'t': 'stat', 'tekst': tekst}).encode('utf-8'),
                                                      headers={'Content-Type': 'application/json'}), timeout=3)
    except Exception:
        pass


def _proveri_sirine(m, rucni):
    pr = pravila(m)
    greske = []
    for net, segs, vias in rucni:
        w_min = pr.get(net, ('', 0.2, 0.15))[1]
        for s in segs:
            sl, x1, y1, x2, y2, w = s
            duz = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5
            if w + 1e-6 < w_min and not (w >= 0.2 - 1e-6 and duz <= 2.0):   # suženje do 2 mm za izlaz iz sitnog kućišta
                greske.append('%s: vod %.2f mm uži od %.2f mm (dužina %.2f mm)' % (net, w, w_min, duz))
    return greske


def primeni(poz=None, vodovi=None, opis=''):
    """Transakcija: upiši raspored/vodove, izgradi, proveri preklapanja + širine + DRC; pri grešci sve vrati."""
    import shutil
    mp, rv = os.path.join(OVDE, 'make_pcb.py'), os.path.join(OVDE, 'rucni_vodovi.py')
    shutil.copy(mp, mp + '.pre')
    shutil.copy(rv, rv + '.pre')
    try:
        if poz:
            postavi(poz)
        if vodovi is not None:
            sacuvaj_vodove(vodovi)
        m = _m()
        b, _ = m.napravi()
        problemi = ['preklapanje: %s' % (p,) for p in m.preklapanja(b)]
        problemi += ['%s nije neophodan, a stoji u zoni 15x15 mm oko RP2040' % r for r in u_zoni_mcu(m, b)]
        problemi += _proveri_sirine(m, __import__('rucni_vodovi').RUCNI)
        if not problemi:
            problemi = ['DRC: ' + g.split('\n')[0] + ' | ' + ' | '.join(l.strip() for l in g.split('\n')[2:4]) for g in drc(b)]
    except Exception as ex:
        problemi = ['izuzetak: %r' % ex]
    if problemi:
        shutil.copy(mp + '.pre', mp)
        shutil.copy(rv + '.pre', rv)
        log('✗ ODBIJENO (%s): %d problema – izmena vraćena' % (opis, len(problemi)), 'e')
        status('Ručni rad · ODBIJENO: %s · %d problema, ploča vraćena na prethodno stanje' % (opis, len(problemi)))
        for p in problemi[:12]:
            log('   ' + p, 'e')
        return False, problemi
    pcbnew.SaveBoard(os.path.join(OVDE, 'apollo_module.kicad_pcb'), b)   # tek sada: prošlo sve provere
    prikazi(b)
    pov, uk, ru = posalji_netlistu(m, b)
    status('Ručni rad · %s · DRC: 0 grešaka · preklapanja: 0 · povezano %d/%d mreža (%d ručno nacrtanih) · ploča %.0f×%.0f mm' % (
        opis, pov, uk, ru, m.X1 - m.X0, m.Y1 - m.Y0))
    log('✓ %s – bez preklapanja i bez DRC grešaka' % opis, 'ok')
    return True, b


def ruter_korak(mreze, opis, gnd_refs=None, skupi_prstenovi=()):
    """Moj ruter (tools/ruter/motor.py) na zadate mreže po mojim pravilima; svi NOVI vodovi i via se prepisuju u
    rucni_vodovi.py (zaključano) i prolaze zaštitu. gnd_refs: delovi čiji GND padovi dobijaju sopstvenu via."""
    sys.path.insert(0, os.path.join(OVDE, '../../../../tools/ruter'))
    from motor import Ruter
    import rucni_vodovi
    importlib.reload(rucni_vodovi)
    r = Ruter(os.path.join(OVDE, 'apollo_module.kicad_pcb'), pregled=URL, visoki=list(VISOKI))
    pre = {t.m_Uuid.AsString() for t in r.b.GetTracks()}
    for (ox0, oy0, ox1, oy1), (ix0, iy0, ix1, iy1), cena in skupi_prstenovi:   # skup prsten: kanal za signale oko čipa
        (si, sj), _, _ = r._prozor(ox0, oy0, ox1, oy1)
        r.cena_zona[:, si, sj] = cena
        (si, sj), _, _ = r._prozor(ix0, iy0, ix1, iy1)
        r.cena_zona[:, si, sj] = 1.0
    if gnd_refs:
        r.gnd_fanout('GND', refs=set(gnd_refs), opis=opis)
    neuspele = r.izvrsi(mreze) if mreze else []
    T = pcbnew.ToMM
    novi = []
    for t in r.b.GetTracks():
        if t.m_Uuid.AsString() in pre:
            continue
        if t.GetClass() == 'PCB_VIA':
            novi.append((t.GetNetname(), [], [(round(T(t.GetPosition().x), 4), round(T(t.GetPosition().y), 4))]))
        else:
            novi.append((t.GetNetname(), [('F' if t.GetLayer() == pcbnew.F_Cu else 'B', round(T(t.GetStart().x), 4),
                                           round(T(t.GetStart().y), 4), round(T(t.GetEnd().x), 4), round(T(t.GetEnd().y), 4),
                                           round(T(t.GetWidth()), 3))], []))
    log('ruter: %d novih elemenata (%s); nepovezane: %s' % (len(novi), opis, ', '.join(neuspele) or 'nema'))
    return primeni(None, list(rucni_vodovi.RUCNI) + novi, opis)
