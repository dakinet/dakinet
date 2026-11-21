import schemdraw
import schemdraw.elements as elm
schemdraw.config(fontsize=11, lw=1.3, font='DejaVu Sans')
ACC = '#b4441f'
def gnd(d, pt): d.add(elm.Ground().at(pt))

with schemdraw.Drawing(file='driver.svg', show=False) as d:
    d.config(unit=2)
    ref = d.add(elm.Ic(pins=[elm.IcPin(name='IN', side='left'),
                             elm.IcPin(name='OUT', side='right'),
                             elm.IcPin(name='GND', side='bottom')],
                       edgepadW=0.8, edgepadH=0.8, label='U3 REF3033', lblloc='top', lblofst=0.3).at((0, 0)).anchor('OUT'))
    d.add(elm.Line().left(1).at(ref.IN)); d.add(elm.Tag(width=1.4).left().label('+5V'))
    d.add(elm.Line().down(0.6).at(ref.GND)); gnd(d, d.here)
    y0 = ref.OUT[1]; x0 = ref.OUT[0]
    d.add(elm.Resistor().right(2.5).at(ref.OUT).label('R3  1k00', loc='top'))
    VS = d.here
    d.add(elm.Dot()); d.add(elm.Label().at((VS[0]-0.3, VS[1]+0.9)).label('VSET', color=ACC))
    # bus
    xs = {'R4': VS[0], 'C6': VS[0]+2.2, 'R5': VS[0]+5.0, 'Q5': VS[0]+13.5}
    xop = VS[0]+17.0
    d.add(elm.Line().right(xop-VS[0]).at(VS))
    for k in ('C6', 'R5', 'Q5'): d.add(elm.Dot().at((xs[k], y0)))
    d.add(elm.Resistor().down(3).at((xs['R4'], y0)).label('R4\n15k0', loc='bottom')); gnd(d, d.here)
    d.add(elm.Capacitor().down(3).at((xs['C6'], y0)).label('C6\n10n', loc='bottom')); gnd(d, d.here)
    d.add(elm.Resistor().down(4).at((xs['R5'], y0)).label('R5\n3k24', loc='bottom'))
    q2 = d.add(elm.NFet().right().reverse().anchor('drain').label('Q2 2N7002', loc='right'))
    gnd(d, q2.source)
    d.add(elm.Resistor().left(2.2).at(q2.gate).label('R19 100R', loc='bottom'))
    d.add(elm.Tag(width=2.9).left().label('NIVO  GP2'))
    d.add(elm.Line().down(1.2).at((xs['Q5'], y0)))
    q5 = d.add(elm.NFet().right().reverse().anchor('drain').label('Q5 2N7002', loc='right'))
    gnd(d, q5.source)
    d.add(elm.Line().left(0.9).at(q5.gate)); g5 = d.here; d.add(elm.Dot())
    d.add(elm.Line().left(1.3)); d.add(elm.Tag(width=2.9).left().label('/EN  GP3'))
    d.add(elm.Resistor().down(2).at(g5).label('R18\n100k', loc='bottom'))
    d.add(elm.Vdd().down().label('+3V3', loc='bottom'))
    # opamp, + on top
    op = d.add(elm.Opamp(leads=True).right().flip().anchor('in2').at((xop, y0)))
    d.add(elm.Label().at((op.center[0]+0.2, op.center[1]-2.4)).label('U4 OPA197\nV+ = +34 V (C13 100n, C58 1µ), V− = GND'))
    yo = op.out[1]
    d.add(elm.Resistor().right(3).at(op.out).label('R6  1k0', loc='top'))
    NB = d.here
    d.add(elm.Line().right(1.4)); d.add(elm.Dot().at(NB))
    q3 = d.add(elm.BjtNpn(circle=True).right().anchor('base').label('Q3 TIP122\n+ hladnjak', loc='right', ofst=(0.3, 0)))
    d.add(elm.Line().up(1).at(q3.collector)); d.add(elm.Vdd().label('+34V'))
    QE = q3.emitter
    d.add(elm.Line().down(1.6).at(QE)); NE = d.here; d.add(elm.Dot())
    r7 = d.add(elm.Resistor().down(2.4).at(NE).label('R7\n1R2 2512', loc='bottom'))
    LD = r7.end; d.add(elm.Dot().at(LD))
    q4 = d.add(elm.BjtNpn(circle=True).right().reverse().anchor('base').at((NE[0]-0.9, NE[1])).label('Q4\nBC547', loc='left', ofst=(0.0, 0)))
    d.add(elm.Line().at(q4.base).to(NE))
    d.add(elm.Wire('|-').at(q4.collector).to(NB))
    d.add(elm.Wire('|-').at(q4.emitter).to(LD))
    # feedback
    d.add(elm.Line().down(1.6).at(LD)); FT = d.here; d.add(elm.Dot())
    xfb = op.in1[0]-1.2
    r8 = d.add(elm.Resistor().left(FT[0]-xfb).at(FT).label('R8  91k0', loc='bottom'))
    FB = r8.end; d.add(elm.Dot().at(FB))
    d.add(elm.Line().up(0.9).at(FT)); d.add(elm.Capacitor().left(FT[0]-xfb).label('C7  100p', loc='top')); d.add(elm.Line().down(0.9))
    d.add(elm.Wire('|-').at(FB).to(op.in1))
    d.add(elm.Resistor().down(2.2).at(FB).label('R9\n10k0', loc='bottom')); gnd(d, d.here)
    # output
    d.add(elm.Line().right(1.5).at(FT))
    d.add(elm.Fuse().right(2.6).label('F2 PTC\n750 mA / 60 V', loc='top'))
    NO = d.here; d.add(elm.Dot())
    d.add(elm.Line().right(4.2)); d.add(elm.Dot(open=True).label('J2-1  LOOP OUT +', loc='right'))
    d.add(elm.Zener().down(2.4).at(NO).reverse().label('D2\nSMBJ36A', loc='bottom')); gnd(d, d.here)
    NV = (NO[0]+2.2, NO[1]); d.add(elm.Dot().at(NV))
    d.add(elm.Resistor().down(2.2).at(NV).label('R10\n100k', loc='bottom')); NVD = d.here; d.add(elm.Dot())
    d.add(elm.Resistor().down(1.8).label('R11\n10k0', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().left(1.3).at(NVD)); d.add(elm.Capacitor().down(1.8).label('C59\n1n', loc='bottom')); gnd(d, d.here)
    d.add(elm.Line().right(1.0).at(NVD)); d.add(elm.Tag(width=2.9).right().label('VLOOP  GP27'))
    # return terminal + loop in
    yb = NO[1]-7.2
    d.add(elm.Dot(open=True).at((NO[0]+4.2, yb+2.6)).label('J2-2  LOOP OUT −  →  R14 (list 3)', loc='right'))
    d.add(elm.Dot(open=True).at((NO[0]+4.2, yb+1.6)).label('J3-1  LOOP IN +  →  R12/R13 → VRET GP28', loc='right'))
    d.add(elm.Line(color='white').at((NO[0]+14, yb)).right(0.1)); d.add(elm.Label().at((ref.IN[0]-1, yb)).label('Pojačanje 1 + 91k/10k = 10,1   ·   VSET 3,094 V → 31,2 V (impuls)   ·   VSET 2,400 V → 24,2 V (osnovni)   ·   τ ≈ 0,94k·10n ≈ 9 µs   ·   Ilim ≈ 0,65 V / 1,2 Ω ≈ 540 mA   ·   Q3 TIP122 na hladnjaku (do ≈ 5 W)', halign='left'))
