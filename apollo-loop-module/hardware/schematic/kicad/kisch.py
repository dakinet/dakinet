"""Generator KiCad šeme (.kicad_sch) iz Python opisa: simboli iz KiCad biblioteka, žice, oznake, napajanje.

Koordinate se zadaju u koracima mreže G = 2,54 mm (dozvoljene polovine), Y raste nadole (kao u KiCad-u).
Pinovi se računaju iz definicije simbola u biblioteci (rotacija / ogledalo), pa su krajevi žica tačno na pinovima.
"""
import math
import os
import uuid

import sexp
from sexp import Sym as S

G = 2.54
LIBDIR = os.environ.get('KICAD_SYMBOLS', r'C:/Program Files/KiCad/10.0/share/kicad/symbols/')
_LIB = {}


def uid():
    return str(uuid.uuid4())


def mm(v):
    return round(v * G, 4)


def _lib(name):
    if name not in _LIB:
        _LIB[name] = sexp.parse(open(os.path.join(LIBDIR, name + '.kicad_sym'), encoding='utf-8').read())
    return _LIB[name]


def _rename(node, old, new):
    """Preimenuje pod-simbole old_U_S -> new_U_S."""
    out = []
    for it in node:
        if isinstance(it, list) and it and it[0] == 'symbol' and isinstance(it[1], str) and it[1].startswith(old + '_'):
            it = [it[0], new + it[1][len(old):]] + it[2:]
        out.append(it)
    return out


def lib_symbol(lib_id):
    """Vraća (ravnu) definiciju simbola iz biblioteke, ime = 'Lib:Ime', razrešen 'extends'."""
    lib, name = lib_id.split(':')
    tree = _lib(lib)
    syms = {s[1]: s for s in sexp.find(tree, 'symbol')}
    s = syms[name]
    ext = sexp.first(s, 'extends')
    if ext:
        par = syms[ext[1]]
        dete = {p[1]: p for p in sexp.find(s, 'property')}
        props = [dete.pop(p[1], p) for p in sexp.find(par, 'property')] + list(dete.values())
        body = [x for x in par[2:] if not (isinstance(x, list) and x and x[0] in ('property', 'extends'))]
        body = _rename(body, ext[1], name)
        s = ['symbol', name] + [x for x in s[2:] if isinstance(x, list) and x[0] not in ('extends', 'property', 'symbol')] \
            + props + body
    s = [S('symbol'), lib_id] + s[2:]
    return s


def pins_of(symdef):
    """{(unit, broj): (x, y, ugao_u_stepenima)} u koordinatama biblioteke (Y nagore). unit 0 = zajednički."""
    out = {}
    for u in sexp.find(symdef, 'symbol'):
        parts = u[1].rsplit('_', 2)
        unit = int(parts[-2])
        for p in sexp.find(u, 'pin'):
            at = sexp.first(p, 'at')
            num = sexp.first(p, 'number')[1]
            out[(unit, num)] = (float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0)
    return out


def _tf(x, y, rot, mirror):
    """Iz koordinata biblioteke (Y nagore) u ekranski pomeraj (Y nadole)."""
    y = -y
    if mirror == 'x':
        y = -y
    elif mirror == 'y':
        x = -x
    r = math.radians(rot)
    return (x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r))


def custom_ic(lib_id, body, pins, ref='U'):
    """Jednostavan pravougaoni simbol. body=(x0,y0,x1,y1) u G (Y nagore); pins: [(broj, ime, x, y, ugao)] u G,
    ugao = smer od kraja pina ka telu (0 desno, 90 gore, 180 levo, 270 dole), dužina 1 G."""
    name = lib_id.split(':')[1]
    x0, y0, x1, y1 = body
    gr = [S('symbol'), name + '_0_1',
          [S('rectangle'), [S('start'), mm(x0), mm(y0)], [S('end'), mm(x1), mm(y1)],
           [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]]
    pp = [S('symbol'), name + '_1_1']
    for num, nm, x, y, a in pins:
        typ = 'power_in' if nm in ('VIN', 'GND', 'PGND', 'AGND', 'PAD') else 'passive'
        pp.append([S('pin'), S(typ), S('line'), [S('at'), mm(x), mm(y), a], [S('length'), 2.54],
                   [S('name'), nm, [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]],
                   [S('number'), num, [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]]])

    def prop(k, v, y, hide=False):
        e = [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]
        if hide:
            e.append([S('hide'), S('yes')])
        return [S('property'), k, v, [S('at'), 0, y, 0], e]
    return [S('symbol'), lib_id, [S('pin_names'), [S('offset'), 1.016]], [S('exclude_from_sim'), S('no')],
            [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
            prop('Reference', ref, mm(y0) + 2), prop('Value', name, mm(y1) - 2),
            prop('Footprint', '', 0, True), prop('Datasheet', '', 0, True), gr, pp]


class Part:
    def __init__(self, sch, ref, lib_id, x, y, rot, mirror, unit, value, fp):
        self.sch, self.ref, self.lib_id, self.x, self.y, self.rot, self.mirror, self.unit = \
            sch, ref, lib_id, x, y, rot, mirror, unit
        self.value, self.fp = value, fp
        self.defn = sch.symdef(lib_id)
        self.pins = {n: v for (u, n), v in pins_of(self.defn).items() if u in (0, unit)}
        self.fields = []
        self.pmap = {}          # zamena pinova po položaju (okrenut nepolarni element)

    def p(self, num):
        """Apsolutna tačka pina u G (num = pin po položaju, vidi pmap)."""
        num = self.pmap.get(num, num)
        px, py, _ = self.pins[num]
        dx, dy = _tf(px / G, py / G, self.rot, self.mirror)
        return (round(self.x + dx, 3), round(self.y + dy, 3))

    def out(self, num):
        """Jedinični vektor od tela ka spolja (ekran)."""
        num = self.pmap.get(num, num)
        _, _, a = self.pins[num]
        r = math.radians(a + 180)
        dx, dy = _tf(math.cos(r), math.sin(r), self.rot, self.mirror)
        return (round(dx), round(dy))


class Sch:
    def __init__(self, title, paper='A1', project='apollo_module'):
        self.title, self.paper, self.project = title, paper, project
        self.root = uid()
        self.libs = {}
        self.parts = []
        self.items = []         # gotovi s-izrazi (žice, oznake, tekst...)
        self.wires = []         # (a, b) u G
        self.npwr = 0
        self.custom = {}

    # ------------------------------------------------------------------ simboli
    def symdef(self, lib_id):
        if lib_id not in self.libs:
            self.libs[lib_id] = self.custom[lib_id] if lib_id in self.custom else lib_symbol(lib_id)
        return self.libs[lib_id]

    def add(self, ref, lib_id, x, y, rot=0, mirror=None, unit=1, value='', fp='', fields='r', fofs=(0, 0)):
        p = Part(self, ref, lib_id, x, y, rot, mirror, unit, value, fp)
        p.fields = fields
        p.fofs = fofs
        self.parts.append(p)
        return p

    # ------------------------------------------------------------------ crtanje
    def w(self, *pts):
        pts = [(round(a, 3), round(b, 3)) for a, b in pts]
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            assert a[0] == b[0] or a[1] == b[1], ('kosa žica', a, b)
            self.wires.append((a, b))
        return pts[-1]

    def pwr(self, pt, name, smer=None):
        """Simbol napajanja u tački pt; smer = vektor ka spolja (crtež simbola ide u tom smeru)."""
        self.npwr += 1
        lib_id = 'power:GND' if name == 'GND' else 'power:+3V3' if name == '+3V3' else 'power:VCC'
        if name == 'GND':
            rot = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}[smer or (0, 1)]
        else:
            rot = {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}[smer or (0, -1)]
        p = self.add('#PWR%03d' % self.npwr, lib_id, pt[0], pt[1], rot, value=name)
        p.fields = 'pwr'
        return p

    def flag(self, pt, rot=0):
        self.npwr += 1
        p = self.add('#FLG%03d' % self.npwr, 'power:PWR_FLAG', pt[0], pt[1], rot, value='PWR_FLAG')
        p.fields = 'pwr'
        return p

    def pwr_pin(self, part, num, name, stub=0):
        a = part.p(num)
        d = part.out(num)
        b = (a[0] + d[0] * stub, a[1] + d[1] * stub)
        if stub:
            self.w(a, b)
        return self.pwr(b, name, d)

    def lab(self, pt, name, smer='r', glob=True):
        """Oznaka mreže. smer = na koju stranu ide telo oznake ('r','l','u','d')."""
        ang = {'r': 0, 'u': 90, 'l': 180, 'd': 270}[smer]
        just = {'r': 'left', 'u': 'left', 'l': 'right', 'd': 'right'}[smer]
        x, y = mm(pt[0]), mm(pt[1])
        eff = [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], [S('justify'), S(just)]]
        if glob:
            self.items.append([S('global_label'), name, [S('shape'), S('passive')], [S('at'), x, y, ang],
                               [S('fields_autoplaced'), S('yes')], eff, [S('uuid'), uid()],
                               [S('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [S('at'), x, y, 0],
                                [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], [S('hide'), S('yes')]]]])
        else:
            eff = [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], [S('justify'), S(just), S('bottom')]]
            self.items.append([S('label'), name, [S('at'), x, y, ang], [S('fields_autoplaced'), S('yes')], eff,
                               [S('uuid'), uid()]])
        self._labpts = getattr(self, '_labpts', []) + [((round(pt[0], 3), round(pt[1], 3)), name)]

    def lab_pin(self, part, num, name, stub=1, glob=True):
        a = part.p(num)
        d = part.out(num)
        b = (a[0] + d[0] * stub, a[1] + d[1] * stub)
        self.w(a, b)
        smer = {(1, 0): 'r', (-1, 0): 'l', (0, -1): 'u', (0, 1): 'd'}[d]
        self.lab(b, name, smer, glob)

    def nc(self, part, num):
        x, y = part.p(num)
        self.items.append([S('no_connect'), [S('at'), mm(x), mm(y)], [S('uuid'), uid()]])

    def text(self, pt, t, size=1.27, bold=False, color=None):
        f = [S('font'), [S('size'), size, size]]
        if bold:
            f.append([S('bold'), S('yes')])
        if color:
            f.append([S('color')] + list(color) + [1])
        self.items.append([S('text'), t, [S('exclude_from_sim'), S('no')], [S('at'), mm(pt[0]), mm(pt[1]), 0],
                           [S('effects'), f, [S('justify'), S('left'), S('top')]], [S('uuid'), uid()]])

    def okvir(self, x0, y0, x1, y1, naslov):
        self.items.append([S('rectangle'), [S('start'), mm(x0), mm(y0)], [S('end'), mm(x1), mm(y1)],
                           [S('stroke'), [S('width'), 0.3], [S('type'), S('dash')], [S('color'), 30, 80, 140, 1]],
                           [S('fill'), [S('type'), S('none')]], [S('uuid'), uid()]])
        self.text((x0 + 0.5, y0 + 0.5), naslov, size=2.0, bold=True, color=(30, 80, 140))

    # ------------------------------------------------------------------ izlaz
    def _junctions(self):
        """Tačke spoja: >= 3 kraja (žice/pinovi) ili kraj žice na sredini druge žice."""
        cnt = {}
        for a, b in self.wires:
            cnt[a] = cnt.get(a, 0) + 1
            cnt[b] = cnt.get(b, 0) + 1
        pinpts = {}
        for p in self.parts:
            for n in p.pins:
                pt = p.p(p.pmap.get(n, n))
                pinpts[pt] = pinpts.get(pt, 0) + 1
        out = set()
        for pt, c in cnt.items():
            k = c + pinpts.get(pt, 0)
            for a, b in self.wires:
                if _inside(pt, a, b):
                    k += 2
            if k >= 3:
                out.add(pt)
        # pin na sredini žice
        for pt in pinpts:
            for a, b in self.wires:
                if _inside(pt, a, b):
                    out.add(pt)
        return out

    def _wires_split(self):
        """KiCad spaja kraj žice sa sredinom druge samo uz junction; radi sigurnosti seku se žice u tim tačkama."""
        pts = set()
        for a, b in self.wires:
            pts.add(a); pts.add(b)
        for p in self.parts:
            for n in p.pins:
                pts.add(p.p(p.pmap.get(n, n)))
        for pt, _ in getattr(self, '_labpts', []):
            pts.add(pt)
        out = []
        for a, b in self.wires:
            cut = sorted([pt for pt in pts if _inside(pt, a, b)], key=lambda q: abs(q[0] - a[0]) + abs(q[1] - a[1]))
            seq = [a] + cut + [b]
            out += list(zip(seq, seq[1:]))
        return out

    def _field(self, k, v, x, y, just=None, hide=False, size=1.27, ang=0):
        e = [S('effects'), [S('font'), [S('size'), size, size]]]
        if just:
            e.append([S('justify'), S(just)])
        if hide:
            e.append([S('hide'), S('yes')])
        return [S('property'), k, v, [S('at'), mm(x), mm(y), ang], e]

    def _sym(self, p):
        fx, fy = p.fofs
        if p.fields == 'pwr':
            d = {0: (0, 1), 90: (1, 0), 180: (0, -1), 270: (-1, 0)}
            dy = {0: -1.6, 90: 0, 180: 1.6, 270: 0}[p.rot] if p.lib_id != 'power:GND' else 1.6
            dx = {90: -1.6, 270: 1.6}.get(p.rot, 0) if p.lib_id != 'power:GND' else 0
            props = [self._field('Reference', p.ref, p.x, p.y, hide=True),
                     self._field('Value', p.value, p.x + dx, p.y + dy,
                                 just={90: 'right', 270: 'left'}.get(p.rot) if p.lib_id != 'power:GND' else None,
                                 hide=p.lib_id == 'power:GND')]
        else:
            if p.fields == 'r':
                a = (p.x + 1.2 + fx, p.y - 0.5 + fy, 'left'); b = (p.x + 1.2 + fx, p.y + 0.5 + fy, 'left')
            elif p.fields == 'l':
                a = (p.x - 1.2 + fx, p.y - 0.5 + fy, 'right'); b = (p.x - 1.2 + fx, p.y + 0.5 + fy, 'right')
            elif p.fields == 't':
                a = (p.x + fx, p.y - 1.7 + fy, None); b = (p.x + fx, p.y - 1.05 + fy, None)
            elif p.fields == 'b':
                a = (p.x + fx, p.y + 1.1 + fy, None); b = (p.x + fx, p.y + 1.75 + fy, None)
            else:                      # (dx, dy) za IC: oznaka i vrednost jedna ispod druge
                a = (p.x + p.fields[0] + fx, p.y + p.fields[1] + fy, 'left')
                b = (p.x + p.fields[0] + fx, p.y + p.fields[1] + 0.65 + fy, 'left')
            # KiCad prikazuje polje pod uglom (ugao polja - rotacija simbola) i okreće ga da bude čitljivo;
            # za 180° to obrće poravnanje, pa ugao ostaje 0 a levo/desno se zamenjuju
            ang = 0 if p.rot == 180 else p.rot
            if (p.mirror == 'y') != (p.rot == 180):
                sw = {'left': 'right', 'right': 'left'}
                a = (a[0], a[1], sw.get(a[2], a[2])); b = (b[0], b[1], sw.get(b[2], b[2]))
            props = [self._field('Reference', p.ref, a[0], a[1], a[2], ang=ang),
                     self._field('Value', p.value, b[0], b[1], b[2], ang=ang),
                     self._field('Footprint', p.fp, p.x, p.y, hide=True),
                     self._field('Datasheet', '~', p.x, p.y, hide=True)]
        at = [S('at'), mm(p.x), mm(p.y), p.rot]
        s = [S('symbol'), [S('lib_id'), p.lib_id], at]
        if p.mirror:
            s.append([S('mirror'), S(p.mirror)])
        s += [[S('unit'), p.unit], [S('exclude_from_sim'), S('no')], [S('in_bom'), S('no' if p.ref.startswith('#') else 'yes')],
              [S('on_board'), S('no' if p.ref.startswith('#') else 'yes')], [S('dnp'), S('no')], [S('uuid'), uid()]]
        s += props
        for n in sorted(p.pins):
            s.append([S('pin'), n, [S('uuid'), uid()]])
        s.append([S('instances'), [S('project'), self.project,
                                   [S('path'), '/' + self.root, [S('reference'), p.ref], [S('unit'), p.unit]]]])
        return s

    def save_projekat(self, folder):
        """apollo.kicad_sym (sopstveni simboli), sym-lib-table i minimalni .kicad_pro - da KiCad nadje sve."""
        lib = [S('kicad_symbol_lib'), [S('version'), 20231120], [S('generator'), 'kicad_symbol_editor']]
        for lid, d in self.custom.items():
            lib.append([S('symbol'), lid.split(':')[1]] + d[2:])
        NL = chr(10)
        with open(os.path.join(folder, 'apollo.kicad_sym'), 'w', encoding='utf-8', newline=NL) as f:
            f.write(sexp.dump(lib) + NL)
        with open(os.path.join(folder, 'sym-lib-table'), 'w', encoding='utf-8', newline=NL) as f:
            f.write(NL.join(['(sym_lib_table', '  (version 7)',
                             '  (lib (name "apollo")(type "KiCad")(uri "${KIPRJMOD}/apollo.kicad_sym")'
                             '(options "")(descr "TPS55340, TPS560430"))', ')', '']))
        pro = os.path.join(folder, self.project + '.kicad_pro')
        if not os.path.exists(pro):
            with open(pro, 'w', encoding='utf-8', newline=NL) as f:
                f.write(NL.join(['{', '  "meta": {', '    "filename": "%s.kicad_pro",' % self.project,
                                 '    "version": 1', '  }', '}', '']))

    def save(self, fname):
        out = [S('kicad_sch'), [S('version'), 20231120], [S('generator'), 'eeschema'],
               [S('generator_version'), '8.0'], [S('uuid'), self.root], [S('paper'), self.paper],
               [S('title_block'), [S('title'), self.title], [S('date'), '2026-11-22'], [S('rev'), '0.1'],
                [S('comment'), 1, 'Samo laboratorija - nije protivpozarni uredjaj (EN 54)'],
                [S('comment'), 2, 'Generisano: hardware/schematic/kicad/apollo_sema.py iz netliste make_pcb.py']],
               [S('lib_symbols')] + list(self.libs.values())]
        for pt in sorted(self._junctions()):
            out.append([S('junction'), [S('at'), mm(pt[0]), mm(pt[1])], [S('diameter'), 0],
                        [S('color'), 0, 0, 0, 0], [S('uuid'), uid()]])
        for a, b in self._wires_split():
            out.append([S('wire'), [S('pts'), [S('xy'), mm(a[0]), mm(a[1])], [S('xy'), mm(b[0]), mm(b[1])]],
                        [S('stroke'), [S('width'), 0], [S('type'), S('default')]], [S('uuid'), uid()]])
        out += self.items
        for p in self.parts:
            out.append(self._sym(p))
        out.append([S('sheet_instances'), [S('path'), '/', [S('page'), '1']]])
        with open(fname, 'w', encoding='utf-8', newline='\n') as f:
            f.write(sexp.dump(out) + '\n')


def _inside(p, a, b, eps=1e-6):
    if a[0] == b[0] == p[0]:
        return min(a[1], b[1]) + eps < p[1] < max(a[1], b[1]) - eps
    if a[1] == b[1] == p[1]:
        return min(a[0], b[0]) + eps < p[0] < max(a[0], b[0]) - eps
    return False
