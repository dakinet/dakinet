"""Šema LoopNet 1IN v0.1 (schemdraw). Pokretanje: python3 loopnet_1in.py -> linija.svg/png, mcu.svg/png
Oznake i mreže su iste kao u ../pcb/make_pcb.py (izvor istine za pločicu)."""
import schemdraw
import schemdraw.elements as elm

schemdraw.config(fontsize=11, lw=1.3, font='DejaVu Sans')
ACC = '#b4441f'


def gnd(d, pt):
    d.add(elm.Ground().at(pt))


def oznaka(d, pt, txt):
    d.add(elm.Label().at((pt[0], pt[1] + 0.55)).label(txt, color=ACC))


def T(w=2.4):
    return elm.Tag(width=w)


# ============================ LIST 1: linija, most, izvor struje, 3,3 V, prijem, odgovor
def list1(fname):
    with schemdraw.Drawing(file=fname, show=False) as d:
        d.config(unit=2)
        # --- stezaljke
        d.add(elm.Dot(open=True).at((0, 0)).label('J1-1 / J2-1  LA', loc='left'))
        d.add(elm.Dot(open=True).at((0, -4)).label('J1-2 / J2-2  LB', loc='left'))
        d.add(elm.Line().right(2).at((0, 0))); LA = d.here; d.add(elm.Dot()); oznaka(d, LA, 'LA')
        d.add(elm.Line().right(2).at((0, -4))); LB = d.here; d.add(elm.Dot()); oznaka(d, (LB[0], LB[1] - 1.1), 'LB')
        # --- most 2x BAV99: gornje diode ka VP, donje ka GND
        xa, xb = 4.0, 6.5
        yvp, ygnd = 3.0, -7.0
        d.add(elm.Line().at(LA).to((xa, 0))); d.add(elm.Dot())
        d.add(elm.Line().at(LB).to((xb, -4))); d.add(elm.Dot())
        d.add(elm.Diode().at((xa, 0)).to((xa, yvp)).label('D1b', loc='left'))
        d.add(elm.Diode().at((xa, ygnd)).to((xa, 0)).label('D1a', loc='left'))
        d.add(elm.Diode().at((xb, -4)).to((xb, yvp)).label('D2b', loc='right'))
        d.add(elm.Diode().at((xb, ygnd)).to((xb, -4)).label('D2a', loc='right'))
        d.add(elm.Label().at((5.25, -8.3)).label('D1, D2 = BAV99 (SOT-23)\n1 = anoda, 2 = katoda, 3 = sredina'))
        d.add(elm.Line().at((xa, yvp)).to((xb, yvp)))
        d.add(elm.Line().at((xa, ygnd)).to((xb, ygnd)))
        VP0 = (xb, yvp)
        d.add(elm.Line().right(2.0).at(VP0)); VP1 = d.here; d.add(elm.Dot()); oznaka(d, VP1, 'VP')
        d.add(elm.Line().right(2.0).at((xb, ygnd))); G1 = d.here; gnd(d, G1)
        d.add(elm.Zener().at(G1).to(VP1).label('D3 SMAJ40A\n(TVS 40 V)', loc='left'))
        # --- izvor konstantne struje
        xq = VP1[0] + 6.0
        d.add(elm.Line().at(VP1).to((xq, yvp)))
        q1 = d.add(elm.BjtNpn(circle=True).anchor('collector').at((xq, yvp - 0.8)).label('Q1\nMMBT5551', loc='right', ofst=(0.1, 0.4)))
        d.add(elm.Line().at((xq, yvp)).to(q1.collector))
        xr1 = xq - 3.0
        d.add(elm.Dot().at((xr1, yvp)))
        r1 = d.add(elm.Resistor().at((xr1, yvp)).to((xr1, q1.base[1])).label('R1\n2M2', loc='bottom'))
        QB = (xr1, q1.base[1]); d.add(elm.Line().at(QB).to(q1.base)); d.add(elm.Dot().at(QB))
        d.add(elm.Line().down(0.8).at(q1.emitter)); QE = d.here; d.add(elm.Dot())
        r2 = d.add(elm.Resistor().down(3.0).at(QE).label('R2\n3k3', loc='bottom'))
        VC = r2.end; d.add(elm.Dot().at(VC))
        q2 = d.add(elm.BjtNpn(circle=True).left().flip().anchor('base').at((QE[0] - 1.4, QE[1])).label('Q2\nMMBT3904', loc='left', ofst=(-0.2, -0.9)))
        d.add(elm.Line().at(q2.base).to(QE))
        xc = q2.collector[0]
        d.add(elm.Line().at(q2.collector).to((xc, QB[1]))); d.add(elm.Dot().at((xc, QB[1])))
        d.add(elm.Wire('|-').at(q2.emitter).to(VC))
        d.add(elm.Label().at((xq + 2.0, QE[1] - 0.6)).label('I = Vbe(Q2)/R2 + VP/R1\n≈ 167 µA + 7…14 µA', halign='left'))
        # Zener i C1
        d.add(elm.Line().right(2.2).at(VC)); VC1 = d.here; d.add(elm.Dot()); oznaka(d, (VC1[0] + 1.2, VC1[1]), 'VC ≈ 10 V')
        d.add(elm.Zener().at((VC1[0], VC1[1] - 2.6)).to(VC1).label('D4\nBZT52C10', loc='left'))
        gnd(d, (VC1[0], VC1[1] - 2.6))
        d.add(elm.Line().right(2.4).at(VC1)); VC2 = d.here; d.add(elm.Dot())
        d.add(elm.Capacitor().down(2.6).at(VC2).label('C1\n10µ/25V', loc='bottom')); gnd(d, d.here)
        # LDO
        ldo = d.add(elm.Ic(pins=[elm.IcPin(name='IN', pin='1', side='left', slot='1/2'),
                                 elm.IcPin(name='EN', pin='2', side='left', slot='2/2'),
                                 elm.IcPin(name='OUT', pin='6', side='right'),
                                 elm.IcPin(name='GND', pin='3,4,5,EP', side='bottom')],
                           edgepadW=1.2, edgepadH=0.7, label='U1 TPS7B8133DRV', lblloc='top', lblofst=0.2)
                    .right().anchor('IN').at((VC2[0] + 2.2, VC2[1])))
        d.add(elm.Line().at(VC2).to(ldo.IN))
        d.add(elm.Wire('-|').at(ldo.EN).to((VC2[0] + 1.0, VC2[1]))); d.add(elm.Dot().at((VC2[0] + 1.0, VC2[1])))
        d.add(elm.Line().down(0.5).at(ldo.GND)); gnd(d, d.here)
        d.add(elm.Line().right(1.6).at(ldo.OUT)); V3 = d.here; d.add(elm.Dot()); oznaka(d, V3, 'VDD 3,3 V')
        d.add(elm.Capacitor().down(2.2).at(V3).label('C2\n10µ', loc='bottom')); gnd(d, d.here)
        d.add(elm.Line().right(2.0).at(V3)); d.add(elm.Dot())
        d.add(elm.Capacitor().down(2.2).label('C3\n100n\n(uz U2)', loc='bottom')); gnd(d, d.here)
        d.add(elm.Line().right(1.2).at((V3[0] + 2.0, V3[1]))); d.add(T(1.8).right().label('VDD'))

        # --- prijem: delitelj sa obe žice PRE mosta
        yr = -12.0
        d.add(T(1.6).left().at((0.5, yr)).label('LA'))
        d.add(elm.Resistor().right(3.2).at((0.5, yr)).label('R3  4M7', loc='top'))
        NL = d.here; d.add(elm.Dot()); oznaka(d, NL, 'LINE')
        d.add(T(1.6).left().at((0.5, yr - 2.4)).label('LB'))
        d.add(elm.Resistor().right(3.2).at((0.5, yr - 2.4)).label('R4  4M7', loc='bottom'))
        d.add(elm.Line().to(NL))
        d.add(elm.Line().right(2.0).at(NL)); NL2 = d.here; d.add(elm.Dot())
        d.add(elm.Resistor().down(2.6).at(NL2).label('R5\n330k', loc='bottom')); gnd(d, d.here)
        d.add(elm.Line().right(2.0).at(NL2)); d.add(T(3.4).right().label('PA7  AC0+ / AIN7'))
        d.add(elm.Label().at((0.2, yr - 4.6)).label(
            'LINE ≈ (U_linije − 2·Vf) · 0,058   (31 V → 1,75 V;  24 V → 1,34 V)\n'
            'Thevenin ≈ 290 kΩ, τ ≈ 3 µs.  Prag: AC0− = PA6 (C4 10 nF, puni ga DAC0 svakih 10 ms)\n'
            '= osnovni nivo (ADC na PA7) + 3,5 V', halign='left'))

        # --- odgovor 10 mA
        xs = 22.0
        d.add(T(1.6).left().at((xs, yr + 1.6)).label('VP'))
        d.add(elm.Line().right(3.0).at((xs, yr + 1.6))); cq = d.here
        q3 = d.add(elm.BjtNpn(circle=True).anchor('collector').at((cq[0], cq[1] - 0.8)).label('Q3\nBCX56-16', loc='right', ofst=(0.3, 0.6)))
        d.add(elm.Line().at(cq).to(q3.collector))
        d.add(elm.Line().down(0.6).at(q3.emitter))
        r6 = d.add(elm.Resistor().down(2.2).label('R6\n240', loc='bottom')); gnd(d, r6.end)
        d.add(elm.Line().left(1.4).at(q3.base)); QSB = d.here; d.add(elm.Dot())
        d.add(elm.Resistor().left(2.6).label('R7  1k', loc='top'))
        d.add(T(2.6).left().label('PB0 SINK'))
        d.add(elm.Resistor().down(2.2).at(QSB).label('R8\n100k', loc='top')); gnd(d, d.here)
        d.add(elm.Label().at((xs - 1.2, yr - 5.4)).label('I ≈ (3,3 − 0,1 − 0,7) V / 240 Ω ≈ 10 mA\nsamo za vreme odgovora (≤ 100 µs)', halign='left'))


# ============================ LIST 2: MCU, ulaz, LED, taster, UPDI
def list2(fname):
    with schemdraw.Drawing(file=fname, show=False) as d:
        d.config(unit=2)
        L = [('PA6', '7', 'VTHR (DAC0 / AC0−)'), ('PA3', '2', 'IN_DRV'), ('PA4', '5', 'IN_SENSE (AIN4)'),
             ('PA7', '8', 'LINE (AC0+ / AIN7)'), ('PA0', '19', 'UPDI')]
        R = [('PB0', '14', 'SINK'), ('PB1', '13', 'LED'), ('PB2', '12', 'BTN'), ('PA5', '6', 'AC0 OUT (n.c.)')]
        pins = [elm.IcPin(name=n, pin=p, side='left', slot='%d/%d' % (i + 1, len(L))) for i, (n, p, _) in enumerate(L)]
        pins += [elm.IcPin(name=n, pin=p, side='right', slot='%d/%d' % (i + 1, len(R))) for i, (n, p, _) in enumerate(R)]
        pins += [elm.IcPin(name='VDD', pin='4', side='top'), elm.IcPin(name='GND', pin='3, EP', side='bottom')]
        u = d.add(elm.Ic(pins=pins, edgepadW=2.6, edgepadH=1.0, pinspacing=1.5).at((0, 0)))
        d.add(elm.Label().at((u.VDD[0] + 3.2, u.VDD[1] + 0.7)).label('U2 ATtiny1616-MNR (VQFN-20)'))
        d.add(elm.Line().up(0.8).at(u.VDD)); d.add(elm.Vdd().label('VDD'))
        d.add(elm.Line().down(0.6).at(u.GND)); gnd(d, d.here)
        for n, p, t in L:
            d.add(elm.Line().left(1.0).at(getattr(u, n)))
            if n == 'PA6':
                k = d.here; d.add(elm.Dot())
                d.add(elm.Capacitor().down(1.4).at(k).label('C4\n10n', loc='bottom')); gnd(d, d.here)
                d.add(elm.Line().left(1.6).at(k))
            d.add(T(4.6).left().label(t))
        for n, p, t in R:
            d.add(elm.Line().right(1.0).at(getattr(u, n)))
            d.add(T(3.6).right().label(t))
        d.add(elm.Label().at((-1.5, -7.6)).label('PA1, PA2, PB3–PB5, PC0–PC3: nepovezani (ulaz sa pull-up)'))

        # ulaz EOL
        x0, y0 = 14.0, 2.0
        d.add(T(2.4).left().at((x0, y0)).label('IN_DRV'))
        d.add(elm.Resistor().right(3).at((x0, y0)).label('R9  2k2', loc='top')); INP = d.here; d.add(elm.Dot()); oznaka(d, INP, 'INP')
        d.add(elm.Line().right(3.0)); d.add(elm.Dot(open=True).label('J3-1  ULAZ +', loc='right'))
        d.add(elm.Resistor().down(2.4).at(INP).label('R10\n1k', loc='bottom')); ns = d.here; d.add(elm.Dot())
        d.add(elm.Capacitor().down(1.8).at(ns).label('C5\n1n', loc='bottom')); gnd(d, d.here)
        d.add(elm.Line().right(1.2).at(ns)); d.add(T(2.8).right().label('IN_SENSE'))
        d.add(elm.Dot(open=True).at((INP[0] + 3.0, y0 - 5.4)).label('J3-2  ULAZ − (GND)', loc='right')); gnd(d, (INP[0] + 3.0, y0 - 5.4))
        d.add(elm.Label().at((x0 - 1.5, y0 - 7.4)).label(
            'Polje: EOL 2k2 serijski + 2k2 paralelno kontaktu\n'
            'U/VDD: < 0,18 kratak spoj · 0,18–0,58 zatvoren (0,50)\n'
            '0,58–0,83 otvoren (0,67) · > 0,83 prekid\n'
            'IN_DRV = 1 samo ~50 µs svakih 10 ms', halign='left'))
        # LED, taster, UPDI
        x1, y1 = 14.0, -11.5
        d.add(T(1.8).left().at((x1, y1)).label('LED'))
        d.add(elm.Resistor().right(2.6).at((x1, y1)).label('R11  1k', loc='top'))
        d.add(elm.LED().down(2.0).label('D5', loc='right')); gnd(d, d.here)
        d.add(T(1.8).left().at((x1 + 6.5, y1)).label('BTN'))
        d.add(elm.Line().right(1.0).at((x1 + 6.5, y1)))
        d.add(elm.Button().down(2.0).label('SW1\nTS-1187A', loc='right')); gnd(d, d.here)
        d.add(elm.Label().at((x1 + 5.0, y1 + 1.0)).label('interni pull-up', halign='left'))
        d.add(elm.Label().at((x1 - 1.5, y1 - 4.2)).label('J4 UPDI (1,27 mm): 1 VDD, 2 UPDI (PA0), 3 GND', halign='left'))


if __name__ == '__main__':
    for f, ime in ((list1, 'linija'), (list2, 'mcu')):
        schemdraw.use('svg')
        f(ime + '.svg')
        schemdraw.use('matplotlib')
        f(ime + '.png')
