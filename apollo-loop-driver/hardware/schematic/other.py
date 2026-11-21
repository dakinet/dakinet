import schemdraw
import schemdraw.elements as elm
schemdraw.config(fontsize=11, lw=1.3, font='DejaVu Sans')
def gnd(d, pt): d.add(elm.Ground().at(pt))
T = lambda w=2.9: elm.Tag(width=w)

# ---------------- LIST 1: NAPAJANJE ----------------
with schemdraw.Drawing(file='power.svg', show=False) as d:
    d.config(unit=2)
    j1 = d.add(elm.Dot(open=True).at((0, 0)).label('J1-1 +24 V (21–28 V)', loc='left'))
    d.add(elm.Fuse().right(2.4).label('F1  3 A', loc='top'))
    d.add(elm.Schottky().right(2.4).label('D3 SS34\n(obrnut polaritet)', loc='top'))
    V12 = d.here; d.add(elm.Dot()); d.add(elm.Label().at((V12[0], V12[1]+0.9)).label('+24V', color='#b4441f'))
    d.add(elm.Dot(open=True).at((0, -4)).label('J1-2 GND', loc='left')); d.add(elm.Line().right(1)); gnd(d, d.here)
    d.add(elm.Capacitor(polar=True).down(2.4).at(V12).label('C1\n100µ/50V', loc='bottom')); gnd(d, d.here)
    # boost: L1 from +12V to SW
    d.add(elm.Line().right(2).at(V12)); NL = d.here; d.add(elm.Dot())
    d.add(elm.Inductor2(loops=3).right(3).label('L1 (na modulu)', loc='top'))
    SW = d.here; d.add(elm.Dot())
    d.add(elm.Schottky().right(3).label('D1 (na modulu)', loc='top'))
    V34 = d.here; d.add(elm.Dot()); d.add(elm.Label().at((V34[0], V34[1]+0.9)).label('+34V', color='#b4441f'))
    ic = d.add(elm.Ic(pins=[elm.IcPin(name='VIN', side='left', slot='1/2'), elm.IcPin(name='EN', side='left', slot='2/2'),
                            elm.IcPin(name='SW', side='top'), elm.IcPin(name='FB', side='right'), elm.IcPin(name='GND', side='bottom')],
                      edgepadW=1.2, edgepadH=0.8, label='U1 boost modul\n≥20 W (npr. XL6019)', lblloc='center').anchor('SW').at((SW[0], SW[1]-1.6)))
    d.add(elm.Line().at(SW).to(ic.SW))
    d.add(elm.Wire('|-').at(NL).to(ic.VIN))
    d.add(elm.Line().at(ic.EN).to((NL[0], ic.EN[1]))); d.add(elm.Dot())
    d.add(elm.Line().down(0.6).at(ic.GND)); gnd(d, d.here)
    for i, (lbl) in enumerate(['C3\n100µ/50V', 'C4\n100µ/50V', 'C5\n1µ/50V']):
        x = V34[0] + 2.6*i
        if i: d.add(elm.Line().at((x-2.6, V34[1])).right(2.6)); d.add(elm.Dot().at((x, V34[1])))
        d.add(elm.Capacitor(polar=(i < 2)).down(2.4).at((x, V34[1])).label(lbl, loc='bottom')); gnd(d, d.here)
    xr = V34[0] + 7.6
    d.add(elm.Line().at((xr-2.4, V34[1])).right(2.4)); d.add(elm.Dot())
    d.add(elm.Line().right(1.6)); d.add(T(2.2).right().label('+34V'))
    d.add(elm.Resistor().down(2.6).at((xr, V34[1])).label('R2\n57k6', loc='bottom'))
    NFBp = d.here; d.add(elm.Dot())
    d.add(elm.Resistor().down(2.0).label('R1\n2k2', loc='bottom')); gnd(d, d.here)
    d.add(elm.Wire('-|').at(ic.FB).to((xr-1.0, NFBp[1]))); d.add(elm.Line().to(NFBp))
    # 5 V regulator
    y5 = -8.5
    d.add(elm.Line().at(V12).down(-y5 - 0.0 + 0)) if False else None
    d.add(elm.Dot().at((NL[0], ic.VIN[1]))); d.add(elm.Wire('|-').at((NL[0], ic.VIN[1])).to((NL[0]+1.5, y5)))
    reg = d.add(elm.Ic(pins=[elm.IcPin(name='IN', side='left'), elm.IcPin(name='OUT', side='right'), elm.IcPin(name='GND', side='bottom')],
                       edgepadW=0.9, edgepadH=0.6, label='U2 R-78E5.0-0.5', lblloc='top', lblofst=0.2).anchor('IN').at((NL[0]+1.5, y5)))
    d.add(elm.Line().down(0.6).at(reg.GND)); gnd(d, d.here)
    d.add(elm.Line().right(1.2).at(reg.OUT)); N5 = d.here; d.add(elm.Dot())
    d.add(elm.Capacitor().down(2).at(N5).label('C10\n10µ', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(2).at(N5)); d.add(T(1.6).right().label('+5V'))
    d.add(elm.Label().at((0, -13)).label('Boost modul podešen trimerom na 34,0 V (za 500 mA petlje ≈ 17 W)  ·  R-78E5.0 (prekidački) napaja Pico i REF3033  ·  ulaz kao centrala: 24 V', halign='left'))

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
    d.add(elm.Resistor().right(IA[0]-NM[0]-1.2).label('R16  51k', loc='bottom'))
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
    d.add(elm.Line().right(1.5).at(NV)); d.add(T(3.2).right().label('VRET  GP28'))
    d.add(elm.Label().at((0, -13.2)).label('U5, U6 napajanje +3V3, 100n uz svaki čip  ·  20 mA · 1 Ω · 6,1 = 122 mV, opseg do ≈ 540 mA  ·  prag = struja mirovanja + 10 mA (PWM 100 kHz kroz R20/C9)', halign='left'))

# ---------------- LIST 4: PICO ----------------
with schemdraw.Drawing(file='pico.svg', show=False) as d:
    d.config(unit=2)
    pins = [elm.IcPin(name='GND', pin='38', side='left'), elm.IcPin(name='USB', side='left'),
            elm.IcPin(name='VSYS', pin='39', side='left'), elm.IcPin(name='3V3(OUT)', pin='36', side='left'),
            elm.IcPin(name='ADC_VREF', pin='35', side='left'),
            elm.IcPin(name='GP2', pin='4', side='right'), elm.IcPin(name='GP3', pin='5', side='right'),
            elm.IcPin(name='GP4', pin='6', side='right'), elm.IcPin(name='GP16', pin='21', side='right'),
            elm.IcPin(name='GP26/ADC0', pin='31', side='right'), elm.IcPin(name='GP27/ADC1', pin='32', side='right'),
            elm.IcPin(name='GP28/ADC2', pin='34', side='right')]
    ic = d.add(elm.Ic(pins=pins, pinspacing=1.0, edgepadW=2.4, edgepadH=0.6, label='U7  Raspberry Pi Pico', lblloc='top', lblofst=0.3).at((0, 0)))
    tags = {'GP2': 'NIVO', 'GP3': '/EN', 'GP4': 'BIT', 'GP16': 'PRAG', 'GP26/ADC0': 'IAMP', 'GP27/ADC1': 'VLOOP', 'GP28/ADC2': 'VRET'}
    A = ic.absanchors
    for p, t in tags.items():
        d.add(elm.Line().right(1.2).at(A[p])); d.add(T(2.0).right().label(t))
    d.add(elm.Line().left(1.6).at(A['ADC_VREF'])); d.add(elm.Capacitor().left(1.6).label('C11 100n', loc='top')); d.add(elm.Line().down(0.3)); gnd(d, d.here)
    d.add(elm.Line().left(1.2).at(A['3V3(OUT)'])); d.add(T(1.8).left().label('+3V3'))
    d.add(elm.Line().left(1.2).at(A['VSYS'])); d.add(elm.Schottky().left(2.2).reverse().label('D4 SS14', loc='top')); d.add(T(1.6).left().label('+5V'))
    d.add(elm.Line().left(1.2).at(A['GND'])); d.add(elm.Line().down(0.4)); gnd(d, d.here)
    d.add(elm.Line().left(8.5).at(A['USB'])); P = d.here
    iso = d.add(elm.Ic(pins=[elm.IcPin(name='PICO', side='right'), elm.IcPin(name='PC', side='left')], edgepadW=1.0, edgepadH=0.5,
                       label='U8 ADuM3160 USB izolator', lblloc='bottom', lblofst=0.2).right().anchor('PICO').at(P))
    d.add(elm.Line().left(1.2).at(iso.PC)); d.add(elm.Dot(open=True).label('USB → PC', loc='left'))
    d.add(elm.Label().at((A['USB'][0]-13, A['USB'][1]-3.2)).label('GND Pico-a = GND petlje (izolovano od PC-a kroz U8)  ·  bez Pico-a R18 drži /EN na 3V3 → petlja ugašena', halign='left'))
