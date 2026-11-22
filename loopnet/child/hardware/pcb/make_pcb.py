"""Pravi KiCad 7 pločicu za LoopNet 1IN v0.1 (30 x 20 mm, 2 sloja).

Pokretanje:  python3.12 make_pcb.py   (KiCad 7 pcbnew modul)
Izlaz:       loopnet_1in.kicad_pcb (raspored + mreže, bez vodova) i loopnet_1in.dsn (za Freerouting)

Raspored pinova proveren po datasheet-ovima (vidi ../../README.md, „Provera pinova“):
  ATtiny1616 VQFN-20: 1 PA2, 2 PA3, 3 GND, 4 VDD, 5 PA4, 6 PA5, 7 PA6, 8 PA7, 9 PB5, 10 PB4, 11 PB3, 12 PB2,
                      13 PB1, 14 PB0, 15 PC0, 16 PC1, 17 PC2, 18 PC3, 19 PA0/UPDI, 20 PA1, EP (21) -> GND
  TPS7B8133 DRV (WSON-6): 1 IN, 2 EN, 3 GND, 4 GND, 5 DNC (na GND), 6 OUT, termalni pad -> GND
  BAV99 (SOT-23): 1 anoda D1, 2 katoda D2, 3 katoda D1 = anoda D2
  MMBT5551 / MMBT3904 (SOT-23): 1 B, 2 E, 3 C;   BCX56 (SOT-89, Nexperia): 1 E, 2 C (i tab), 3 B
  SMAJ40A (SMA) i BZT52C10 (SOD-123): pad 1 = katoda
"""
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew

FP = '/usr/share/kicad/footprints/'
MM = pcbnew.FromMM
IME = 'loopnet_1in'

R0603 = ('Resistor_SMD', 'R_0603_1608Metric')       # otpornici na liniji (do 64 V): 0603, 75 V
R0402 = ('Resistor_SMD', 'R_0402_1005Metric')
C0603 = ('Capacitor_SMD', 'C_0603_1608Metric')
C0402 = ('Capacitor_SMD', 'C_0402_1005Metric')
C0805 = ('Capacitor_SMD', 'C_0805_2012Metric')
SOT23 = ('Package_TO_SOT_SMD', 'SOT-23')
TB2 = ('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal')

# ref: (biblioteka, vrednost, {pin: mreža})
# Mreže: LA/LB žice linije, VP ispravljena linija, VC napon iza izvora struje (10 V Zener), VDD 3,3 V
P = {
    # ---- stezaljke: linija ulaz/izlaz (prolazno), ulaz kontakta
    'J1': (TB2, 'LINIJA ULAZ', {'1': 'LA', '2': 'LB'}),
    'J2': (TB2, 'LINIJA IZLAZ', {'1': 'LA', '2': 'LB'}),
    'J3': (TB2, 'ULAZ', {'1': 'INP', '2': 'GND'}),
    # ---- most (2x BAV99) i TVS
    'D1': (SOT23, 'BAV99', {'1': 'GND', '2': 'VP', '3': 'LA'}),
    'D2': (SOT23, 'BAV99', {'1': 'GND', '2': 'VP', '3': 'LB'}),
    'D3': (('Diode_SMD', 'D_SMA'), 'SMAJ40A', {'1': 'VP', '2': 'GND'}),
    # ---- izvor konstantne struje ~180 µA: I = Vbe(Q2)/R2 + VP/R1
    'R1': (R0603, '2M2', {'1': 'VP', '2': 'QB'}),
    'Q1': (SOT23, 'MMBT5551', {'1': 'QB', '2': 'QE', '3': 'VP'}),
    'R2': (R0402, '3k3', {'1': 'QE', '2': 'VC'}),
    'Q2': (SOT23, 'MMBT3904', {'1': 'QE', '2': 'VC', '3': 'QB'}),
    'D4': (('Diode_SMD', 'D_SOD-123'), 'BZT52C10', {'1': 'VC', '2': 'GND'}),
    'C1': (C0805, '10u/25V', {'1': 'VC', '2': 'GND'}),
    # ---- 3,3 V
    'U1': (('Package_SON', 'WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm'), 'TPS7B8133DRV',
           {'1': 'VC', '2': 'VC', '3': 'GND', '4': 'GND', '5': 'GND', '6': 'VDD', '7': 'GND'}),
    'C2': (C0805, '10u/25V', {'1': 'VDD', '2': 'GND'}),
    'C3': (C0402, '100n', {'1': 'VDD', '2': 'GND'}),
    # ---- MCU
    'U2': (('Package_DFN_QFN', 'VQFN-20-1EP_3x3mm_P0.4mm_EP1.7x1.7mm'), 'ATtiny1616-MNR',
           {'2': 'IN_DRV', '3': 'GND', '4': 'VDD', '5': 'IN_SENSE', '7': 'VTHR', '8': 'LINE',
            '12': 'BTN', '13': 'LED', '14': 'SINK', '19': 'UPDI', '21': 'GND',
            '6': 'AC_OUT', '1': 'AC_OUT'}),   # AC0 OUT (PA5) -> PA2: asinhroni prekid budi CPU iz STANDBY-a
    # ---- prijem: delitelj sa obe žice pre mosta, prag na kondenzatoru (DAC0 sample-hold)
    'R3': (R0603, '4M7', {'1': 'LA', '2': 'LINE'}),
    'R4': (R0603, '4M7', {'1': 'LB', '2': 'LINE'}),
    'R5': (R0402, '330k', {'1': 'LINE', '2': 'GND'}),
    'C4': (C0402, '10n', {'1': 'VTHR', '2': 'GND'}),
    # ---- odgovor: 10 mA ponor
    'Q3': (('Package_TO_SOT_SMD', 'SOT-89-3'), 'BCX56-16', {'1': 'QSE', '2': 'VP', '3': 'QSB'}),
    'R6': (R0402, '240', {'1': 'QSE', '2': 'GND'}),
    'R7': (R0402, '1k', {'1': 'SINK', '2': 'QSB'}),
    'R8': (R0402, '100k', {'1': 'QSB', '2': 'GND'}),
    # ---- ulaz kontakta (EOL), LED, taster, UPDI
    'R9': (R0402, '2k2', {'1': 'IN_DRV', '2': 'INP'}),
    'R10': (R0402, '1k', {'1': 'INP', '2': 'IN_SENSE'}),
    'C5': (C0402, '1n', {'1': 'IN_SENSE', '2': 'GND'}),
    'R11': (R0402, '1k', {'1': 'LED', '2': 'LED_A'}),
    'D5': (('LED_SMD', 'LED_0603_1608Metric'), 'LED', {'1': 'GND', '2': 'LED_A'}),
    'SW1': (('Button_Switch_SMD', 'SW_Push_1P1T_XKB_TS-1187A'), 'TASTER', {'1': 'BTN', '2': 'GND'}),
    'J4': (('Connector_PinHeader_1.27mm', 'PinHeader_1x03_P1.27mm_Vertical'), 'UPDI',
           {'1': 'VDD', '2': 'UPDI', '3': 'GND'}),
}

# (x, y, rotacija); ploča 30 x 20 mm, gornji levi ugao (100, 100)
POZ = {
    'J1': (102.75, 115.0, 0), 'J2': (111.25, 115.0, 0), 'J3': (122.25, 115.0, 0),
    'D3': (104.3, 101.95, 0), 'D1': (102.0, 105.6, 0), 'D2': (105.9, 105.6, 0),
    'R3': (102.5, 109.9, 0), 'R4': (105.7, 109.9, 0),
    'Q1': (109.75, 102.0, 0), 'R1': (110.0, 104.9, 0), 'Q2': (113.65, 102.0, 0), 'R2': (113.6, 104.6, 0),
    'D4': (109.0, 108.9, 90), 'C1': (116.55, 102.3, 90),
    'U1': (116.6, 105.35, 0), 'C2': (118.55, 102.3, 90), 'C3': (119.3, 107.9, 90),
    'U2': (121.65, 104.4, 0), 'R5': (121.1, 107.6, 0), 'C4': (121.1, 108.8, 0),
    'Q3': (113.0, 108.9, 0), 'R6': (117.0, 110.2, 0), 'R7': (117.0, 108.0, 0), 'R8': (117.0, 109.1, 0),
    'R9': (118.0, 112.6, 90), 'R10': (119.2, 112.6, 90), 'C5': (118.6, 114.9, 0),
    'R11': (123.3, 109.2, 0), 'D5': (123.3, 110.5, 0),
    'SW1': (126.95, 104.0, 90), 'J4': (126.0, 109.6, 90),
}
assert set(POZ) == set(P), set(P) ^ set(POZ)

HV = ['LA', 'LB', 'VP', 'QB', 'QE']                # do 64 V (stezanje TVS-a)
KLASE = [
    ('linija', ['LA', 'LB', 'VP'], 400, 300),          # 10 mA odgovor + punjenje kabla, do 64 V
    ('hv', ['QB', 'QE'], 250, 300),                    # izvor struje, do 64 V
]

# Funkcionalni blokovi (okviri na F.Fab)
BLOKOVI = [
    ('LINIJA I MOST', ['J1', 'J2', 'D1', 'D2', 'D3']),
    ('IZVOR STRUJE 180uA + 3V3', ['Q1', 'Q2', 'R1', 'R2', 'D4', 'C1', 'U1', 'C2']),
    ('ODGOVOR 10mA', ['Q3', 'R6', 'R7', 'R8']),
    ('MCU', ['U2', 'C3', 'R3', 'R4', 'R5', 'C4', 'J4', 'SW1', 'R11', 'D5']),
    ('ULAZ EOL', ['J3', 'R9', 'R10', 'C5']),
]

# Unapred zadati (zaključani) vodovi i via: (mreža, [(sloj, x1, y1, x2, y2, širina)], [via]).
# Via u centralnim padovima MCU (U2) i LDO (U1) postavljaju se pre rutiranja da ih Freerouting zaobiđe.
PREVODI = [
    ('GND', [], [(121.65, 104.4), (116.6, 105.35)]),
]

X0, Y0, X1, Y1 = 100, 100, 130, 120


def ucitaj(lib, ime):
    fp = pcbnew.FootprintLoad(FP + lib + '.pretty', ime)
    if fp is None:
        raise SystemExit('nema footprinta %s:%s' % (lib, ime))
    return fp


def napravi():
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetClearance(MM(0.15))
    nc.SetTrackWidth(MM(0.2))
    nc.SetViaDiameter(MM(0.6))
    nc.SetViaDrill(MM(0.3))
    ds.m_MinClearance = MM(0.15)
    ds.m_TrackMinWidth = MM(0.15)
    ds.m_CopperEdgeClearance = MM(0.3)       # JLCPCB: bakar do ivice >= 0,3 mm
    nets = {}

    def net(ime):
        if ime not in nets:
            n = pcbnew.NETINFO_ITEM(b, ime)
            b.Add(n)
            nets[ime] = n
        return nets[ime]

    for ref, (li, val, pins) in P.items():
        x, y, rot = POZ[ref]
        fp = ucitaj(*li)
        fp.SetReference(ref)
        fp.SetValue(val)
        b.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            m = pins.get(pad.GetNumber())
            if m:
                pad.SetNet(net(m))
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        fp.Reference().SetTextThickness(MM(0.1))
        fp.Reference().SetVisible(False)            # premalo mesta: oznake su na F.Fab crtežu
    for a, c in [((X0, Y0), (X1, Y0)), ((X1, Y0), (X1, Y1)), ((X1, Y1), (X0, Y1)), ((X0, Y1), (X0, Y0))]:
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        b.Add(s)
    # natpisi na donjoj strani (gore nema mesta)
    for txt, x, y, sz in [('LoopNet 1IN v0.1', 115, 103, 1.0), ('LINIJA ULAZ', 104.5, 111.4, 0.8),
                          ('LINIJA IZLAZ', 113.0, 111.4, 0.8), ('ULAZ EOL', 124.0, 112.4, 0.8),
                          ('UPDI: VDD UPDI GND', 115, 105, 0.8), ('nije protivpozarni', 115, 107, 0.8)]:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(txt)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.B_SilkS)
        t.SetMirrored(True)
        t.SetTextSize(pcbnew.VECTOR2I(MM(sz), MM(sz)))
        t.SetTextThickness(MM(sz * 0.15))
        b.Add(t)
    fpd = {f.GetReference(): f for f in b.GetFootprints()}
    for ime, refs in BLOKOVI:
        xs0, ys0, xs1, ys1 = [], [], [], []
        for r in refs:
            c = fpd[r].GetBoundingBox(False, False)
            xs0.append(pcbnew.ToMM(c.GetLeft())); ys0.append(pcbnew.ToMM(c.GetTop()))
            xs1.append(pcbnew.ToMM(c.GetRight())); ys1.append(pcbnew.ToMM(c.GetBottom()))
        r = pcbnew.PCB_SHAPE(b)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetStart(pcbnew.VECTOR2I(MM(max(min(xs0) - 0.3, X0)), MM(max(min(ys0) - 0.3, Y0))))
        r.SetEnd(pcbnew.VECTOR2I(MM(min(max(xs1) + 0.3, X1)), MM(min(max(ys1) + 0.3, Y1))))
        r.SetLayer(pcbnew.F_Fab)
        r.SetWidth(MM(0.1))
        b.Add(r)
        t = pcbnew.PCB_TEXT(b)
        t.SetText(ime)
        t.SetLayer(pcbnew.F_Fab)
        t.SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        t.SetTextThickness(MM(0.1))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        t.SetPosition(pcbnew.VECTOR2I(MM(max(min(xs0), X0) + 0.2), MM(max(min(ys0), Y0) + 0.5)))
        b.Add(t)
    for ime, segs, vias in PREVODI:
        n = net(ime)
        for lay, x1, y1, x2, y2, w in segs:
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1))); t.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
            t.SetWidth(MM(w)); t.SetLayer(pcbnew.F_Cu if lay == 'F' else pcbnew.B_Cu)
            t.SetNet(n); t.SetLocked(True); b.Add(t)
        for x, y in vias:
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetDrill(MM(0.3)); v.SetWidth(MM(0.6))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(n); v.SetLocked(True); b.Add(v)
    ds.SetBoardThickness(MM(1.6))
    return b, nets


def preklapanja(b):
    """Parovi komponenti čiji se courtyard-i preklapaju, i komponente van ivice ploče."""
    out = []
    box = {}
    for f in b.GetFootprints():
        c = f.GetCourtyard(pcbnew.F_CrtYd)
        bb = c.BBox() if not c.IsEmpty() else f.GetBoundingBox(False, False)
        box[f.GetReference()] = (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                                 pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))
    refs = sorted(box)
    for i, a in enumerate(refs):
        ax0, ay0, ax1, ay1 = box[a]
        if ax0 < X0 - 0.01 or ay0 < Y0 - 0.01 or ax1 > X1 + 0.01 or ay1 > Y1 + 0.01:
            out.append((a, 'IVICA', box[a]))
        for c in refs[i + 1:]:
            bx0, by0, bx1, by1 = box[c]
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                out.append((a, c, round(min(ax1, bx1) - max(ax0, bx0), 2), round(min(ay1, by1) - max(ay0, by0), 2)))
    return out


def slika(b, ime='raspored.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.add_patch(plt.Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fill=False, lw=1.5))
    for f in b.GetFootprints():
        c = f.GetCourtyard(pcbnew.F_CrtYd)
        bb = c.BBox() if not c.IsEmpty() else f.GetBoundingBox(False, False)
        x0, y0 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())
        ax.add_patch(plt.Rectangle((x0, y0), pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight()), fill=False, ec='b', lw=0.6))
        for pd in f.Pads():
            q = pd.GetPosition(); sz = pd.GetBoundingBox()
            ax.add_patch(plt.Rectangle((pcbnew.ToMM(sz.GetLeft()), pcbnew.ToMM(sz.GetTop())), pcbnew.ToMM(sz.GetWidth()),
                                       pcbnew.ToMM(sz.GetHeight()), color='orange', alpha=0.6))
            ax.text(pcbnew.ToMM(q.x), pcbnew.ToMM(q.y), pd.GetNetname()[:6], fontsize=5, ha='center', va='center')
        p = f.GetPosition()
        ax.text(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y) - 0.6, f.GetReference(), fontsize=8, color='r', ha='center')
    ax.set_xlim(X0 - 1, X1 + 1); ax.set_ylim(Y1 + 1, Y0 - 1); ax.set_aspect('equal')
    fig.savefig(ime, dpi=110)


def postavi_klase(dsn):
    import re
    m = re.search(r'\(class kicad_default(.*?)\(circuit', dsn, re.S)
    if not m:
        return dsn
    nets = m.group(1)
    for _, mr, _, _ in KLASE:
        for n in mr:
            nets = re.sub(r'(?<=\s)%s(?=[\s)])' % re.escape(n), '', nets)
    dsn = dsn[:m.start(1)] + nets + dsn[m.end(1):]
    klase = ''
    for ime, mr, w, c in KLASE:
        klase += ('(class %s %s\n      (circuit\n        (use_via Via[0-1]_600:300_um)\n      )\n'
                  '      (rule\n        (width %d)\n        (clearance %d)\n      )\n    )\n    ' % (ime, ' '.join(mr), w, c))
    i = dsn.index('(class kicad_default')
    return dsn[:i] + klase + dsn[i:]


def main():
    b, nets = napravi()
    pr = preklapanja(b)
    for p in pr:
        print('PREKLAPANJE:', p)
    if '--slika' in sys.argv:
        slika(b)
    if '--samo-proveri' in sys.argv:
        return
    pcbnew.SaveBoard(IME + '.kicad_pcb', b)
    pcbnew.ExportSpecctraDSN(b, IME + '.dsn')
    t = postavi_klase(open(IME + '.dsn').read())
    open(IME + '.dsn', 'w').write(t)
    print('komponenti:', len(b.GetFootprints()), 'mreza:', len(nets))


if __name__ == '__main__':
    main()
