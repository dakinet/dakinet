"""Pravi KiCad 7 pločicu za Apollo XP95 laboratorijski drajver.

Pokretanje:  python3.12 make_pcb.py   (treba KiCad 7 i njegov pcbnew modul)
Izlaz:       apollo_loop_driver.kicad_pcb (raspored + mreže, bez vodova)
             apollo_loop_driver.dsn       (za Freerouting)
"""
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew

FP = '/usr/share/kicad/footprints/'
MM = pcbnew.FromMM

R0805 = ('Resistor_SMD', 'R_0805_2012Metric')
C0805 = ('Capacitor_SMD', 'C_0805_2012Metric')
C1206 = ('Capacitor_SMD', 'C_1206_3216Metric')
R2512 = ('Resistor_SMD', 'R_2512_6332Metric')
SOT23 = ('Package_TO_SOT_SMD', 'SOT-23')
SOIC8 = ('Package_SO', 'SOIC-8_3.9x4.9mm_P1.27mm')
TB2 = ('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal')
CP8 = ('Capacitor_THT', 'CP_Radial_D8.0mm_P3.50mm')

# ref: (biblioteka, x_mm, y_mm, rot, vrednost, {pin: mreža})
# Ploča: 120 x 85 mm, gornji levi ugao u (100, 100).
P = {
    # ---- napajanje 24 V
    'J1':  (TB2, 106, 112, 270, '24V IN', {'1': '+24V_IN', '2': 'GND'}),
    'F1':  (('Fuse', 'Fuse_1206_3216Metric'), 116, 106, 0, '3A', {'1': '+24V_IN', '2': 'VIN_F'}),
    'D3':  (('Diode_SMD', 'D_SMA'), 124, 106, 180, 'SS34', {'2': 'VIN_F', '1': '+24V'}),
    'C1':  (CP8, 132, 112, 0, '100u/50V', {'1': '+24V', '2': 'GND'}),
    'U2':  (('Converter_DCDC', 'Converter_DCDC_RECOM_R-78E-0.5_THT'), 116, 124, 0, 'R-78E5.0-0.5',
            {'1': '+24V', '2': 'GND', '3': '+5V'}),
    'C16': (C1206, 116, 131, 0, '4u7/50V', {'1': '+24V', '2': 'GND'}),
    'C10': (C1206, 124, 131, 0, '10u', {'1': '+5V', '2': 'GND'}),
    'J4':  (('Connector_PinHeader_2.54mm', 'PinHeader_1x04_P2.54mm_Vertical'), 106, 140, 0, 'BOOST 24->34V',
            {'1': '+24V', '2': 'GND', '3': '+34V', '4': 'GND'}),
    'C3':  (CP8, 116, 148, 0, '100u/63V', {'1': '+34V', '2': 'GND'}),
    'C5':  (C1206, 116, 140, 0, '1u/50V', {'1': '+34V', '2': 'GND'}),
    # ---- referenca i VSET
    'U3':  (SOT23, 130, 124, 0, 'REF3033', {'1': '+5V', '2': 'REF', '3': 'GND'}),
    'C17': (C0805, 130, 119, 0, '100n', {'1': '+5V', '2': 'GND'}),
    'R3':  (R0805, 136, 124, 0, '1k', {'1': 'REF', '2': 'VSET'}),
    'R4':  (R0805, 141, 128, 90, '15k', {'1': 'VSET', '2': 'GND'}),
    'C6':  (C0805, 144, 128, 90, '10n', {'1': 'VSET', '2': 'GND'}),
    'R5':  (R0805, 147, 128, 90, '3k24', {'1': 'VSET', '2': 'Q2D'}),
    'Q2':  (SOT23, 147, 134, 0, '2N7002', {'1': 'NIVO_G', '2': 'GND', '3': 'Q2D'}),
    'R19': (R0805, 141, 135, 0, '100', {'1': 'NIVO', '2': 'NIVO_G'}),
    'Q5':  (SOT23, 151, 128, 0, '2N7002', {'1': 'EN_N', '2': 'GND', '3': 'VSET'}),
    'R18': (R0805, 151, 134, 90, '100k', {'1': 'EN_N', '2': '+3V3'}),
    # ---- drajver petlje
    'U4':  (SOIC8, 160, 130, 0, 'OPA197', {'2': 'FB', '3': 'VSET', '4': 'GND', '6': 'U4OUT', '7': '+34V'}),
    'C13': (C0805, 160, 123, 0, '100n', {'1': '+34V', '2': 'GND'}),
    'R6':  (R0805, 167, 128, 0, '1k', {'1': 'U4OUT', '2': 'NB'}),
    'R8':  (R0805, 160, 137, 0, '91k', {'1': 'LOOP_DRV', '2': 'FB'}),
    'C7':  (C0805, 160, 140, 0, '100p', {'1': 'LOOP_DRV', '2': 'FB'}),
    'R9':  (R0805, 155, 137, 90, '10k', {'1': 'FB', '2': 'GND'}),
    'Q3':  (('Package_TO_SOT_THT', 'TO-220-3_Vertical'), 176, 106, 0, 'TIP122 + hladnjak',
            {'1': 'NB', '2': '+34V', '3': 'NE'}),
    'Q4':  (SOT23, 174, 117, 0, 'BC847', {'1': 'NE', '2': 'LOOP_DRV', '3': 'NB'}),
    'R7':  (R2512, 182, 121, 90, '1R2 1W', {'1': 'NE', '2': 'LOOP_DRV'}),
    # ---- zaštita izlaza
    'F2':  (('Fuse', 'Fuse_2920_7451Metric'), 194, 117, 0, 'PTC 750mA/60V', {'1': 'LOOP_DRV', '2': 'LOOP_OUT'}),
    'D2':  (('Diode_SMD', 'D_SMB'), 202, 127, 90, 'SMBJ36A', {'1': 'LOOP_OUT', '2': 'GND'}),
    'R10': (R0805, 196, 128, 90, '100k', {'1': 'LOOP_OUT', '2': 'VLOOP'}),
    'R11': (R0805, 196, 134, 90, '10k', {'1': 'VLOOP', '2': 'GND'}),
    'J2':  (TB2, 214, 118, 90, 'LOOP OUT', {'1': 'LOOP_OUT', '2': 'ISENSE'}),
    # ---- merenje struje
    'R14': (R2512, 205, 145, 90, '1R 1W', {'1': 'ISENSE', '2': 'GND'}),
    'R15': (R0805, 198, 150, 0, '1k', {'1': 'ISENSE', '2': 'NA'}),
    'C8':  (C0805, 194, 154, 90, '1n', {'1': 'NA', '2': 'GND'}),
    'U5':  (SOIC8, 186, 154, 0, 'MCP6002', {'1': 'IAMP', '2': 'NM', '3': 'NA', '4': 'GND',
                                           '5': 'GND', '6': 'U5B', '7': 'U5B', '8': '+3V3'}),
    'C14': (C0805, 186, 147, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'R17': (R0805, 180, 160, 90, '10k', {'1': 'NM', '2': 'GND'}),
    'R16': (R0805, 186, 161, 0, '51k', {'1': 'NM', '2': 'IAMP'}),
    'U6':  (('Package_TO_SOT_SMD', 'SOT-23-5'), 174, 160, 0, 'MCP6561',
            {'1': 'BIT', '2': 'GND', '3': 'IAMP', '4': 'PRAG_F', '5': '+3V3'}),
    'C15': (C0805, 174, 154, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'R20': (R0805, 168, 166, 0, '10k', {'1': 'PRAG', '2': 'PRAG_F'}),
    'C9':  (C0805, 174, 166, 90, '1u', {'1': 'PRAG_F', '2': 'GND'}),
    'J3':  (TB2, 214, 165, 90, 'LOOP IN', {'1': 'LOOP_IN', '2': 'ISENSE'}),
    'R12': (R0805, 202, 168, 0, '100k', {'1': 'LOOP_IN', '2': 'VRET'}),
    'R13': (R0805, 196, 172, 90, '10k', {'1': 'VRET', '2': 'GND'}),
    # ---- Pico
    'D4':  (('Diode_SMD', 'D_SMA'), 126, 140, 0, 'SS14', {'2': '+5V', '1': 'VSYS'}),
    'C11': (C0805, 140, 150, 0, '100n', {'1': 'ADC_VREF', '2': 'GND'}),
}

# Pico na dva podnožja 1x20, položen vodoravno; pin 1 levo dole.
PICO_X0, PICO_Y_DOLE, PICO_Y_GORE = 118, 177, 159.22
pico_mreze = {3: 'GND', 8: 'GND', 13: 'GND', 18: 'GND', 23: 'GND', 28: 'GND', 33: 'GND', 38: 'GND',
              4: 'NIVO', 5: 'EN_N', 6: 'BIT', 21: 'PRAG', 31: 'IAMP', 32: 'VLOOP', 34: 'VRET',
              35: 'ADC_VREF', 36: '+3V3', 39: 'VSYS'}

SNAGA = ['+24V_IN', 'VIN_F', '+24V', '+34V', 'NE', 'LOOP_DRV', 'LOOP_OUT', 'ISENSE', 'GND']


def ucitaj(lib, ime):
    fp = pcbnew.FootprintLoad(FP + lib + '.pretty', ime)
    if fp is None:
        raise SystemExit('nema footprinta %s:%s' % (lib, ime))
    return fp


def main():
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    nets = {}

    def net(ime):
        if ime not in nets:
            n = pcbnew.NETINFO_ITEM(b, ime)
            b.Add(n)
            nets[ime] = n
        return nets[ime]

    def postavi(ref, lib_ime, x, y, rot, val, pinovi):
        fp = ucitaj(*lib_ime)
        fp.SetReference(ref)
        fp.SetValue(val)
        b.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            m = pinovi.get(pad.GetNumber())
            if m:
                pad.SetNet(net(m))
        return fp

    for ref, (li, x, y, rot, val, pins) in P.items():
        postavi(ref, li, x, y, rot, val, pins)

    sock = ('Connector_PinSocket_2.54mm', 'PinSocket_1x20_P2.54mm_Vertical')
    # U7A: Pico pinovi 1..20 (donji red), pin 1 levo
    postavi('U7A', sock, PICO_X0, PICO_Y_DOLE, 90, 'Pico 1-20',
            {str(k): pico_mreze[k] for k in range(1, 21) if k in pico_mreze})
    # U7B: Pico pinovi 40..21 (gornji red), podnožje pin n = Pico pin 41-n, pin 1 levo
    postavi('U7B', sock, PICO_X0, PICO_Y_GORE, 90, 'Pico 40-21',
            {str(n): pico_mreze[41 - n] for n in range(1, 21) if (41 - n) in pico_mreze})

    for i, (x, y) in enumerate([(104, 104), (216, 104), (104, 181), (216, 181)]):
        postavi('H%d' % (i + 1), ('MountingHole', 'MountingHole_3.2mm_M3'), x, y, 0, 'M3', {})

    # ivica ploče 120 x 85
    x0, y0, x1, y1 = 100, 100, 220, 185
    for a, c in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        b.Add(s)

    # natpisi na silk sloju
    for txt, x, y, sz in [('APOLLO XP95 LOOP DRIVER v0.1 - SAMO LABORATORIJA', 175, 183, 1.1),
                          ('24V IN', 106, 120.5, 1.0), ('LOOP OUT', 209, 112, 1.0), ('LOOP IN', 209, 159, 1.0),
                          ('BOOST 34V: VIN GND VOUT GND', 112, 135, 0.9), ('HLADNJAK', 176, 102, 1.0)]:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(txt)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(MM(sz), MM(sz)))
        t.SetTextThickness(MM(sz * 0.15))
        b.Add(t)

    ds.SetBoardThickness(MM(1.6))
    pcbnew.SaveBoard('apollo_loop_driver.kicad_pcb', b)
    pcbnew.ExportSpecctraDSN(b, 'apollo_loop_driver.dsn')

    # širi vodovi za mreže snage: posebna klasa u DSN fajlu
    t = open('apollo_loop_driver.dsn').read()
    t = postavi_klasu_snage(t)
    open('apollo_loop_driver.dsn', 'w').write(t)
    print('komponenti:', len(b.GetFootprints()), 'mreza:', len(nets))


def postavi_klasu_snage(dsn):
    import re
    m = re.search(r'\(class kicad_default(.*?)\(circuit', dsn, re.S)
    if not m:
        return dsn
    nets = m.group(1)
    for n in SNAGA:
        nets = re.sub(r'(?<=\s)%s(?=[\s)])' % re.escape(n), '', nets)
    dsn = dsn[:m.start(1)] + nets + dsn[m.end(1):]
    dsn = dsn.replace('(width 200)', '(width 300)')
    snaga = ' '.join(SNAGA)
    klasa = ('(class snaga %s\n      (circuit\n        (use_via Via[0-1]_600:300_um)\n      )\n'
             '      (rule\n        (width 800)\n        (clearance 300)\n      )\n    )\n    ' % snaga)
    i = dsn.index('(class kicad_default')
    return dsn[:i] + klasa + dsn[i:]


if __name__ == '__main__':
    main()
