"""Kompletna šema LoopNet 1IN v0.1 na jednom listu, svi elementi povezani žicama.
Pokretanje: python3 kompletna.py -> kompletna.svg, kompletna.png
Mreže i oznake su iste kao u ../pcb/make_pcb.py (izvor istine)."""
import schemdraw
import schemdraw.elements as elm

schemdraw.config(fontsize=10, lw=1.2, font='DejaVu Sans')
ACC = '#b4441f'


def crtaj(fname):
    with schemdraw.Drawing(file=fname, show=False) as d:
        d.config(unit=2)
        L = lambda a, b: d.add(elm.Line().at(a).to(b))
        dot = lambda p: d.add(elm.Dot().at(p))
        txt = lambda p, t, **k: d.add(elm.Label().at(p).label(t, **k))
        mreza = lambda p, t: d.add(elm.Label().at(p).label(t, color=ACC, fontsize=9))

        YG, YVP, YVC = 0.0, 12.0, 5.0          # GND sabirnica, VP sabirnica, VC/VDD nivo
        YLA, YLB = 8.0, 5.0                     # žice linije kod stezaljki
        YTA, YTB = 17.0, 18.0                   # LA/LB vod do delitelja prijema (iznad svega)

        # ---------------- stezaljke J1 (ulaz) i J2 (izlaz), prolazno
        d.add(elm.Dot(open=True).at((0, YLA)).label('J1-1', loc='left'))
        d.add(elm.Dot(open=True).at((0, YLB)).label('J1-2', loc='left'))
        d.add(elm.Dot(open=True).at((0, YLA + 1.4)).label('J2-1', loc='left'))
        d.add(elm.Dot(open=True).at((0, YLB - 1.4)).label('J2-2', loc='left'))
        L((0, YLA + 1.4), (0.8, YLA + 1.4)); L((0.8, YLA + 1.4), (0.8, YLA)); dot((0.8, YLA))
        L((0, YLB - 1.4), (0.8, YLB - 1.4)); L((0.8, YLB - 1.4), (0.8, YLB)); dot((0.8, YLB))
        txt((-1.6, YLA + 3.0), 'LINIJA\n(polaritet nebitan)', fontsize=9)
        xa, xb = 6.0, 8.0
        L((0, YLA), (xa, YLA)); L((0, YLB), (xb, YLB))
        mreza((3.6, YLA + 0.5), 'LA'); mreza((4.6, YLB - 0.55), 'LB')
        # most 2x BAV99
        d.add(elm.Diode().at((xa, YLA)).to((xa, YVP)))
        d.add(elm.Diode().at((xa, YG)).to((xa, YLA)))
        d.add(elm.Diode().at((xb, YLB)).to((xb, YVP)))
        d.add(elm.Diode().at((xb, YG)).to((xb, YLB)))
        dot((xa, YLA)); dot((xb, YLB))
        for x, y, t, h in ((xa - 0.35, (YLA + YVP) / 2, 'D1\n3→2', 'right'), (xa - 0.35, YLA / 2, 'D1\n1→3', 'right'),
                           (xb + 0.35, (YLB + YVP) / 2, 'D2\n3→2', 'left'), (xb + 0.35, YLB / 2, 'D2\n1→3', 'left')):
            txt((x, y), t, fontsize=9, halign=h)
        txt((7.0, -1.9), 'D1, D2 = BAV99 (SOT-23): 1 anoda, 2 katoda, 3 sredina\nQ1, Q2, Q3 (SOT-23): 1 B, 2 E, 3 C', fontsize=9)
        # LA/LB gore, ka delitelju prijema
        L((2.6, YLA), (2.6, YTA)); dot((2.6, YLA))
        L((1.6, YLB), (1.6, YTB)); dot((1.6, YLB))

        # ---------------- sabirnice VP i GND
        xvp_end = 20.5
        L((xa, YVP), (xvp_end, YVP)); dot((xb, YVP))
        mreza((15.0, YVP + 0.5), 'VP')
        xg_end = 58.0
        L((xa, YG), (xg_end, YG)); dot((xb, YG))
        d.add(elm.Ground().at((16.0, YG)))
        mreza((14.0, YG - 0.6), 'GND')

        # TVS
        xt = 9.4
        d.add(elm.Zener().at((xt, YG)).to((xt, YVP)).label('D3\nSMAJ40A', loc='bottom'))
        dot((xt, YVP)); dot((xt, YG))

        # ---------------- izvor konstantne struje
        xr1, xq1 = 17.0, 20.5
        d.add(elm.Resistor().at((xr1, YVP)).to((xr1, 9.0)).label('R1\n1M', loc='bottom')); dot((xr1, YVP))
        q1 = d.add(elm.BjtNpn(circle=True).right().anchor('base').at((xq1 - 0.75, 9.0)).label('Q1 MMBT5551', loc='right', ofst=(0.1, 0.5)))
        L((xr1, 9.0), q1.base)
        L(q1.collector, (q1.collector[0], YVP)); dot((q1.collector[0], YVP))
        QE = (q1.emitter[0], 7.3)
        L(q1.emitter, QE); dot(QE)
        d.add(elm.Resistor().at(QE).to((QE[0], YVC)).label('R2\n3k3', loc='bottom'))
        VC = (QE[0], YVC); dot(VC)
        q2 = d.add(elm.BjtNpn(circle=True).left().flip().anchor('base').at((QE[0] - 1.4, QE[1])).label('Q2\nMMBT3904', loc='left', ofst=(-0.1, -0.7)))
        L(q2.base, QE)
        L(q2.collector, (q2.collector[0], 9.0)); dot((q2.collector[0], 9.0))
        L(q2.emitter, (q2.emitter[0], YVC)); L((q2.emitter[0], YVC), VC)
        txt((q1.collector[0] + 0.6, 10.9), 'I ≈ Vbe/R2 + VP/R1 ≈ 190 µA', fontsize=9, halign='left')

        # VC: Zener, C1, LDO
        xz, xc1, xu = 23.5, 25.5, 28.5
        L(VC, (xu, YVC))
        mreza((22.0, YVC + 0.5), 'VC ≈ 10 V')
        d.add(elm.Zener().at((xz, YG)).to((xz, YVC)).label('D4\nBZT52C10', loc='top')); dot((xz, YVC)); dot((xz, YG))
        d.add(elm.Capacitor().at((xc1, YVC)).to((xc1, YG)).label('C1\n10µ/25V', loc='bottom')); dot((xc1, YVC)); dot((xc1, YG))
        u1 = d.add(elm.Ic(pins=[elm.IcPin(name='VIN', pin='2', side='left'), elm.IcPin(name='VOUT', pin='3', side='right'),
                                elm.IcPin(name='GND', pin='1', side='bottom')],
                          edgepadW=0.8, edgepadH=0.5, label='U1\nHT7533-1', lblloc='top', lblofst=0.15)
                   .right().anchor('VIN').at((xu + 0.6, YVC)))
        L((xu, YVC), u1.VIN)
        L(u1.GND, (u1.GND[0], YG)); dot((u1.GND[0], YG))
        xvdd = u1.VOUT[0] + 1.0
        L(u1.VOUT, (xvdd, YVC))
        # C2, C3 na VDD
        xc2, xc3 = xvdd + 0.8, xvdd + 2.6
        L((xvdd, YVC), (xc3, YVC))
        d.add(elm.Capacitor().at((xc2, YVC)).to((xc2, YG)).label('C2\n10µ', loc='bottom')); dot((xc2, YVC)); dot((xc2, YG))
        d.add(elm.Capacitor().at((xc3, YVC)).to((xc3, YG)).label('C3\n100n', loc='bottom')); dot((xc3, YG))
        mreza((xc2 - 0.6, YVC + 0.5), 'VDD 3,3 V')

        # ---------------- odgovor 10 mA (Q3 na kraju VP sabirnice)
        xq3 = 13.0
        q3 = d.add(elm.BjtNpn(circle=True).right().anchor('collector').at((xq3, YVP - 1.0)).label('Q3\nMMBT5551', loc='right', ofst=(0.1, 0.5)))
        L((xq3, YVP), q3.collector); dot((xq3, YVP))
        d.add(elm.Resistor().at(q3.emitter).to((q3.emitter[0], YG)).label('R6\n270', loc='bottom')); dot((q3.emitter[0], YG))
        QSB = (q3.base[0] - 0.9, q3.base[1])
        L(q3.base, QSB); dot(QSB)
        d.add(elm.Resistor().at(QSB).to((QSB[0], YG + 3.8)).label('R8\n100k', loc='top'))
        L((QSB[0], YG + 3.8), (QSB[0], YG)); dot((QSB[0], YG))

        # ---------------- MCU
        R = [('PB0', '14'), ('PB1', '13'), ('PB2', '12'), ('PA3', '2'), ('PA4', '5'), ('PA5', '6'), ('PA2', '1')]
        Lp = [('PA7', '8'), ('PA6', '7'), ('PA0', '19'), ('VDD', '4')]
        pins = [elm.IcPin(name=n, pin=p, side='right', slot='%d/%d' % (len(R) - i, len(R))) for i, (n, p) in enumerate(R)]
        pins += [elm.IcPin(name=n, pin=p, side='left', slot='%d/%d' % (len(Lp) - i, len(Lp))) for i, (n, p) in enumerate(Lp)]
        pins += [elm.IcPin(name='GND', pin='3, EP', side='bottom')]
        u2 = d.add(elm.Ic(pins=pins, edgepadW=2.2, edgepadH=0.8, pinspacing=1.2,
                          label='U2  ATtiny1616-MNR', lblloc='top', lblofst=0.2).right().anchor('GND').at((44.0, YG + 1.0)))
        L(u2.GND, (u2.GND[0], YG)); dot((u2.GND[0], YG))
        # VDD u MCU
        L((xc3, YVC), (xc3 + 1.0, YVC)); dot((xc3, YVC))
        L((xc3 + 1.0, YVC), (xc3 + 1.0, u2.VDD[1])); L((xc3 + 1.0, u2.VDD[1]), u2.VDD)
        # baza Q3 <- R7 <- PB0 (iznad VP sabirnice)
        d.add(elm.Resistor().at(QSB).to((QSB[0], YVP + 3.0)).label('R7\n1k', loc='bottom'))
        L((QSB[0], YVP + 3.0), (u2.PB0[0] + 1.2, YVP + 3.0))
        L(u2.PB0, (u2.PB0[0] + 1.2, u2.PB0[1])); L((u2.PB0[0] + 1.2, u2.PB0[1]), (u2.PB0[0] + 1.2, YVP + 3.0))
        mreza((24.0, YVP + 3.5), 'SINK')

        # prijem: R3 (LA), R4 (LB) -> LINE -> PA7, R5 na GND; C4 na PA6
        xr3, xr4 = 37.0, 38.6
        L((2.6, YTA), (xr3, YTA)); L((1.6, YTB), (xr4, YTB))
        mreza((20.0, YTA + 0.45), 'LA'); mreza((20.0, YTB + 0.45), 'LB')
        yline = u2.PA7[1]
        d.add(elm.Resistor().at((xr3, YTA)).to((xr3, yline + 1.2)).label('R3\n4M7', loc='top'))
        d.add(elm.Resistor().at((xr4, YTB)).to((xr4, yline + 1.2)).label('R4\n4M7', loc='bottom'))
        L((xr3, yline + 1.2), (xr3, yline)); L((xr4, yline + 1.2), (xr4, yline))
        L((xr3, yline), u2.PA7); dot((xr4, yline))
        xr5 = xr3 - 1.6
        L((xr5, yline), (xr3, yline)); dot((xr3, yline))
        d.add(elm.Resistor().at((xr5, yline)).to((xr5, yline - 1.3)).label('R5 330k', loc='bottom'))
        d.add(elm.Ground().at((xr5, yline - 1.3)))
        mreza((xr4 + 0.3, yline + 0.4), 'LINE')
        xc4 = u2.PA0[0] - 3.4
        L(u2.PA6, (xc4, u2.PA6[1])); dot((xc4, u2.PA6[1]))
        d.add(elm.Capacitor().at((xc4, u2.PA6[1])).to((xc4, u2.PA6[1] - 1.1)).label('C4\n10n', loc='bottom'))
        d.add(elm.Ground().at((xc4, u2.PA6[1] - 1.1)))
        # R5 do GND: kroz levo, preko VDD nivoa ne prelazi (ide do VC visine pa na GND)
        # UPDI J4
        xj = u2.PA0[0] - 2.4
        L(u2.PA0, (xj, u2.PA0[1])); d.add(elm.Dot(open=True).at((xj, u2.PA0[1])).label('J4-2 UPDI', loc='top'))
        # J4-1 na VDD, J4-3 na GND
        yv = u2.VDD[1]
        dot((xj, yv)); L((xj, yv), (xj, yv - 0.7))
        d.add(elm.Dot(open=True).at((xj, yv - 0.7)).label('J4-1 VDD', loc='left'))
        d.add(elm.Dot(open=True).at((xj + 1.2, yv - 0.7)).label('J4-3 GND', loc='right'))
        L((xj + 1.2, yv - 0.7), (xj + 1.2, YG)); dot((xj + 1.2, YG))

        # PA5 (AC0 OUT) -> PA2 (asinhroni prekid)
        xa5 = u2.PA5[0] + 1.0
        L(u2.PA5, (xa5, u2.PA5[1])); L((xa5, u2.PA5[1]), (xa5, u2.PA2[1])); L((xa5, u2.PA2[1]), u2.PA2)
        txt((xa5 + 0.3, (u2.PA5[1] + u2.PA2[1]) / 2), 'AC_OUT', fontsize=8, halign='left', color=ACC)

        # LED (PB1)
        xl = u2.PB1[0] + 3.0
        d.add(elm.Resistor().at(u2.PB1).to((xl + 2.0, u2.PB1[1])).label('R11 1k', loc='top'))
        d.add(elm.LED().at((xl + 2.0, u2.PB1[1])).to((xl + 2.0, u2.PB1[1] + 2.2)).label('D5\ncrvena', loc='right'))
        L((xl + 2.0, u2.PB1[1] + 2.2), (xl + 2.0, u2.PB1[1] + 2.8))
        d.add(elm.Ground().at((xl + 2.0, u2.PB1[1] + 2.8)).theta(180))
        # taster (PB2)
        xs = xl + 4.4
        L(u2.PB2, (xs, u2.PB2[1]))
        d.add(elm.Button().at((xs, u2.PB2[1])).to((xs, YG)).label('SW1', loc='right')); dot((xs, YG))
        # ulaz EOL: PA3 -> R9 -> INP -> J3-1; INP -> R10 -> PA4 (C5 na GND)
        xin = xs + 3.0
        d.add(elm.Resistor().at(u2.PA3).to((xin, u2.PA3[1])).label('R9 2k2', loc='top'))
        INP = (xin, u2.PA3[1]); dot(INP)
        L(INP, (xin + 3.5, INP[1])); d.add(elm.Dot(open=True).at((xin + 3.5, INP[1])).label('J3-1 ULAZ', loc='right'))
        mreza((xin + 1.2, INP[1] + 0.4), 'INP')
        d.add(elm.Resistor().at(INP).to((xin, u2.PA4[1] - 0.0)).label('R10\n1k', loc='bottom'))
        L((xin, u2.PA4[1]), u2.PA4)
        dot((xin - 1.4, u2.PA4[1]))
        d.add(elm.Capacitor().at((xin - 1.4, u2.PA4[1])).to((xin - 1.4, YG)).label('C5\n1n', loc='bottom'))
        dot((xin - 1.4, YG))
        d.add(elm.Dot(open=True).at((xin + 3.5, YG)).label('J3-2', loc='right'))
        L((xg_end, YG), (xin + 3.5, YG))
        txt((xin - 1.0, -2.3), 'Polje: EOL 2k2 serijski + 2k2 paralelno kontaktu', fontsize=8, halign='left')

        txt((0, -4.0), 'LoopNet 1IN v0.1 — kompletna šema.  Nije protivpožarni uređaj.  '
                       'Prijem: LINE = 0,058·U_linije, prag AC0 = C4 (DAC0 osvežava svakih 10 ms).  '
                       'Odgovor: (3,3 − 0,75) V / 270 Ω ≈ 9,4 mA.', fontsize=9, halign='left')


if __name__ == '__main__':
    schemdraw.use('svg'); crtaj('kompletna.svg')
    schemdraw.use('matplotlib'); crtaj('kompletna.png')
