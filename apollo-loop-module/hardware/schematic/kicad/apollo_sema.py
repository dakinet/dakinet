"""KiCad šema Apollo loop driver MODULA v0.1 (jedan list, A1) – generiše apollo_module.kicad_sch.

Pokretanje:  python apollo_sema.py
  1) iz rečnika P u ../../pcb/make_pcb.py (izvor istine) uzima oznake, vrednosti, footprint-ove i mreže;
  2) crta simbole iz KiCad 10 biblioteka (TPS55340 i TPS560430 nemaju simbol u KiCad-u – napravljeni ovde);
  3) kicad-cli izvozi netlistu iz šeme i skripta je poredi sa P (svaki pin, svaka mreža), pa pokreće ERC.
Samo laboratorija – nije protivpožarni uređaj (EN 54).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import sexp                       # noqa: E402
from alat import ucitaj_P         # noqa: E402
import raspored                   # noqa: E402

FPDIR = os.environ.get('KICAD_FOOTPRINTS', r'C:/Program Files/KiCad/10.0/share/kicad/footprints/')
P = ucitaj_P(FPDIR if os.path.isdir(FPDIR) else '')   # imena footprint-ova kao u KiCad 10
CLI = os.environ.get('KICAD_CLI', r'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe')
IME = 'apollo_module'

LIB = {
    'R': 'Device:R', 'C': 'Device:C', 'L': 'Device:L',
    'C1': 'Device:C_Polarized', 'C5': 'Device:C_Polarized',
    'F1': 'Device:Fuse', 'F2': 'Device:Polyfuse',
    'D1': 'Device:D_Schottky', 'D2': 'Device:D_Schottky', 'D4': 'Device:D_Schottky',
    'D3': 'Device:D_Zener', 'D6': 'Device:D_Zener', 'D5': 'Device:LED',
    'Q1': 'Transistor_BJT:Q_NPN_Darlington_BCE', 'Q4': 'Transistor_BJT:MMBT3904', 'Q5': 'Transistor_BJT:Q_PNP_BEC',
    'Q2': 'Transistor_FET:2N7002', 'Q3': 'Transistor_FET:2N7002', 'Q6': 'Transistor_FET:2N7002',
    'Q7': 'Transistor_FET:2N7002',
    'U1': 'apollo:TPS55340PWP', 'U2': 'apollo:TPS560430X3FDBV', 'U3': 'Amplifier_Operational:OPA197xD',
    'U4': 'Amplifier_Operational:MCP6002-xSN', 'U6': 'Comparator:MCP6561-OT',
    'U7': 'apollo:AVR64DD28-xSO', 'Y1': 'Device:Crystal_GND24',
    'J1': 'Connector_Generic:Conn_02x14_Odd_Even',
}


def lid(ref):
    return LIB.get(ref) or LIB[ref.rstrip('0123456789')]


NEPOLARNI = {r for r in P if r[0] in 'RLF' or (r[0] == 'C' and r not in ('C1', 'C5'))}


def napravi(okreni=frozenset()):
    return raspored.napravi(P, lid, okreni)


# -------------------------------------------------------------------- provera
def netlista_iz_seme(sch_path):
    net_path = os.path.splitext(sch_path)[0] + '.net'
    r = subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', net_path, sch_path],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('kicad-cli netlist: ' + r.stdout + r.stderr)
    tree = sexp.parse(open(net_path, encoding='utf-8').read())
    nets = []
    for n in sexp.find(sexp.first(tree, 'nets'), 'net'):
        name = sexp.first(n, 'name')[1]
        nodes = {(sexp.first(x, 'ref')[1], sexp.first(x, 'pin')[1]) for x in sexp.find(n, 'node')}
        nets.append((name, nodes))
    return nets


def _zameni(nets, zam):
    f = lambda k: (k[0], {'1': '2', '2': '1'}[k[1]]) if k[0] in zam and k[1] in '12' else k
    return [(n, {f(k) for k in nodes}) for n, nodes in nets]


def nadji_zamene(nets):
    """Nepolarni element se okreće ako su ostali pinovi u mreži njegovog pina 1 iz mreže koju P daje pinu 2."""
    ocek = {(r, p): n for r, (_, _, ps) in P.items() for p, n in ps.items()}
    grupa = {k: nodes for _, nodes in nets for k in nodes}
    zam = set()
    for r in NEPOLARNI:
        n1, n2 = P[r][2]['1'], P[r][2]['2']
        drugi = [ocek.get(k) for k in grupa.get((r, '1'), ()) if k[0] != r and k[0] not in NEPOLARNI]
        if not drugi:      # samo nepolarni susedi: gledaj njihove pinove posle zamene nije potrebno – glasaj svima
            drugi = [ocek.get(k) for k in grupa.get((r, '1'), ()) if k[0] != r]
        if drugi.count(n2) > drugi.count(n1):
            zam.add(r)
    return zam


def uporedi(nets):
    greske = []
    ocek = {}
    for ref, (_, _, pins) in P.items():
        for pin, net in pins.items():
            ocek.setdefault(net, set()).add((ref, pin))
    po_pinu = {}
    for name, nodes in nets:
        for k in nodes:
            po_pinu[k] = (name, nodes)
    for net, pins in ocek.items():
        grupe = {po_pinu[k][0] for k in pins if k in po_pinu}
        nema = [k for k in pins if k not in po_pinu]
        if nema:
            greske.append('%s: pinovi nisu u šemi %s' % (net, sorted(nema)))
        if len(grupe) > 1:
            greske.append('PREKID %s: %s' % (net, sorted(grupe)))
        for g in grupe:
            visak = {k for k in dict(nets)[g] if k not in pins}
            if visak:
                greske.append('KRATAK SPOJ %s sa %s' % (net, sorted(visak)))
    sve = {k for v in ocek.values() for k in v}
    for name, nodes in nets:
        if len(nodes) > 1 and not nodes & sve:
            greske.append('mreža %s nije u netlisti: %s' % (name, sorted(nodes)))
        for k in nodes:
            if k not in sve and len(nodes) > 1:
                greske.append('pin %s.%s povezan (%s), a nije u netlisti' % (k[0], k[1], name))
    return greske


if __name__ == '__main__':
    path = os.path.join(HERE, IME + '.kicad_sch')
    napravi().save(path)
    zam = nadji_zamene(netlista_iz_seme(path))
    if zam:
        print('okrećem za 180° (pin 1/2 kao na pločici):', ' '.join(sorted(zam)))
        napravi(frozenset(zam)).save(path)
    napravi(frozenset(zam)).save_projekat(HERE)
    nets = netlista_iz_seme(path)
    g = uporedi(nets)
    for e in g:
        print('GRESKA:', e)
    print('netlista: %d mreža, %d grešaka u odnosu na make_pcb.py' % (len([n for n in nets if len(n[1]) > 1]), len(g)))
    sys.exit(1 if g else 0)
