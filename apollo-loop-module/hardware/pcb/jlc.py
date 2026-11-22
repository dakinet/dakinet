#!/usr/bin/env python3.12
"""Izlazni fajlovi za JLCPCB: Gerber + drill (zip), BOM_JLC.csv, CPL_JLC.csv, bom.csv.

Pokreni posle build.sh:  python3.12 jlc.py
Kolona „Provera“: S = broj viđen na LCSC/JLC stranici u rezultatima web pretrage (jlcpcb.com/lcsc.com nisu
dostupni iz kontejnera, pa ništa nije otvoreno direktno), M = isti deo već je u BOM-u apollo-loop-driver,
? = NIJE potvrđeno. Napomena počinje sa B (JLC Basic, prema listi basic delova sa GitHub-a cpldcpu/TouchSynth) ili E (Extended) – pre narudžbine proveri u JLC katalogu (navedena je preporučena oznaka proizvođača).
"""
import csv, os, re, subprocess, sys, zipfile
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import pcbnew

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PCB = 'apollo_module.kicad_pcb'
R0402, R0603 = 'R_0402_1005Metric', 'R_0603_1608Metric'
C0402, C0805 = 'C_0402_1005Metric', 'C_0805_2012Metric'
TB = 'TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal'

# (vrednost, otisak) -> (LCSC, proizvođač i oznaka, provera, napomena)
LCSC = {
    # Basic (B) = bez naknade za učitavanje; Extended (E) = 3 USD po vrsti dela
    ('ATtiny1616-MNR', 'VQFN-20-1EP_3x3mm_P0.4mm_EP1.7x1.7mm'): ('C507118', 'Microchip ATTINY1616-MNR', 'S', 'E; nema Basic zamene'),
    ('HT7533-1', 'SOT-89-3'): ('C14289', 'Holtek HT7533-1', 'S', 'B; 1 GND, 2 VIN, 3 VOUT - PROVERI datasheet (klonovi imaju drugi raspored)'),
    ('BAV99', 'SOT-23'): ('C2500', 'Nexperia BAV99,215', 'S', 'B'),
    ('MMBT5551', 'SOT-23'): ('C2145', 'JSCJ MMBT5551', 'S', 'B; 160 V'),
    ('MMBT3904', 'SOT-23'): ('C20526', 'CJ MMBT3904', 'M', 'B'),
    ('SMAJ40A', 'D_SMA'): ('C3719895', 'Taiwan Semi SMAJ40A', 'S', 'E; nema Basic TVS 40 V'),
    ('BZT52C10', 'D_SOD-123'): ('C2103', 'JSCJ BZT52C10', 'S', 'E; nema Basic zener'),
    ('LED', 'LED_0603_1608Metric'): ('C2286', 'Hubei KENTO KT-0603R', 'S', 'B; crvena'),
    ('TASTER', 'SW_Push_1P1T_XKB_TS-1187A'): ('C318884', 'XKB TS-1187A-B-A-B', 'M', 'B'),
    ('10u/25V', C0805): ('C15850', 'Samsung CL21A106KAYNNNE', 'M', 'B; X5R 25 V'),
    ('100n', C0402): ('C1525', 'Samsung CL05B104KO5NNNC', 'S', 'B'),
    ('10n', C0402): ('C15195', 'Samsung CL05B103KB5NNNC', 'S', 'B'),
    ('1n', C0402): ('C1523', 'FH 0402B102K500NT', 'S', 'B'),
    ('1k', R0402): ('C11702', 'UNI-ROYAL 0402WGF1001TCE', 'S', 'B'),
    ('2k2', R0402): ('C25879', 'UNI-ROYAL 0402WGF2201TCE', 'S', 'B'),
    ('3k3', R0402): ('C25890', 'UNI-ROYAL 0402WGF3301TCE', 'S', 'B; odredjuje I_CC'),
    ('100k', R0402): ('C25741', 'UNI-ROYAL 0402WGF1003TCE', 'S', 'B'),
    ('330k', R0603): ('C23137', 'UNI-ROYAL 0603WAF3303T5E', 'S', 'B'),
    ('270', R0603): ('C22966', 'UNI-ROYAL 0603WAF2700T5E', 'S', 'B; odredjuje ~9,4 mA odgovora'),
    ('1M', R0603): ('C22935', 'UNI-ROYAL 0603WAF1004T5E', 'S', 'B'),
    ('4M7', R0603): ('C23163', 'UNI-ROYAL 0603WAF4704T5E', '?', 'E; nema Basic >1 MOhm (1M bi trosio +25 µA)'),
}
for v in ('LINIJA ULAZ', 'LINIJA IZLAZ', 'ULAZ'):
    LCSC[(v, TB)] = ('C474892', 'Kefa KF350-3.5-2P', 'S', 'E; THT 3,5 mm; uporedi crtež sa Phoenix PT 1,5/2-3,5-H')
# ne montira JLC
RUCNO = {'J4': 'UPDI: rupe 1,27 mm, ne montira se (pogo ili zalemljene žice)'}


def footprints(board):
    out = []
    for fp in board.GetFootprints():
        p = fp.GetPosition()
        out.append(dict(ref=fp.GetReference(), val=fp.GetValue(), fp=str(fp.GetFPID().GetLibItemName()),
                        x=pcbnew.ToMM(p.x), y=-pcbnew.ToMM(p.y), rot=fp.GetOrientationDegrees() % 360,
                        side='Bottom' if fp.IsFlipped() else 'Top'))
    return out


def natkey(r):
    m = re.match(r'([A-Z]+)(\d+)', r)
    return (m.group(1), int(m.group(2))) if m else (r, 0)


def main():
    b = pcbnew.LoadBoard(PCB)
    fps = footprints(b)
    os.makedirs('gerber', exist_ok=True)
    for f in os.listdir('gerber'):
        os.remove(os.path.join('gerber', f))
    layers = 'F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'
    subprocess.run(['kicad-cli', 'pcb', 'export', 'gerbers', '-o', 'gerber/', '-l', layers,
                    '--subtract-soldermask', PCB], check=True, capture_output=True)
    subprocess.run(['kicad-cli', 'pcb', 'export', 'drill', '-o', 'gerber/', '--excellon-separate-th',
                    '--format', 'excellon', '-u', 'mm', PCB], check=True, capture_output=True)
    with zipfile.ZipFile('apollo_module_gerber.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir('gerber')):
            z.write(os.path.join('gerber', f), f)

    grupe = {}
    for f in fps:
        grupe.setdefault((f['val'], f['fp']), []).append(f['ref'])
    red = sorted(grupe.items(), key=lambda kv: natkey(sorted(kv[1], key=natkey)[0]))
    nepotvrdjeno = []
    with open('BOM_JLC.csv', 'w', newline='') as fh, open('bom.csv', 'w', newline='') as fb:
        w, wb = csv.writer(fh), csv.writer(fb)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Manufacturer Part', 'Provera', 'Note'])
        wb.writerow(['Kolicina', 'Oznake', 'Vrednost', 'Kuciste', 'LCSC', 'Provera'])
        for (val, fp), refs in red:
            refs = sorted(refs, key=natkey)
            if all(r in RUCNO for r in refs):
                w.writerow([val, ','.join(refs), fp, '', '', '', RUCNO[refs[0]]])
                continue
            lc, mpn, pr, note = LCSC.get((val, fp), ('', '', '?', 'NEMA U TABELI'))
            if pr == '?':
                nepotvrdjeno.append((val, fp, refs, mpn))
            w.writerow([val, ','.join(refs), fp, lc, mpn, pr, note])
            wb.writerow([len(refs), ' '.join(refs), val, fp, lc, pr])
    with open('CPL_JLC.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for f in sorted(fps, key=lambda f: natkey(f['ref'])):
            if f['ref'] in RUCNO:
                continue
            w.writerow([f['ref'], f"{f['x']:.3f}mm", f"{f['y']:.3f}mm", f['side'], f"{f['rot']:.1f}"])
    print(f'{len(fps)} delova, {len(grupe)} stavki u BOM-u')
    for val, fp, refs, mpn in nepotvrdjeno:
        print('NEPOTVRDJEN LCSC:', val, fp, ' '.join(refs), '->', mpn)


if __name__ == '__main__':
    main()
