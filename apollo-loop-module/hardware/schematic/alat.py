"""Mali sloj iznad schemdraw-a: crtanje sa evidencijom pinova i žica + provera povezanosti prema netlisti pločice.

Svaki nacrtani pin se beleži kao (oznaka, broj pina) na tački crteža. Na kraju se iz žica, oznaka mreža (tag),
simbola napajanja i mase izračunaju mreže i porede sa P iz ../pcb/make_pcb.py (izvor istine):
  - svaki pin iz P mora biti nacrtan, u tačno jednoj mreži, zajedno sa svim pinovima te mreže i ni sa jednim drugim;
  - nepovezani pinovi IC-a moraju imati oznaku NC (X);
  - žica ne sme da prolazi preko tela elementa; T-spojevi i čvorovi sa >= 3 grane dobijaju tačku.
"""
import math
import os

import schemdraw
import schemdraw.elements as elm

ACC = '#b4441f'      # boja oznaka mreža
SIVA = '#555555'


def ucitaj_P():
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pcb', 'make_pcb.py')
    s = open(src, encoding='utf-8').read()
    a, b = s.index('R0603 ='), s.index('# delovi sa donje')
    ns = {'os': os, 'FP': ''}
    exec(s[a:b], ns)            # samo konstante i rečnik P, bez pcbnew
    return ns['P']


def _t(p):
    return (round(float(p[0]), 3), round(float(p[1]), 3))


def _na_duzi(p, a, b, eps=1e-3):
    """p leži na unutrašnjosti duži a-b (ne na krajevima)."""
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > eps * max(1, math.hypot(x2 - x1, y2 - y1)):
        return False
    if min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps:
        return math.hypot(x - x1, y - y1) > eps and math.hypot(x - x2, y - y2) > eps
    return False


def _sece_pravougaonik(a, b, bb):
    """Da li duž a-b ulazi u unutrašnjost pravougaonika bb=(x0,y0,x1,y1) (Liang-Barsky)."""
    x0, y0, x1, y1 = bb
    if x1 <= x0 or y1 <= y0:
        return False
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if abs(p) < 1e-12:
            if q <= 0:
                return False
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
    return t1 - t0 > 1e-6


def vrednost(v):
    """'10u/50V' -> '10µ/50V', '100n' ostaje; razmak -> novi red."""
    out = []
    for i, ch in enumerate(v):
        if ch == 'u' and i > 0 and v[i - 1].isdigit():
            ch = 'µ'
        out.append(ch)
    return ''.join(out).replace(' ', '\n')


class Sema:
    def __init__(self, d, P, fs=7.5):
        self.d, self.P, self.fs = d, P, fs
        self.zice = []          # (a, b)
        self.pinovi = {}        # (ref, pin) -> tačka
        self.imena = []         # (tačka, ime mreže)   tag / napajanje / masa
        self.nc = set()         # (ref, pin)
        self.tela = []          # (ref, bbox, {tačke pinova})
        self.nacrtani = set()   # oznake nacrtanih elemenata
        self.nepolarni = set()  # (ref) R, C, L, F – pin 1/2 svejedno

    # ------------------------------------------------------------ osnovno
    def w(self, *pts):
        pts = [_t(p) for p in pts]
        for a, b in zip(pts, pts[1:]):
            if a != b:
                self.d.add(elm.Line().at(a).to(b))
                self.zice.append((a, b))
        return pts[-1]

    def txt(self, p, t, **k):
        k.setdefault('fontsize', self.fs)
        self.d.add(elm.Label().at(_t(p)).label(t, **k))

    def _pin(self, ref, pin, p):
        assert (ref, pin) not in self.pinovi, ('dupli pin', ref, pin)
        self.pinovi[(ref, pin)] = _t(p)

    def _telo(self, ref, e, pts, smanji=0.12):
        bb = e.get_bbox(transform=True, includetext=False)
        self.tela.append((ref, (bb.xmin + smanji, bb.ymin + smanji, bb.xmax - smanji, bb.ymax - smanji),
                          {_t(p) for p in pts}))

    # ------------------------------------------------------------ mreže po imenu
    def gnd(self, p):
        self.d.add(elm.Ground(lead=False).theta(0).at(_t(p)))
        self.imena.append((_t(p), 'GND'))

    def vcc(self, p, ime, dole=False):
        e = elm.Vdd(lead=True).theta(0).at(_t(p))
        if dole:
            e = e.flip()
        self.d.add(e.label(ime, fontsize=self.fs, color=ACC))
        self.imena.append((_t(p), ime))

    def tag(self, p, ime, smer='r'):
        """Oznaka mreže (zastavica) sa vrhom u tački p; smer 'r' – telo desno od p, 'l' – levo."""
        wdt = 0.42 + 0.115 * len(ime)
        e = elm.Tag(width=wdt, height=0.5).at(_t(p)).label(ime, fontsize=self.fs - 0.5, color=ACC)
        e = e.right() if smer == 'r' else e.left()
        self.d.add(e)
        self.imena.append((_t(p), ime))

    def nepovezan(self, ref, pin):
        p = self.pinovi[(ref, pin)]
        self.d.add(elm.NoConnect().theta(0).at(p))
        self.nc.add((ref, pin))

    # ------------------------------------------------------------ elementi sa dva kraja
    def dv(self, ref, a, b, t=None, ofs=0.0, ime=None):
        """Element sa dva kraja od tačke a do b. Oznaka i vrednost se uzimaju iz P.
        Pinovi: R/C/L/F start=1, end=2 (nepolarni: provera dozvoljava zamenu); diode: start=anoda(2), end=katoda(1);
        C1/C5 (elektrolit): start = + (pin 1)."""
        _, val, pins = self.P[ref]
        a, b = _t(a), _t(b)
        k = ref.rstrip('0123456789')
        if k == 'R':
            e = elm.Resistor()
        elif k == 'C':
            e = elm.Capacitor(polar=ref in ('C1', 'C5'))
        elif k == 'L':
            e = elm.Inductor2(loops=3)
        elif k == 'F':
            e = elm.Fuse()
        elif k == 'D':
            # u 'with Drawing()' svaki napravljeni element se automatski crta – praviti samo jedan
            e = elm.Zener() if ref == 'D3' else elm.LED() if ref == 'D5' else elm.Schottky()
        elif k == 'Y':
            e = elm.Crystal()
        else:
            raise ValueError(ref)
        e = self.d.add(e.at(a).to(b))
        if k == 'D':
            self._pin(ref, '2', a); self._pin(ref, '1', b)
        elif k == 'Y':                       # kvarc 3225: 1 i 3 su kristal, 2 i 4 kućište
            self._pin(ref, '1', a); self._pin(ref, '3', b)
        else:
            self._pin(ref, '1', a); self._pin(ref, '2', b)
            if k in 'RLF' or (k == 'C' and ref not in ('C1', 'C5')):
                self.nepolarni.add(ref)
        self._telo(ref, e, [a, b], smanji=0.18)
        self.nacrtani.add(ref)
        # tekst: oznaka + vrednost
        vert = abs(a[0] - b[0]) < 1e-6
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        s = '%s\n%s' % (ref, vrednost(ime or val))
        if t is None:
            t = 'r' if vert else 't'
        if t == 'r':
            self.txt((cx + 0.42, cy + ofs), s, halign='left', valign='center')
        elif t == 'l':
            self.txt((cx - 0.42, cy + ofs), s, halign='right', valign='center')
        elif t == 't':
            self.txt((cx + ofs, cy + 0.38), s, halign='center', valign='bottom')
        else:
            self.txt((cx + ofs, cy - 0.38), s, halign='center', valign='top')
        return e

    # ------------------------------------------------------------ tranzistori, OP, IC
    def tr(self, ref, e, mapa, t='r', ofs=(0, 0), brojevi=True):
        """mapa: anchor -> pin (npr. {'base': '1', 'emitter': '2', 'collector': '3'})."""
        _, val, _ = self.P[ref]
        e = self.d.add(e.theta(0))
        for an, pin in mapa.items():
            p = e.absanchors[an]
            self._pin(ref, pin, p)
        self._telo(ref, e, [e.absanchors[a] for a in mapa])
        self.nacrtani.add(ref)
        bb = e.get_bbox(transform=True, includetext=False)
        cy = (bb.ymin + bb.ymax) / 2
        if t == 'r':
            self.txt((bb.xmax + 0.2 + ofs[0], cy + ofs[1]), '%s\n%s' % (ref, val), halign='left', valign='center')
        else:
            self.txt((bb.xmin - 0.2 + ofs[0], cy + ofs[1]), '%s\n%s' % (ref, val), halign='right', valign='center')
        if brojevi:
            for an, pin in mapa.items():
                p = e.absanchors[an]
                self.txt((p[0] + 0.12, p[1] + 0.12), pin, fontsize=self.fs - 2, color=SIVA, halign='left', valign='bottom')
        return e

    def oa(self, ref, e, mapa, naziv, t_ofs=(0, 0)):
        """Operacioni pojačavač / komparator; mapa: anchor (in1 '-', in2 '+', out) -> pin."""
        e = self.d.add(e.theta(0))
        for an, pin in mapa.items():
            self._pin(ref, pin, e.absanchors[an])
            p = e.absanchors[an]
            dx = 0.1 if an == 'out' else -0.1
            self.txt((p[0] + (0.25 if an == 'out' else -0.05) , p[1] + 0.1), pin, fontsize=self.fs - 2, color=SIVA,
                     halign='left' if an == 'out' else 'right', valign='bottom')
        self._telo(ref, e, [e.absanchors[a] for a in mapa], smanji=0.25)
        self.nacrtani.add(ref)
        c = e.absanchors['center']
        self.txt((c[0] - 0.55 + t_ofs[0], c[1] + 1.25 + t_ofs[1]), naziv, halign='left', valign='bottom')
        return e

    def ic(self, ref, strane, naziv=None, pinspacing=0.9, rot=90, **kw):
        """strane: {'left': [(pin, ime) ili None za razmak, ...] odozgo nadole, 'right': ..., 'top': [s leva], 'bottom': ...}
        Vraća element; pin p<broj> je anchor."""
        _, val, _ = self.P[ref]
        pins = []
        for side, lst in strane.items():
            n = len(lst)
            for i, it in enumerate(lst):
                if it is None:
                    continue
                pin, ime = it
                slot = (n - i) if side in ('left', 'right') else (i + 1)
                pins.append(elm.IcPin(name=ime, pin=pin, side=side, slot='%d/%d' % (slot, n),
                                      anchorname='p' + pin, rotation=rot if side in ('top', 'bottom') else 0))
        kw.setdefault('pinspacing', pinspacing)
        kw.setdefault('edgepadW', 1.0)
        kw.setdefault('edgepadH', 0.6)
        kw.setdefault('leadlen', 0.6)
        kw.setdefault('fontsize', self.fs - 0.5)
        kw.setdefault('lsize', self.fs - 0.5)
        e = elm.Ic(pins=pins, label=naziv or '%s\n%s' % (ref, val), lblsize=self.fs + 1, **kw)
        return e

    def ic_dodaj(self, ref, e):
        e = self.d.add(e.theta(0))
        pts = []
        for an, p in e.absanchors.items():
            if an.startswith('p') and an[1:].isdigit():
                self._pin(ref, an[1:], p)
                pts.append(p)
        self._telo(ref, e, pts, smanji=0.05)
        self.nacrtani.add(ref)
        return e

    def pin_rucno(self, ref, pin, p):
        """Pin koji nema svoj anchor (npr. kućište kvarca)."""
        self._pin(ref, pin, p)

    # ------------------------------------------------------------ provera
    def proveri(self):
        greske, upoz = [], []
        # sve tačke od interesa
        tacke = set()
        for a, b in self.zice:
            tacke.add(a); tacke.add(b)
        tacke |= set(self.pinovi.values())
        tacke |= {p for p, _ in self.imena}
        par = {p: p for p in tacke}

        def nadji(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x

        def spoji(a, b):
            ra, rb = nadji(a), nadji(b)
            if ra != rb:
                par[ra] = rb

        for a, b in self.zice:
            spoji(a, b)
        # tačka na unutrašnjosti žice = spoj (T); i preklapanje kolinearnih žica
        broj = {p: 0 for p in tacke}
        for a, b in self.zice:
            broj[a] += 1; broj[b] += 1
        for p in tacke:
            for a, b in self.zice:
                if _na_duzi(p, a, b):
                    spoji(p, a)
                    broj[p] += 2
        for p in self.pinovi.values():
            broj[p] += 1
        # isto ime -> ista mreža
        po_imenu = {}
        for p, ime in self.imena:
            po_imenu.setdefault(ime, []).append(p)
        for ime, ps in po_imenu.items():
            for p in ps[1:]:
                spoji(ps[0], p)
        # tačke spojeva
        for p in tacke:
            if broj[p] >= 3:
                self.d.add(elm.Dot(radius=0.09).at(p))
        # grupe pinova
        grupe = {}
        for k, p in self.pinovi.items():
            grupe.setdefault(nadji(p), []).append(k)
        imena_grupe = {}
        for p, ime in self.imena:
            imena_grupe.setdefault(nadji(p), set()).add(ime)
        # pinovi iz P
        ocek = {}
        for ref, (_, _, pins) in self.P.items():
            for pin, net in pins.items():
                ocek[(ref, pin)] = net
        for k in ocek:
            if k not in self.pinovi:
                greske.append('pin nije nacrtan: %s.%s (%s)' % (k[0], k[1], ocek[k]))
        for k in self.pinovi:
            if k not in ocek and k not in self.nc:
                if len(grupe[nadji(self.pinovi[k])]) > 1:
                    greske.append('pin %s.%s nije u netlisti a povezan je' % k)
                else:
                    greske.append('pin %s.%s nije u netlisti i nema NC oznaku' % k)
        for k in self.nc:
            if len(grupe[nadji(self.pinovi[k])]) > 1 or nadji(self.pinovi[k]) in imena_grupe:
                greske.append('NC pin %s.%s je povezan' % k)
        # imenovanje grupa: polarni pinovi i oznake određuju ime; nepolarni dvopolni elementi se rešavaju eliminacijom
        kand = {}
        for g, ks in grupe.items():
            s = set(imena_grupe.get(g, set()))
            for k in ks:
                if k in ocek and k[0] not in self.nepolarni:
                    s.add(ocek[k])
            kand[g] = s
        for g, s in imena_grupe.items():
            if g not in kand:
                kand[g] = set(s)
        promena = True
        while promena:
            promena = False
            for ref in self.nepolarni:
                if (ref, '1') not in self.pinovi or (ref, '2') not in self.pinovi:
                    continue
                n1, n2 = ocek[(ref, '1')], ocek[(ref, '2')]
                g1, g2 = nadji(self.pinovi[(ref, '1')]), nadji(self.pinovi[(ref, '2')])
                for ga, gb in ((g1, g2), (g2, g1)):
                    if len(kand[ga]) == 1 and not kand[gb]:
                        (na,) = kand[ga]
                        if na in (n1, n2):
                            kand[gb] = {n2 if na == n1 else n1}
                            promena = True
        for g, s in kand.items():
            if len(s) > 1:
                greske.append('KRATAK SPOJ mreža %s: %s' % (sorted(s), sorted('%s.%s' % k for k in grupe.get(g, []))))
            if not s and g in grupe and not all(k in self.nc for k in grupe[g]):
                greske.append('neimenovana grupa: %s' % sorted('%s.%s' % k for k in grupe[g]))
        # svaka mreža tačno jedna grupa
        net_grupe = {}
        for g, s in kand.items():
            for n in s:
                net_grupe.setdefault(n, set()).add(g)
        for n, gs in net_grupe.items():
            if len(gs) > 1:
                delovi = [sorted('%s.%s' % k for k in grupe.get(g, [])) or ['(samo oznaka)'] for g in gs]
                greske.append('PREKID mreže %s: %s' % (n, delovi))
        # nepolarni: krajevi moraju biti {n1, n2}
        for ref in self.nepolarni:
            n1, n2 = ocek[(ref, '1')], ocek[(ref, '2')]
            g1, g2 = nadji(self.pinovi[(ref, '1')]), nadji(self.pinovi[(ref, '2')])
            if sorted([tuple(kand[g1]), tuple(kand[g2])]) != sorted([(n1,), (n2,)]):
                greske.append('%s spaja %s/%s, očekivano %s/%s' % (ref, kand[g1], kand[g2], n1, n2))
        # polarni pinovi: grupa mora nositi ime iz P
        for k, p in self.pinovi.items():
            if k in ocek and k[0] not in self.nepolarni and ocek[k] not in kand[nadji(p)]:
                greske.append('%s.%s u mreži %s, očekivano %s' % (k[0], k[1], kand[nadji(p)], ocek[k]))
        # imena koja ne postoje u P
        sve = set(ocek.values())
        for _, ime in self.imena:
            if ime not in sve:
                greske.append('oznaka %s ne postoji u netlisti' % ime)
        # elementi
        for ref in self.P:
            if ref not in self.nacrtani:
                greske.append('element nije nacrtan: ' + ref)
        # žica preko tela elementa
        for ref, bb, pp in self.tela:
            for a, b in self.zice:
                if _sece_pravougaonik(a, b, bb):
                    upoz.append('žica %s-%s prelazi preko %s' % (a, b, ref))
        # ukrštanja žica bez spoja (dozvoljeno, ali brojimo)
        ukrst = 0
        for i, (a, b) in enumerate(self.zice):
            for c, e in self.zice[i + 1:]:
                if _ukrstanje(a, b, c, e):
                    ukrst += 1
                    upoz.append('ukrštanje %s-%s / %s-%s' % (a, b, c, e))
        return greske, upoz


def _ukrstanje(a, b, c, d):
    """Pravo ukrštanje (unutrašnje tačke obe duži), bez zajedničkih krajeva."""
    def orient(p, q, r):
        v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return o1 * o2 < 0 and o3 * o4 < 0
