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
C0603, C0805, C1206 = 'C_0603_1608Metric', 'C_0805_2012Metric', 'C_1206_3216Metric'
R0603, R0805, R2512 = 'R_0603_1608Metric', 'R_0805_2012Metric', 'R_2512_6332Metric'
SOT23 = 'SOT-23'
LCSC = {
    # --- kondenzatori
    ('100n', C0603): ('C14663', 'Yageo CC0603KRX7R9BB104', ''),
    ('1u', C0603): ('C15849', 'Samsung CL10A105KB8NNNC', ''),
    ('1n', C0603): ('C1588', 'Samsung CL10B102KB8NNNC', ''),
    ('33p', C0603): ('C1663', 'Samsung CL10C330JB8NNNC', 'C0G; kristal C9002 CL=20 pF'),
    ('100n', C0805): ('C49678', 'Yageo CC0805KRX7R9BB104', ''),
    ('1u', C0805): ('C28323', 'Samsung CL21B105KBFNNNE', ''),
    ('10u', C0805): ('C15850', 'Samsung CL21A106KAYNNNE', ''),
    ('680n', C0805): ('C282780', 'CCTC TCC0805X7R684K500DT', ''),
    ('10n', C0805): ('C1710', 'Samsung CL21B103KBANNNC', ''),
    ('100p', C0805): ('C1790', 'Samsung CL21C101JBANNNC', 'C0G'),
    ('1n', C0805): ('C46653', 'Samsung CL21B102KBCNNNC', ''),
    ('1u/50V', C1206): ('C1848', 'Samsung CL31B105KBHNNNE', ''),
    ('4u7/50V', C1206): ('C29823', 'FH 1206B475K500NT', ''),
    ('10u', C1206): ('C13585', 'Samsung CL31A106KBHNNNE', ''),
    ('10u/50V', C1206): ('C13585', 'Samsung CL31A106KBHNNNE', 'X5R 50 V; X7R zamena C303950'),
    ('100u/50V', 'CP_Radial_D8.0mm_P3.50mm'): ('C88859', 'Rubycon 50YXJ100M', 'THT; proveri D8/P3,5'),
    ('470u/50V lowESR', 'CP_Radial_D10.0mm_P5.00mm'): ('C2902875', 'Rubycon 50ZLJ470M', 'THT low-ESR; proveri D10/P5'),
    # --- otpornici 1 %
    ('100k', R0805): ('C149504', 'UNI-ROYAL 0805W8F1003T5E', ''),
    ('10k', R0805): ('C17414', 'UNI-ROYAL 0805W8F1002T5E', ''),
    ('1k', R0805): ('C17513', 'UNI-ROYAL 0805W8F1001T5E', ''),
    ('2k', R0805): ('C17604', 'UNI-ROYAL 0805W8F2001T5E', ''),
    ('15k', R0805): ('C17475', 'UNI-ROYAL 0805W8F1502T5E', ''),
    ('100', R0805): ('C17408', 'UNI-ROYAL 0805W8F1000T5E', ''),
    ('3k0', R0805): ('C17661', 'UNI-ROYAL 0805W8F3001T5E', ''),
    ('40k2', R0805): ('C17678', 'UNI-ROYAL 0805W8F4022T5E', ''),
    ('3k24', R0805): ('C17609', 'UNI-ROYAL 0805W8F3241T5E', ''),
    ('53k6', R0805): ('C322510', 'FH RS-05K5362FT', ''),
    ('91k', R0805): ('C137484', 'Yageo RC0805FR-0791KL', 'ne C17855 (9k1)'),
    ('27', R0603): ('C25190', 'UNI-ROYAL 0603WAF270JT5E', ''),
    ('10k', R0603): ('C25804', 'UNI-ROYAL 0603WAF1002T5E', ''),
    ('1k', R0603): ('C21190', 'UNI-ROYAL 0603WAF1001T5E', ''),
    ('3k3', R0603): ('C22978', 'UNI-ROYAL 0603WAF3301T5E', ''),
    ('100k', R0603): ('C25803', 'UNI-ROYAL 0603WAF1003T5E', ''),
    ('1R 1W', R2512): ('C11254', 'UNI-ROYAL 25121WF100KT4E', '1 W, 1 %'),
    ('1R2 1W', R2512): ('C46193', 'UNI-ROYAL 25121WF120KT4E', '1 W, 1 %'),
    # --- poluprovodnici
    ('SS56', 'D_SMC'): ('C698825', 'Yangjie SS56', 'SMC'),
    ('SMBJ36A', 'D_SMB'): ('C353364', 'SMBJ36A', 'unidirekciona'),
    ('SS34', 'D_SMA'): ('C8678', 'MDD SS34', ''),
    ('LED', 'LED_0805_2012Metric'): ('C2297', 'KENTO KT-0805G', 'zelena'),
    ('BAT54J', 'D_SOD-323'): ('C130415', 'Nexperia BAT54J,115', ''),
    ('2N7002', SOT23): ('C8545', 'CJ 2N7002', ''),
    ('MMBT3904', SOT23): ('C20526', 'CJ MMBT3904', 'umesto BC847, isti raspored B-E-C'),
    ('TIP122 + hladnjak', 'TO-220-3_Vertical'): ('C84073', 'CJ TIP122', 'THT, polozen na hladnjak'),
    # --- IC
    ('LM2587S-ADJ', 'TO-263-5_TabPin3'): ('C1355343', 'TI LM2587S-ADJ/NOPB', 'malo na stanju'),
    ('W25Q16JVSS', 'SOIC-8_5.23x5.23mm_P1.27mm'): ('C131025', 'Winbond W25Q16JVSSIQ', ''),
    ('AP2112K-3.3', 'SOT-23-5'): ('C51118', 'Diodes AP2112K-3.3TRG1', ''),
    ('MCP6561', 'SOT-23-5'): ('C117501', 'Microchip MCP6561T-E/OT', 'samo OT varijanta'),
    ('R-78E5.0-0.5', 'Converter_DCDC_RECOM_R-78E-0.5_THT'): ('C5199916', 'RECOM R-78E5.0-0.5', 'THT'),
    ('REF3033', SOT23): ('C36658', 'TI REF3033AIDBZR', ''),
    ('OPA197', 'SOIC-8_3.9x4.9mm_P1.27mm'): ('C79274', 'TI OPA197IDR', ''),
    ('MCP6002', 'SOIC-8_3.9x4.9mm_P1.27mm'): ('C7377', 'Microchip MCP6002T-I/SN', ''),
    ('ADuM3160', 'SOIC-16W_7.5x10.3mm_P1.27mm'): ('C108501', 'ADI ADuM3160BRWZ', 'malo na stanju'),
    ('RP2040', 'QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm'): ('C2040', 'Raspberry Pi RP2040', ''),
    ('12MHz', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'): ('C9002', 'YXC X322512MSB4SI', 'CL 20 pF'),
    # --- ostalo
    ('3A', 'Fuse_1206_3216Metric'): ('C14165', 'Littelfuse 0466003.NRHF', '32 V, ulaz je 24 V'),
    ('PTC 750mA/60V', 'Fuse_2920_7451Metric'): ('C47513', 'Ruilon SMD2920P075TF/60', ''),
    ('100uH SRR1280-101M', 'L_Bourns_SRR1260'): ('C2041361', 'Bourns SRR1280-101M', 'isti otisak kao SRR1260; Isat 2,0 A'),
    ('BOOTSEL', 'SW_Push_1P1T_XKB_TS-1187A'): ('C318884', 'XKB TS-1187A-B-A-B', ''),
    ('RESET', 'SW_Push_1P1T_XKB_TS-1187A'): ('C318884', 'XKB TS-1187A-B-A-B', ''),
    ('USB-B', 'USB_B_OST_USB-B1HSxx_Horizontal'): ('C720549', 'XUNPU USB-B10-BRW', 'THT; proveri crtez otiska, original OST C3198024'),
    ('SWD', 'PinHeader_1x03_P2.54mm_Vertical'): ('C49257', 'BOOMELE 2.54-1*3P', 'THT'),
}
TB = 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'
for v in ('24V IN', 'LOOP OUT', 'LOOP IN'):
    LCSC[(v, TB)] = ('C5183929', 'Phoenix MKDS 1,5/2-5,08', 'THT; zamena Kefa KF128-5.08-2P C474952')
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
