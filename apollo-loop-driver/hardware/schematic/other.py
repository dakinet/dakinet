import schemdraw
import schemdraw.elements as elm
schemdraw.config(fontsize=11, lw=1.3, font='DejaVu Sans')
def gnd(d, pt): d.add(elm.Ground().at(pt))
T = lambda w=2.9: elm.Tag(width=w)

# ---------------- LIST 1: NAPAJANJE ----------------
with schemdraw.Drawing(file='power.svg', show=False) as d:
    d.config(unit=2)
    d.add(elm.Dot(open=True).at((0, 0)).label('J1-1 +24 V (21–28 V)', loc='left'))
    d.add(elm.Fuse().right(2.4).label('F1  3 A', loc='top'))
    d.add(elm.Schottky().right(2.4).label('D3 SS34', loc='top'))
    V24 = d.here; d.add(elm.Dot()); d.add(elm.Label().at((V24[0], V24[1]+0.9)).label('+24V', color='#b4441f'))
    d.add(elm.Dot(open=True).at((0, -3.5)).label('J1-2 GND', loc='left')); d.add(elm.Line().right(1)); gnd(d, d.here)
    d.add(elm.Capacitor(polar=True).down(2.4).at(V24).label('C1\n100µ/50V', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(2.2).at(V24)); NV = d.here; d.add(elm.Dot())
    d.add(elm.Capacitor().down(2.4).at(NV).label('C31\n1µ/50V', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(1.6).at(NV)); NL = d.here; d.add(elm.Dot())
    d.add(elm.Inductor2(loops=3).right(3.2).label('L1  100 µH (SRR1260-101M)', loc='top'))
    SW = d.here; d.add(elm.Dot()); d.add(elm.Label().at((SW[0], SW[1]+0.9)).label('SW', color='#b4441f'))
    d.add(elm.Schottky().right(3).label('D1  SS56', loc='top'))
    V34 = d.here; d.add(elm.Dot()); d.add(elm.Label().at((V34[0], V34[1]+0.9)).label('+34V', color='#b4441f'))
    ic = d.add(elm.Ic(pins=[elm.IcPin(name='VIN', pin='5', side='left', slot='1/2'), elm.IcPin(name='COMP', pin='1', side='left', slot='2/2'),
                            elm.IcPin(name='SW', pin='4', side='top'), elm.IcPin(name='FB', pin='2', side='right'), elm.IcPin(name='GND', pin='3', side='bottom')],
                      edgepadW=1.4, edgepadH=0.9, label='U1 LM2587S-ADJ', lblloc='bottom', lblofst=0.6).right().anchor('SW').at((SW[0], SW[1]-1.6)))
    d.add(elm.Line().at(SW).to(ic.SW))
    d.add(elm.Wire('|-').at(NL).to(ic.VIN)); d.add(elm.Dot().at((NL[0], ic.VIN[1])))
    d.add(elm.Line().down(0.6).at(ic.GND)); gnd(d, d.here)
    d.add(elm.Line().left(2.4).at(ic.COMP)); cp = d.here
    d.add(elm.Resistor().down(1.8).label('R30\n3k0', loc='bottom')); d.add(elm.Capacitor().down(1.6).label('C30\n680n', loc='bottom')); gnd(d, d.here)
    for i, lbl in enumerate(['C3\n470µ/50V', 'C32\n470µ/50V', 'C5\n1µ/50V', 'C63\n10µ/50V']):
        x = V34[0] + 2.6*i
        if i: d.add(elm.Line().at((x-2.6, V34[1])).right(2.6)); d.add(elm.Dot().at((x, V34[1])))
        d.add(elm.Capacitor(polar=(i < 2)).down(2.4).at((x, V34[1])).label(lbl, loc='bottom')); gnd(d, d.here)
    xr = V34[0] + 10.2
    d.add(elm.Line().at((xr-2.4, V34[1])).right(2.4)); d.add(elm.Dot())
    d.add(elm.Line().right(1.6)); d.add(T(2.2).right().label('+34V'))
    d.add(elm.Resistor().down(2.6).at((xr, V34[1])).label('R31\n53k6', loc='bottom'))
    NFBp = d.here; d.add(elm.Dot())
    d.add(elm.Resistor().down(2.0).label('R32\n2k0', loc='bottom')); gnd(d, d.here)
    d.add(elm.Wire('-|').at(ic.FB).to((xr-1.0, NFBp[1]))); d.add(elm.Line().to(NFBp))
    # 5 V i 3,3 V
    y5 = -9.5
    p5 = (0.5, y5)
    d.add(T(1.8).left().at(p5).label('+24V'))
    reg = d.add(elm.Ic(pins=[elm.IcPin(name='VIN', pin='1', side='left'), elm.IcPin(name='VOUT', pin='3', side='right'), elm.IcPin(name='GND', pin='2', side='bottom')],
                       edgepadW=0.9, edgepadH=0.6, label='U2 R-78E5.0-0.5', lblloc='top', lblofst=0.2).right().anchor('VIN').at((p5[0]+2.5, y5)))
    d.add(elm.Line().at(p5).to(reg.VIN))
    d.add(elm.Capacitor().down(2).at((p5[0]+1.2, y5)).label('C16\n4µ7/50V', loc='bottom')); gnd(d, d.here); d.add(elm.Dot().at((p5[0]+1.2, y5)))
    d.add(elm.Line().down(0.6).at(reg.GND)); gnd(d, d.here)
    d.add(elm.Line().right(1.4).at(reg.VOUT)); N5 = d.here; d.add(elm.Dot()); d.add(elm.Label().at((N5[0], N5[1]+0.9)).label('+5V', color='#b4441f'))
    d.add(elm.Capacitor().down(2).at(N5).label('C10\n10µ', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(2.6).at(N5)); M = d.here; d.add(elm.Dot())
    d.add(elm.Capacitor().down(2).at(M).label('C54\n1µ', loc='bottom')); gnd(d, d.here)
    ldo = d.add(elm.Ic(pins=[elm.IcPin(name='VIN', pin='1', side='left', slot='1/2'), elm.IcPin(name='EN', pin='3', side='left', slot='2/2'),
                             elm.IcPin(name='VOUT', pin='5', side='right'), elm.IcPin(name='GND', pin='2', side='bottom')],
                       edgepadW=0.9, edgepadH=0.6, label='U11 AP2112K-3.3', lblloc='top', lblofst=0.2).right().anchor('VIN').at((M[0]+1.5, M[1])))
    d.add(elm.Line().at(M).to(ldo.VIN))
    d.add(elm.Wire('-|').at(ldo.EN).to((M[0]+0.7, M[1]))); d.add(elm.Dot().at((M[0]+0.7, M[1])))
    d.add(elm.Line().down(0.6).at(ldo.GND)); gnd(d, d.here)
    d.add(elm.Line().right(1.4).at(ldo.VOUT)); N3 = d.here; d.add(elm.Dot())
    d.add(elm.Capacitor().down(2).at(N3).label('C55\n1µ', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(1.6).at(N3)); d.add(T(1.8).right().label('+3V3'))
    d.add(elm.Line().right(5.0).at((N5[0], N5[1]))) if False else None
    d.add(elm.Label().at((0, -17)).label('LM2587: Vout = 1,23 V · (1 + 53k6 / 2k0) = 34,2 V  ·  vrednosti prema TI referenci „24-V To 36-V Boost“ (L 100 µH, Rc 3k, Cc 0,68 µF, R1/R2 = 56k3/2k → ovde 53k6/2k); C31, L1, D1, C5, C63 uz pinove U1  ·  +5V ide i na U8 VBUS2 i REF3033', halign='left'))

# ---------------- LIST 3: MERENJE STRUJE ----------------
with schemdraw.Drawing(file='sense.svg', show=False) as d:
    d.config(unit=2)
    d.add(elm.Dot(open=True).at((0, 0)).label('J2-2 LOOP OUT −', loc='left'))
    d.add(elm.Line().right(2.5)); IS = d.here; d.add(elm.Dot())
    d.add(elm.Label().at((IS[0], IS[1]+0.9)).label('ISENSE', color='#b4441f'))
    d.add(elm.Dot(open=True).at((0, -1.5)).label('J3-2 LOOP IN −', loc='left'))
    d.add(elm.Wire('-|').to((IS[0]-1.2, IS[1]))); d.add(elm.Dot())
    d.add(elm.Resistor().down(3).at(IS).label('R14\n1R0 1% 1W\n(šant)', loc='bottom')); gnd(d, d.here)
    d.add(elm.Resistor().right(3.5).at(IS).label('R15  1k0', loc='top')); NA = d.here; d.add(elm.Dot())
    d.add(elm.Capacitor().down(2.4).at(NA).label('C8\n1n', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(1.2).at(NA))
    op = d.add(elm.Opamp(leads=True).right().flip().anchor('in2').label('U5A\nMCP6002', loc='center', ofst=(-0.4, 0)))
    OUT = op.out
    d.add(elm.Line().right(1.4).at(OUT)); IA = d.here; d.add(elm.Dot())
    d.add(elm.Label().at((IA[0], IA[1]+0.9)).label('IAMP', color='#b4441f'))
    # gain network
    d.add(elm.Line().down(0.9).at(op.in1)); NM = d.here
    d.add(elm.Dot().at(NM))
    d.add(elm.Resistor().down(2.2).at(NM).label('R17\n10k0', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(1.2).at(NM))
    d.add(elm.Resistor().right(IA[0]-NM[0]-1.2).label('R16  40k2', loc='bottom'))
    d.add(elm.Line().to(IA))
    d.add(elm.Line().up(1.2).at((IA[0], IA[1]))) if False else None
    d.add(elm.Line().right(1.2).at(IA)); d.add(elm.Dot()); TAP = d.here
    d.add(elm.Line().up(1.6).at(TAP)); d.add(T(3.2).right().label('ADC0  GP26'))
    d.add(elm.Line().right(1.2).at(TAP))
    cmp_ = d.add(elm.Opamp(leads=True).right().flip().anchor('in2').label('U6\nMCP6561', loc='center', ofst=(-0.4, 0)))
    d.add(elm.Line().right(1.2).at(cmp_.out)); d.add(T(2.6).right().label('BIT  GP4'))
    d.add(elm.Line().down(1.6).at(cmp_.in1)); NT = d.here; d.add(elm.Dot())
    d.add(elm.Capacitor().down(2).at(NT).label('C9\n1µ', loc='bottom')); gnd(d, d.here)
    d.add(elm.Resistor().left(2.4).at(NT).label('R20 10k', loc='bottom'))
    d.add(T(2.9).left().label('PRAG  GP16'))
    # VRET divider
    yv = -8.5
    d.add(elm.Dot(open=True).at((0, yv)).label('J3-1 LOOP IN +', loc='left'))
    d.add(elm.Resistor().right(3).label('R12  100k', loc='top')); NV = d.here; d.add(elm.Dot())
    d.add(elm.Resistor().down(2).at(NV).label('R13\n10k0', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(0.9).at(NV)); d.add(elm.Dot()); cn = d.here
    d.add(elm.Capacitor().down(1.8).at(cn).label('C60\n1n', loc='right')); gnd(d, d.here)
    d.add(elm.Line().right(1.0).at(cn)); d.add(T(3.2).right().label('VRET  GP28'))
    # ---- hardverska zaštita > ~500 mA sa zadrškom
    yo = -16.5
    d.add(T(2.4).left().at((3.0, yo)).label('IAMP'))
    d.add(elm.Resistor().right(2.6).at((3.0, yo)).label('R35 10k', loc='top')); OC = d.here; d.add(elm.Dot())
    d.add(elm.Line().right(0.7).at(OC)); c62 = d.here; d.add(elm.Dot())
    d.add(elm.Capacitor().down(1.8).at(c62).label('C62 1n', loc='right')); gnd(d, d.here)
    d.add(elm.Line().right(0.7).at(c62))
    oc = d.add(elm.Opamp(leads=True).right().flip().anchor('in2').label('U12\nMCP6561', loc='center', ofst=(-0.4, 0)))
    d.add(elm.Line().right(1.6).at(oc.out)); OP = d.here; d.add(elm.Dot())
    d.add(elm.Label().at((OP[0], OP[1] + 0.8)).label('OCP', color='#b4441f'))
    d.add(elm.Line().right(1.4).at(OP)); d.add(T(3.0).right().label('OC_FLAG  GP6'))
    d.add(elm.Line().up(2.6).at(OP)); fb = d.here
    d.add(elm.Schottky().left(OP[0] - OC[0] - 3.0).at(fb).label('D6 BAT54', loc='top'))
    d.add(elm.Resistor().left(3.0).label('R36 1k (zadrška)', loc='top')); d.add(elm.Line().to(OC))
    d.add(elm.Line().down(1.6).at(oc.in1)); NR = d.here; d.add(elm.Dot())
    d.add(elm.Resistor().down(1.8).at(NR).label('R34\n10k', loc='right')); gnd(d, d.here)
    d.add(elm.Line().right(1.4).at(NR)); d.add(elm.Resistor().down(1.8).label('R33\n3k3', loc='right')); d.add(T(1.8).down().label('+3V3'))
    # Q6 gasi VSET, Q7 briše zadršku
    q6x = OP[0] + 5.5
    d.add(elm.Line().down(2.4).at(OP)); g6 = d.here
    d.add(elm.Line().right(q6x - g6[0] - 1.37).at(g6))
    q6 = d.add(elm.NFet().right().reverse().anchor('gate').label('Q6 2N7002\nD = VSET (list 2)', loc='right'))
    gnd(d, q6.source)
    d.add(elm.Line().up(0.5).at(q6.drain)); d.add(T(1.8).up().label('VSET'))
    d.add(elm.Line().down(3.4).at(OC))
    q7 = d.add(elm.NFet().right().reverse().anchor('drain').label('Q7 2N7002', loc='right'))
    gnd(d, q7.source)
    d.add(elm.Line().left(0.8).at(q7.gate)); gq = d.here; d.add(elm.Dot())
    d.add(elm.Line().left(1.2)); d.add(T(3.0).left().label('OC_RST  GP5'))
    d.add(elm.Resistor().down(1.6).at(gq).label('R37 100k', loc='left')); gnd(d, d.here)
    d.add(elm.Label().at((0, -25)).label('U5, U6 napajanje +3V3, 100n uz svaki čip  ·  20 mA · 1 Ω · 5,02 = 100 mV, 500 mA = 2,51 V  ·  prag = struja mirovanja + 10 mA (PWM 100 kHz kroz R20/C9)\nZaštita: 500 mA → IAMP 2,51 V > 2,48 V (R33/R34) → OCP = 1 → Q6 ugasi petlju za nekoliko µs; D6/R36 drže stanje dok RP2040 ne pusti OC_RST', halign='left'))

# ---------------- LIST 4: RP2040 I USB IZOLACIJA ----------------
with schemdraw.Drawing(file='pico.svg', show=False) as d:
    d.config(unit=2)
    pinsL = [elm.IcPin(name='QSPI_SS', pin='56', side='left'), elm.IcPin(name='QSPI_SD1', pin='55', side='left'),
             elm.IcPin(name='QSPI_SD2', pin='54', side='left'), elm.IcPin(name='QSPI_SD0', pin='53', side='left'),
             elm.IcPin(name='QSPI_SCLK', pin='52', side='left'), elm.IcPin(name='QSPI_SD3', pin='51', side='left'),
             elm.IcPin(name='USB_DP', pin='47', side='left'), elm.IcPin(name='USB_DM', pin='46', side='left'),
             elm.IcPin(name='XIN', pin='20', side='left'), elm.IcPin(name='XOUT', pin='21', side='left'),
             elm.IcPin(name='RUN', pin='26', side='left'), elm.IcPin(name='SWCLK', pin='24', side='left'), elm.IcPin(name='SWDIO', pin='25', side='left')]
    pinsR = [elm.IcPin(name='GPIO2', pin='4', side='right'), elm.IcPin(name='GPIO3', pin='5', side='right'),
             elm.IcPin(name='GPIO4', pin='6', side='right'), elm.IcPin(name='GPIO16', pin='27', side='right'),
             elm.IcPin(name='GPIO25', pin='37', side='right'), elm.IcPin(name='GPIO26/ADC0', pin='38', side='right'),
             elm.IcPin(name='GPIO27/ADC1', pin='39', side='right'), elm.IcPin(name='GPIO28/ADC2', pin='40', side='right'),
             elm.IcPin(name='IOVDD×6, USB_VDD, ADC_AVDD, VREG_VIN', pin='', side='right'),
             elm.IcPin(name='DVDD×2, VREG_VOUT', pin='23,50,45', side='right'), elm.IcPin(name='TESTEN, GND (EP)', pin='19,57', side='right')]
    ic = d.add(elm.Ic(pins=pinsL[::-1] + pinsR[::-1], pinspacing=0.9, edgepadW=4.0, edgepadH=0.5, label='U9  RP2040 (QFN-56)', lblloc='top', lblofst=0.3).right().at((0, 0)))
    A = ic.absanchors
    out = {'GPIO2': 'NIVO', 'GPIO3': '/EN', 'GPIO4': 'BIT', 'GPIO16': 'PRAG', 'GPIO26/ADC0': 'IAMP', 'GPIO27/ADC1': 'VLOOP', 'GPIO28/ADC2': 'VRET'}
    for p, t in out.items():
        d.add(elm.Line().right(1.0).at(A[p])); d.add(T(2.0).right().label(t))
    d.add(elm.Line().right(1.0).at(A['GPIO25'])); d.add(elm.Resistor().right(1.8).label('R27 1k', loc='top')); d.add(elm.LED().right(1.4).label('D5', loc='top')); gnd(d, d.here)
    d.add(elm.Line().right(1.0).at(A['IOVDD×6, USB_VDD, ADC_AVDD, VREG_VIN'])); d.add(T(2.0).right().label('+3V3'))
    d.add(elm.Line().right(1.0).at(A['DVDD×2, VREG_VOUT'])); d.add(elm.Dot()); dv = d.here
    d.add(elm.Capacitor().down(1.3).label('C46,C49 100n\nC47 1µ', loc='right')); gnd(d, d.here)
    d.add(elm.Line().right(1.0).at(A['TESTEN, GND (EP)'])); d.add(elm.Line().down(0.4)); gnd(d, d.here)
    # flash (levo gore), veze preko oznaka
    for p in ['QSPI_SS', 'QSPI_SD1', 'QSPI_SD2', 'QSPI_SD0', 'QSPI_SCLK', 'QSPI_SD3']:
        d.add(elm.Line().left(1.0).at(A[p])); d.add(T(2.4).left().label(p.replace('QSPI_', 'Q')))
    fl = d.add(elm.Ic(pins=[elm.IcPin(name='/CS', pin='1', side='right'), elm.IcPin(name='DO', pin='2', side='right'),
                            elm.IcPin(name='/WP', pin='3', side='right'), elm.IcPin(name='DI', pin='5', side='right'),
                            elm.IcPin(name='CLK', pin='6', side='right'), elm.IcPin(name='/HOLD', pin='7', side='right'),
                            elm.IcPin(name='VCC', pin='8', side='left'), elm.IcPin(name='GND', pin='4', side='left')][::-1],
                      pinspacing=0.9, edgepadW=1.6, edgepadH=0.5, label='U10 W25Q16JV', lblloc='top', lblofst=0.2)
              .right().at((-24, 2)))
    for a, t in [('/CS', 'QSS'), ('DO', 'QSD1'), ('/WP', 'QSD2'), ('DI', 'QSD0'), ('CLK', 'QSCLK'), ('/HOLD', 'QSD3')]:
        d.add(elm.Line().right(1.0).at(fl.absanchors[a])); d.add(T(2.2).right().label(t))
    d.add(elm.Line().left(1.0).at(fl.absanchors['VCC'])); d.add(T(1.8).left().label('+3V3'))
    d.add(elm.Line().left(1.0).at(fl.absanchors['GND'])); d.add(elm.Line().down(0.4)); gnd(d, d.here)
    # BOOTSEL i pull-up na QSS (dole levo)
    bx, by = -26, -6
    d.add(T(2.0).left().at((bx, by)).label('QSS'))
    d.add(elm.Line().at((bx, by)).right(1.0)); n = d.here; d.add(elm.Dot())
    d.add(elm.Resistor().up(1.6).at(n).label('R23 10k', loc='right')); d.add(elm.Vdd().label('+3V3'))
    d.add(elm.Resistor().right(2.0).at(n).label('R24 1k', loc='top'))
    d.add(elm.Button().right(2.2).label('SW1 BOOTSEL', loc='bottom')); d.add(elm.Line().down(0.4)); gnd(d, d.here)
    # RESET
    rx, ry = -12, -6
    d.add(T(2.0).left().at((rx, ry)).label('RUN'))
    d.add(elm.Line().at((rx, ry)).right(1.0)); n = d.here; d.add(elm.Dot())
    d.add(elm.Resistor().up(1.6).at(n).label('R25 10k', loc='right')); d.add(elm.Vdd().label('+3V3'))
    d.add(elm.Button().right(2.2).at(n).label('SW2 RESET', loc='bottom')); d.add(elm.Line().down(0.4)); gnd(d, d.here)
    # kristal
    cx, cy = -26, -12
    d.add(T(1.8).left().at((cx, cy)).label('XIN'))
    d.add(elm.Line().at((cx, cy)).right(0.8)); k1 = d.here; d.add(elm.Dot())
    d.add(elm.Crystal().right(2.4).label('Y1 12 MHz', loc='top')); k2 = d.here; d.add(elm.Dot())
    d.add(elm.Line().right(0.8)); d.add(T(1.8).right().label('XO'))
    d.add(elm.Capacitor().down(1.6).at(k1).label('C51 15p', loc='left')); gnd(d, d.here)
    d.add(elm.Capacitor().down(1.6).at(k2).label('C52 15p', loc='right')); gnd(d, d.here)
    # SWD
    sx, sy = -12, -12
    for i, (t, lab) in enumerate([('SWCLK', 'J6-1'), ('GND', 'J6-2'), ('SWDIO', 'J6-3')]):
        p = (sx, sy - 0.9 * i)
        d.add(elm.Dot(open=True).at(p).label(lab, loc='left'))
        if t == 'GND':
            d.add(elm.Line().at(p).right(1.0)); gnd(d, d.here)
        else:
            d.add(elm.Line().at(p).right(1.0)); d.add(T(2.2).right().label(t))
    # ADuM3160 (dole levo)
    iso = d.add(elm.Ic(pins=[elm.IcPin(name='VBUS1', pin='1', side='left'), elm.IcPin(name='UD−', pin='6', side='left'),
                             elm.IcPin(name='UD+', pin='7', side='left'), elm.IcPin(name='GND1', pin='2,8', side='left'),
                             elm.IcPin(name='VBUS2', pin='16', side='right'), elm.IcPin(name='DD−', pin='11', side='right'),
                             elm.IcPin(name='DD+', pin='10', side='right'), elm.IcPin(name='GND2', pin='9,15', side='right')][::-1],
                       edgepadW=1.8, edgepadH=0.5, pinspacing=0.9,
                       label='U8 ADuM3160\nVDD1=PDEN=SPU (3,4,5), VDD2=PIN=SPD (14,12,13)', lblloc='bottom', lblofst=0.3)
               .right().at((-24, -20)))
    I = iso.absanchors
    for p, t in [('VBUS1', 'J5-1 VBUS'), ('UD−', 'J5-2 D−'), ('UD+', 'J5-3 D+')]:
        d.add(elm.Line().left(1.2).at(I[p])); d.add(elm.Dot(open=True).label(t, loc='left'))
    d.add(elm.Line().left(1.2).at(I['GND1'])); d.add(elm.Dot(open=True).label('GND_USB (J5-4, J5-5)', loc='left'))
    d.add(elm.Line().right(1.0).at(I['VBUS2'])); d.add(T(1.6).right().label('+5V'))
    d.add(elm.Line().right(1.0).at(I['DD−'])); d.add(T(2.2).right().label('DM_ISO'))
    d.add(elm.Line().right(1.0).at(I['DD+'])); d.add(T(2.2).right().label('DP_ISO'))
    d.add(elm.Line().right(1.0).at(I['GND2'])); d.add(elm.Line().down(0.4)); gnd(d, d.here)
    d.add(elm.Line().left(1.0).at(A['RUN'])); d.add(T(1.8).left().label('RUN'))
    d.add(elm.Resistor().left(2.4).at(A['USB_DP']).label('R21 27R', loc='top')); d.add(T(2.2).left().label('DP_ISO'))
    d.add(elm.Resistor().left(2.4).at(A['USB_DM']).label('R22 27R', loc='bottom')); d.add(T(2.2).left().label('DM_ISO'))
    d.add(elm.Line().left(1.0).at(A['XIN'])); d.add(T(1.8).left().label('XIN'))
    d.add(elm.Resistor().left(2.4).at(A['XOUT']).label('R26 1k', loc='bottom')); d.add(T(1.8).left().label('XO'))
    d.add(elm.Line().left(1.0).at(A['SWCLK'])); d.add(T(2.2).left().label('SWCLK'))
    d.add(elm.Line().left(1.0).at(A['SWDIO'])); d.add(T(2.2).left().label('SWDIO'))
    d.add(elm.Label().at((-28, -26)).label('Razdvajanje: C40–C45, C56, C57 100n (IOVDD, USB_VDD, ADC_AVDD), C48 1µ VREG_VIN · ADuM: C20 10µ, C21 1µ + C22 100n (VDD1), C23 1µ + C25 100n (VDD2), C24 100n + C26 1µ (VBUS2)\nUSB strana (J5, GND_USB) je galvanski odvojena od ostatka ploče kroz U8', halign='left'))
