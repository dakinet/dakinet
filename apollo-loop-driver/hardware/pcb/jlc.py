#!/usr/bin/env python3.12
"""Izlazni fajlovi za JLCPCB: Gerber + drill (zip), BOM_JLC.csv, CPL_JLC.csv i obican bom.csv.

Pokreni posle build.sh:  python3.12 jlc.py
LCSC brojevi su u tabeli LCSC ispod (kljuc: vrednost, otisak). Deo bez LCSC broja
ide u BOM_JLC.csv bez broja i JLC ga ne montira (oznacen je u RUCNO).
"""
import csv, os, re, subprocess, sys, zipfile
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import pcbnew

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PCB = 'apollo_loop_driver.kicad_pcb'

# (vrednost, otisak) -> (LCSC, proizvodjac i oznaka, napomena)
LCSC = {
}
# delovi koje JLC ne montira (nema ih ili se montiraju rucno)
RUCNO = {'HS1': 'Aavid/Boyd TV5G nije u LCSC katalogu - montirati rucno (M3 zavrtanj kroz TIP122 i hladnjak)'}


def footprints(board):
    out = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        name = str(fp.GetFPID().GetLibItemName())
        if name.startswith('MountingHole'):
            continue
        p = fp.GetPosition()
        out.append(dict(ref=ref, val=fp.GetValue(), fp=name,
                        x=pcbnew.ToMM(p.x), y=-pcbnew.ToMM(p.y),
                        rot=fp.GetOrientationDegrees() % 360,
                        side='Bottom' if fp.IsFlipped() else 'Top',
                        tht=any(pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for pad in fp.Pads())))
    return out


def natkey(r):
    m = re.match(r'([A-Z]+)(\d+)', r)
    return (m.group(1), int(m.group(2))) if m else (r, 0)


def main():
    b = pcbnew.LoadBoard(PCB)
    fps = footprints(b)

    # --- Gerber + drill
    os.makedirs('gerber', exist_ok=True)
    for f in os.listdir('gerber'):
        os.remove(os.path.join('gerber', f))
    layers = 'F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'
    subprocess.run(['kicad-cli', 'pcb', 'export', 'gerbers', '-o', 'gerber/', '-l', layers,
                    '--subtract-soldermask', PCB], check=True, capture_output=True)
    subprocess.run(['kicad-cli', 'pcb', 'export', 'drill', '-o', 'gerber/', '--excellon-separate-th',
                    '--format', 'excellon', '-u', 'mm', PCB], check=True, capture_output=True)
    with zipfile.ZipFile('apollo_loop_driver_gerber.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir('gerber')):
            z.write(os.path.join('gerber', f), f)

    # --- grupisanje po (vrednost, otisak)
    grupe = {}
    for f in fps:
        grupe.setdefault((f['val'], f['fp']), []).append(f['ref'])
    nedostaje = []
    with open('BOM_JLC.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Manufacturer Part', 'Note'])
        for (val, fp), refs in sorted(grupe.items(), key=lambda kv: natkey(sorted(kv[1], key=natkey)[0])):
            refs = sorted(refs, key=natkey)
            if all(r in RUCNO for r in refs):
                w.writerow([val, ','.join(refs), fp, '', '', RUCNO[refs[0]]])
                continue
            lc, mpn, note = LCSC.get((val, fp), ('', '', ''))
            if not lc:
                nedostaje.append((val, fp, refs))
            w.writerow([val, ','.join(refs), fp, lc, mpn, note])
    with open('bom.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Kolicina', 'Oznake', 'Vrednost', 'Kuciste', 'LCSC'])
        for (val, fp), refs in sorted(grupe.items(), key=lambda kv: natkey(sorted(kv[1], key=natkey)[0])):
            refs = sorted(refs, key=natkey)
            w.writerow([len(refs), ' '.join(refs), val, fp, LCSC.get((val, fp), ('',))[0]])

    # --- CPL (pozicije). Rotacija je KiCad-ova; JLC je prikazuje u pregledu pre potvrde.
    with open('CPL_JLC.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for f in sorted(fps, key=lambda f: natkey(f['ref'])):
            if f['ref'] in RUCNO:
                continue
            w.writerow([f['ref'], f"{f['x']:.3f}mm", f"{f['y']:.3f}mm", f['side'], f"{f['rot']:.1f}"])

    print(f'{len(fps)} delova, {len(grupe)} stavki u BOM-u')
    for val, fp, refs in nedostaje:
        print('BEZ LCSC:', val, fp, ' '.join(refs))


if __name__ == '__main__':
    main()
