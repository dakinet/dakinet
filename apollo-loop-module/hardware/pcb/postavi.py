"""Automatski raspored delova Apollo modula po mojim pravilima (tools/ruter/postavljac.py, 16 paralelnih lanaca).

Pokretanje (KiCad Python):  python postavi.py [sekundi_po_lancu] [--upisi]
  bez --upisi samo prikazuje rezultat; sa --upisi menja POZ u make_pcb.py, pa razmakni.py uklanja preostala
  preklapanja po stvarnim courtyard-ima.

Pravila:
  - FIKSNO: jezgra prekidačkih napajanja sa ručno nacrtanim strujnim putevima (TI layout), izlazni stepen Q1/R13
    sa bakrom za hlađenje, letvica sa ulazom (F1, D1), TVS D3 i šant R19/R20 – oni su već po dobroj praksi
  - blokadni kondenzator je vezan za tačan pin napajanja svog IC-a (par velike težine)
  - kristal i analogni čvorovi imaju veću težinu (kratko); velike mreže (+3V3) manju; GND se ne računa (via u masu)
  - oko MCU (SSOP-28) slobodan prsten 0,6 mm za izlaz vodova, oko ostalih delova 0,25 mm (prolaz za vod)
"""
import os
import sys

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDE)
sys.path.insert(0, os.path.join(OVDE, '../../../../tools/ruter'))
import numpy as np  # noqa: E402
import pcbnew  # noqa: E402
import make_pcb as m  # noqa: E402
import postavljac  # noqa: E402

FIKSNO = {
    # boost jezgro (SW čvor, izlazna petlja, ulazni kondenzatori) – ručno nacrtani putevi
    'U1', 'L1', 'D2', 'C36', 'C3', 'C4', 'C5', 'C2', 'C9', 'C35',
    # buck jezgro
    'U2', 'C10', 'C37', 'C11', 'L2',
    # izlazni stepen i petlja (NE, LOOP_DRV ručno)
    'Q1', 'R13', 'Q4', 'R14', 'F2',
    # letvica, ulaz, TVS i šant uz konektor
    'J1', 'F1', 'D1', 'D3', 'R19', 'R20',
}
# blokadni kondenzator / kratka veza -> (IC, pin)   (AVR64DD28: VDD 14/20, VDDIO2 6, RESET 18, XTALHF 22/23)
BLOKADA = {
    'C25': ('U7', '14'), 'C28': ('U7', '20'), 'C29': ('U7', '6'), 'C32': ('U7', '14'),
    'Y1': ('U7', '22'), 'R29': ('U7', '18'), 'C30': ('U7', '18'),
    'C20': ('U4', '8'), 'C23': ('U6', '5'), 'C15': ('U3', '7'),
    'C12': ('L2', '2'), 'C13': ('L2', '2'), 'C26': ('Y1', '1'), 'C27': ('Y1', '3'),
    'C8': ('U1', '5'), 'R2': ('U1', '9'), 'R4': ('U1', '8'), 'C7': ('U1', '8'), 'R3': ('U1', '10'),
    'D6': ('F1', '2'), 'C1': ('D1', '1'),
}
TEZINA_BLOKADE = 15.0
VAZNE = {'XIN': 3, 'XO': 3, 'BFB': 3, 'COMP': 3, 'CC': 2, 'FREQ': 2, 'SS': 2, 'FB': 2, 'VSET': 2,
         'NA': 2, 'IAMP': 1.5, 'OC_IN': 1.5, 'RESET': 1.5, 'UPDI': 1.5}
PRSTEN = {'U7': 0.6, 'U3': 0.35, 'U4': 0.35, 'U6': 0.3}
PRSTEN_OST = 0.25


def napravi_model():
    b, _ = m.napravi()
    fpd = {f.GetReference(): f for f in b.GetFootprints()}
    imena = sorted(m.POZ)
    blokovi = {r: bi for bi, (_, refs) in enumerate(m.BLOKOVI) for r in refs}
    mreze = sorted({n for _, (_, _, pins) in m.P.items() for n in pins.values()} - {'GND'})
    mid = {n: i for i, n in enumerate(mreze)}
    T = pcbnew.ToMM
    d = dict(imena=imena, pomicni=[], rot_dozv=[], pad_dx=[], pad_dy=[], pad_net=[], okvir=[], blok=[], tip=[],
             x=[], y=[], k=[])
    pad_ind = {}
    for i, r in enumerate(imena):
        f = fpd[r]
        x, y, _ = m.POZ[r]
        pads = list(f.Pads())
        d.setdefault('pad_info', []).append([
            [round(T(p.GetPosition().x) - x, 3), round(T(p.GetPosition().y) - y, 3),
             round(T(p.GetBoundingBox().GetWidth()), 3), round(T(p.GetBoundingBox().GetHeight()), 3),
             'c' if p.GetShape(pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu) in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL) else 'r',
             'FB' if (p.IsOnLayer(pcbnew.F_Cu) and p.IsOnLayer(pcbnew.B_Cu)) else ('F' if p.IsOnLayer(pcbnew.F_Cu) else 'B'),
             p.GetNetname()] for p in pads])
        d.setdefault('crtyd', []).append((x0_ := m.kutija(f)[0] - x, m.kutija(f)[1] - y, m.kutija(f)[2] - x, m.kutija(f)[3] - y))
        d.setdefault('strana', []).append('B' if f.IsFlipped() else 'F')
        d['pad_dx'].append(np.array([T(p.GetPosition().x) - x for p in pads]))
        d['pad_dy'].append(np.array([T(p.GetPosition().y) - y for p in pads]))
        d['pad_net'].append(np.array([mid.get(p.GetNetname(), -1) for p in pads]))
        for k, p in enumerate(pads):
            pad_ind[(r, p.GetNumber())] = k
        x0, y0, x1, y1 = m.kutija(f)
        g = PRSTEN.get(r, PRSTEN_OST) if r not in FIKSNO else 0.05
        d['okvir'].append((x0 - x - g, y0 - y - g, x1 - x + g, y1 - y + g))
        d['pomicni'].append(r not in FIKSNO)
        d['rot_dozv'].append([0, 1, 2, 3] if r not in FIKSNO else [0])
        d['blok'].append(blokovi.get(r, 99))
        d['tip'].append(m.P[r][0])
        d['x'].append(x)
        d['y'].append(y)
        d['k'].append(0)
    d['pad_ind'] = pad_ind
    tez = []
    for n in mreze:
        br = sum(1 for _, (_, _, pins) in m.P.items() for v in pins.values() if v == n)
        tez.append(VAZNE.get(n, 0.3 if br > 8 else 1.0))
    d['tezina'] = tez
    d['parovi'] = []
    ind = {r: i for i, r in enumerate(imena)}
    for c, (ic, pin) in BLOKADA.items():
        d['parovi'].append((ind[c], pad_ind[(c, '1')], ind[ic], pad_ind[(ic, pin)], TEZINA_BLOKADE))
    d['ploca'] = (m.X0 + 0.4, m.Y0 + 0.4, m.X1 - 0.4, m.Y1 - 0.4)
    return d


def upisi(d, rez):
    import re
    s = open(os.path.join(OVDE, 'make_pcb.py'), encoding='utf-8').read()
    n = 0
    for i, r in enumerate(d['imena']):
        if not d['pomicni'][i]:
            continue
        x, y, rot0 = m.POZ[r]
        nx, ny = round(rez['x'][i] / 0.05) * 0.05, round(rez['y'][i] / 0.05) * 0.05
        nr = (rot0 + 90 * rez['k'][i]) % 360
        s, k = re.subn(r"'%s': \([-\d.]+, [-\d.]+, -?\d+\)" % r, "'%s': (%g, %g, %d)" % (r, round(nx, 2), round(ny, 2), nr), s)
        assert k == 1, r
        n += 1
    open(os.path.join(OVDE, 'make_pcb.py'), 'w', encoding='utf-8', newline='\n').write(s)
    return n


def posalji_pregled(d, url='http://127.0.0.1:8765'):
    import json
    import urllib.request

    def push(path, e):
        try:
            urllib.request.urlopen(urllib.request.Request(url + path, data=json.dumps(e).encode('utf-8'),
                                                          headers={'Content-Type': 'application/json'}), timeout=3)
        except Exception:
            pass
    b, _ = m.napravi()
    T = pcbnew.ToMM
    vodovi, via = [], []
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            via.append(dict(x=T(t.GetPosition().x), y=T(t.GetPosition().y), d=T(t.GetWidth(pcbnew.F_Cu)), mreza=t.GetNetname()))
        else:
            vodovi.append(dict(sloj='F' if t.GetLayer() == pcbnew.F_Cu else 'B', x1=T(t.GetStart().x), y1=T(t.GetStart().y),
                               x2=T(t.GetEnd().x), y2=T(t.GetEnd().y), w=T(t.GetWidth()), mreza=t.GetNetname()))
    push('/reset', {})
    push('/push', [{'t': 'ploca', 'x0': m.X0, 'y0': m.Y0, 'x1': m.X1, 'y1': m.Y1, 'padovi': [], 'vodovi': vodovi, 'via': via},
                   {'t': 'delovi', 'delovi': [dict(ref=r, pads=d['pad_info'][i], box=d['crtyd'][i], sloj=d['strana'][i],
                                                  x=d['x'][i], y=d['y'][i]) for i, r in enumerate(d['imena'])]},
                   {'t': 'log', 'tekst': 'Raspored: %d delova (%d pomični), %d mreža, %d parova blokade' % (
                       len(d['imena']), sum(d['pomicni']), len(d['tezina']), len(d['parovi'])), 'nivo': ''}])


if __name__ == '__main__':
    vreme = float(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1][0].isdigit() else 60.0
    d = napravi_model()
    pocetak = postavljac.zari(d, seme=0, vreme=0.01)
    print('polazno:  cena %.1f  HPWL %.1f mm  preklapanje %.2f mm2  zagušenje %.1f' %
          (pocetak['cena'], pocetak['hpwl'], pocetak['preklapanje'], pocetak['zagusenje']), flush=True)
    posalji_pregled(d)
    if '--cpu' in sys.argv:
        rez = postavljac.paralelno(d, lanaca=16, vreme=vreme)
    elif '--oba' in sys.argv:                       # 15 lanaca na procesoru + GPU istovremeno, bira se najbolji
        from multiprocessing import Pool
        import postavljac_gpu2
        with Pool(15) as pool:
            cpu = pool.map_async(postavljac._radnik, [(d, s_, vreme) for s_ in range(15)])
            G = postavljac_gpu2.GpuPostavljac2(d, lanaca=int(os.environ.get('LANACA', 512)))
            g = G.radi(vreme, url='http://127.0.0.1:8765')
            g['seme'] = 'GPU'
            rez = sorted(cpu.get() + [g], key=lambda r: r['cena'])
        print('GPU:', postavljac_gpu2.GPU, flush=True)
    else:
        import postavljac_gpu2
        lanaca = int(os.environ.get('LANACA', 512))
        G = postavljac_gpu2.GpuPostavljac2(d, lanaca=lanaca)
        print('GPU:', postavljac_gpu2.GPU, ' lanaca:', lanaca, flush=True)
        rez = [G.radi(vreme, url='http://127.0.0.1:8765')]
    for r in rez[:5]:
        print('lanac %4s: cena %.1f  HPWL %.1f mm  preklapanje %.2f mm2  zagušenje %.1f  (%d koraka, %s poteza)' %
              (r['seme'], r['cena'], r['hpwl'], r['preklapanje'], r['zagusenje'], r['iteracija'], r.get('potezi', '-')), flush=True)
    if '--upisi' in sys.argv:
        print('upisano delova:', upisi(d, rez[0]))
