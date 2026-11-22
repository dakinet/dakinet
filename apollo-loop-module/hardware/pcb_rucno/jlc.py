"""Izlazni fajlovi za JLCPCB: Gerber + drill (zip), BOM_JLC.csv, CPL_JLC.csv, bom.csv.

Pokreni (KiCad 10, Windows):  "C:/Program Files/KiCad/10.0/bin/python.exe" jlc.py
Kolona „Provera“: S = broj viđen na LCSC/JLC stranici u rezultatima web pretrage (22.11.2026, stranice nisu otvarane
direktno), M = isti deo (vrednost + kućište) već je u BOM-u apollo-loop-driver, ? = NIJE potvrđeno (broj iz sećanja ili
zamena) – obavezno proveriti u JLC katalogu pre narudžbine. Napomena: B = JLC Basic, E = Extended (+3 USD po vrsti).
"""
import csv
import os
import re
import subprocess
import zipfile

import pcbnew

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PCB = 'apollo_module.kicad_pcb'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
R0603, R0805, R2512 = 'R_0603_1608Metric', 'R_0805_2012Metric', 'R_2512_6332Metric'
C0402, C0603, C0805, C1210 = 'C_0402_1005Metric', 'C_0603_1608Metric', 'C_0805_2012Metric', 'C_1210_3225Metric'
SOT23, SOIC8 = 'SOT-23', 'SOIC-8_3.9x4.9mm_P1.27mm'

# (vrednost, otisak) -> (LCSC, proizvođač i oznaka, provera, napomena)
LCSC = {
    # --- IC
    ('TPS55340PWPR', 'Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3.155x3.255mm'):
        ('C43862', 'TI TPS55340PWPR', 'S', 'E; boost'),
    ('TPS560430X3FDBVR', 'SOT-23-6'): ('C2071721', 'TI TPS560430X3FDBVR', 'S', 'E; buck 3,3 V; malo na stanju (~300-400)'),
    ('RP2040', 'QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm'): ('C2040', 'Raspberry Pi RP2040', 'M', 'E'),
    ('W25Q16JVSS', 'SOIC-8_5.3x5.3mm_P1.27mm'): ('C131025', 'Winbond W25Q16JVSSIQ', 'M', 'E; SOIC-8 208 mil'),
    ('OPA197', SOIC8): ('C79274', 'TI OPA197IDR', 'M', 'E'),
    ('MCP6002', SOIC8): ('C7377', 'Microchip MCP6002T-I/SN', 'M', 'E'),
    ('MCP6561T-E/OT', 'SOT-23-5'): ('C117501', 'Microchip MCP6561T-E/OT', 'M', 'E'),
    ('12MHz ABM8-272-T3', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'): ('C20625731', 'Abracon ABM8-272-T3', 'S', 'E; CL 10 pF (uz 15 pF kond.)'),
    # --- poluprovodnici
    ('MJD122', 'TO-252-2'): ('C59488', 'CJ MJD122', 'S', 'E; DPAK, 100 V 8 A'),
    ('2N7002', SOT23): ('C8545', 'CJ 2N7002', 'M', 'B'),
    ('MMBT3904', SOT23): ('C20526', 'CJ MMBT3904', 'M', 'B'),
    ('MMBT5401', SOT23): ('C8326', 'CJ MMBT5401', 'S', 'E; nema Basic 5401'),
    ('BAT54J', 'D_SOD-323'): ('C130415', 'Nexperia BAT54J,115', 'M', 'E'),
    ('SS34', 'D_SMA'): ('C8678', 'MDD SS34', 'M', 'B'),
    ('SS210', 'D_SMA'): ('C14996', 'MDD SS210', 'S', 'B; 100 V 2 A'),
    ('SMBJ36A', 'D_SMB'): ('C353364', 'SMBJ36A', 'M', 'E'),
    ('LED', 'LED_0603_1608Metric'): ('C2286', 'KENTO KT-0603R', 'S', 'B; crvena'),
    # --- induktivnosti
    ('33uH SRN6045TA-330M', 'L_Bourns_SRN6045TA'):
        ('C780211', 'Bourns SRN6045-330M', '?', 'E; LCSC ima SRN6045 bez TA (1,4 A) – otisak 6x6, proveri struju boost-a'),
    ('15uH SRN4018-150M', 'L_Bourns-SRN4018'):
        ('C326304', '3L COILS SNR4018K-150M', '?', 'E; ZAMENA (Bourns nije na LCSC), 0,92 A; proveri otisak 4x4'),
    # --- osigurači
    ('3A', 'Fuse_1206_3216Metric'): ('C14165', 'Littelfuse 0466003.NRHF', 'M', 'E; 32 V'),
    ('PTC 750mA/60V', 'Fuse_2920_7451Metric'): ('C47513', 'Ruilon SMD2920P075TF/60', 'M', 'E'),
    # --- elektroliti
    ('100u/50V', 'CP_Elec_8x10'): ('C569485', 'SUNCON 50CE100LX', 'S', 'E; D8xL10,2'),
    ('47u/50V', 'CP_Elec_6.3x7.7'): ('C83788', 'CapXon DV470M050E077ETR', 'S', 'E'),
    # --- keramički kondenzatori
    ('10u/50V', C1210): ('C138687', 'Samsung CL32B106KBJNNNE', 'S', 'E; X7R 50 V'),
    ('22u/10V', C0805): ('C45783', 'Samsung CL21A226MAQNNNE', 'S', 'B; 25 V (bolje od 10 V)'),
    ('10u', C0805): ('C15850', 'Samsung CL21A106KAYNNNE', 'M', 'B; 25 V'),
    ('100n', C0603): ('C14663', 'Yageo CC0603KRX7R9BB104', 'M', 'B; 50 V'),
    ('100n/50V', C0603): ('C14663', 'Yageo CC0603KRX7R9BB104', 'M', 'B; 50 V X7R'),
    ('1u', C0603): ('C15849', 'Samsung CL10A105KB8NNNC', 'M', 'B; 50 V'),
    ('1u/50V', C0603): ('C15849', 'Samsung CL10A105KB8NNNC', 'M', 'B; 50 V X5R'),
    ('1n', C0603): ('C1588', 'Samsung CL10B102KB8NNNC', 'M', 'B'),
    ('100p', C0603): ('C14858', 'Samsung CL10C101JB8NNNC', 'S', 'B; C0G'),
    ('10n', C0603): ('C57112', 'FH 0603B103K500NT', 'S', 'B'),
    ('15p', C0603): ('C1644', 'Samsung CL10C150JB8NNNC', '?', 'B; C0G, kristal'),
    ('47n', C0603): ('C1622', 'Samsung CL10B473KB8NNNC', 'S', 'B'),
    ('100n', C0402): ('C1525', 'Samsung CL05B104KO5NNNC', 'S', 'B'),
    ('1u', C0402): ('C52923', 'Samsung CL05A105KA5NQNC', 'S', 'B; 25 V'),
    # --- otpornici 0603 (UNI-ROYAL 0603WAF…, Basic)
    ('10k', R0603): ('C25804', 'UNI-ROYAL 0603WAF1002T5E', 'M', 'B'),
    ('1k', R0603): ('C21190', 'UNI-ROYAL 0603WAF1001T5E', 'M', 'B'),
    ('100k', R0603): ('C25803', 'UNI-ROYAL 0603WAF1003T5E', 'M', 'B'),
    ('27', R0603): ('C25190', 'UNI-ROYAL 0603WAF270JT5E', 'M', 'B'),
    ('10', R0603): ('C22859', 'UNI-ROYAL 0603WAF100JT5E', 'S', 'B'),
    ('100', R0603): ('C22775', 'UNI-ROYAL 0603WAF1000T5E', 'S', 'B'),
    ('470', R0603): ('C23179', 'UNI-ROYAL 0603WAF4700T5E', 'S', 'B'),
    ('2k2', R0603): ('C4190', 'UNI-ROYAL 0603WAF2201T5E', 'S', 'B'),
    ('3k24', R0603): ('C22994', 'UNI-ROYAL 0603WAF3241T5E', 'S', 'B?; FB boost-a'),
    ('13k', R0603): ('C22797', 'UNI-ROYAL 0603WAF1302T5E', 'S', 'B'),
    ('15k', R0603): ('C22809', 'UNI-ROYAL 0603WAF1502T5E', 'S', 'B'),
    ('40k2', R0603): ('C12447', 'UNI-ROYAL 0603WAF4022T5E', 'S', 'E; podešava napon'),
    ('82k', R0603): ('C310289', 'FH RS-03K8202FT', 'S', 'E; UNI-ROYAL 82k nije nađen'),
    ('270k', R0603): ('C22965', 'UNI-ROYAL 0603WAF2703T5E', 'S', 'B'),
    ('91k', R0805): ('C137484', 'Yageo RC0805FR-0791KL', 'M', 'E; ne C17855 (9k1)'),
    ('1R 1W', R2512): ('C11254', 'UNI-ROYAL 25121WF100KT4E', 'M', 'E; 1 W 1 %'),
    ('2R0 1W', R2512): ('C49298', 'UNI-ROYAL 25121WF200KT4E', 'S', 'E; 1 W 1 % (NE 25121WF200LT4E = 0,2 oma)'),
}
# ne montira JLC SMT (THT, telo letvice je na donjoj strani)
RUCNO = {'J1': 'Letvica 2x14 / 2,54 mm THT, donja strana – lemi se ručno ili JLC THT opcija'}


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
    subprocess.run([CLI, 'pcb', 'export', 'gerbers', '-o', 'gerber/', '-l', layers,
                    '--subtract-soldermask', PCB], check=True, capture_output=True)
    subprocess.run([CLI, 'pcb', 'export', 'drill', '-o', 'gerber/', '--excellon-separate-th',
                    '--format', 'excellon', '-u', 'mm', PCB], check=True, capture_output=True)
    with zipfile.ZipFile('apollo_module_gerber.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir('gerber')):
            z.write(os.path.join('gerber', f), f)

    grupe = {}
    for f in fps:
        grupe.setdefault((f['val'], f['fp']), []).append(f['ref'])
    red = sorted(grupe.items(), key=lambda kv: natkey(sorted(kv[1], key=natkey)[0]))
    nepotvrdjeno = []
    with open('BOM_JLC.csv', 'w', newline='', encoding='utf-8') as fh, \
            open('bom.csv', 'w', newline='', encoding='utf-8') as fb:
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
    with open('CPL_JLC.csv', 'w', newline='', encoding='utf-8') as fh:
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
