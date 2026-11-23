"""Raspored KiCad šeme modula (A1). Koordinate u G = 2,54 mm, Y nadole. Poziva se iz apollo_sema.py."""
from kisch import Sch, custom_ic


def napravi(P, lid, okreni=frozenset()):
    """okreni: nepolarni elementi koje treba zarotirati za 180° da bi pin 1/2 odgovarao pločici."""
    s = Sch('Apollo loop driver MODUL v0.1 - kompletna sema')
    # ---------------------------------------------------------------- sopstveni simboli (pinovi po TI datasheet-u)
    s.custom['apollo:TPS55340PWP'] = custom_ic('apollo:TPS55340PWP', (-7, 4, 7, -5), [
        ('1', 'SW', 3, 5, 270), ('2', 'SW', 4, 5, 270),
        ('3', 'VIN', -8, 3, 0), ('4', 'EN', -8, 2, 0), ('5', 'SS', -8, 0, 0), ('10', 'FREQ', -8, -1, 0),
        ('9', 'FB', 8, 3, 180), ('8', 'COMP', 8, 2, 180),
        ('6', 'SYNC', -3, -6, 90), ('7', 'AGND', -2, -6, 90), ('11', 'NC', -1, -6, 90), ('12', 'PGND', 0, -6, 90),
        ('13', 'PGND', 1, -6, 90), ('14', 'PGND', 2, -6, 90), ('15', 'PAD', 3, -6, 90)])
    s.custom['apollo:TPS560430X3FDBV'] = custom_ic('apollo:TPS560430X3FDBV', (-4, 3, 4, -3), [
        ('5', 'VIN', -5, 1, 0), ('4', 'EN', -5, -1, 0),
        ('1', 'CB', 5, 1, 180), ('6', 'SW', 5, 0, 180), ('3', 'FB', 5, -1, 180), ('2', 'GND', 0, -4, 90)])

    s.custom['apollo:AVR64DD28-xSO'] = custom_ic('apollo:AVR64DD28-xSO', (-9, 15, 9, -15), [
        ('14', 'VDD', -2, 16, 270), ('20', 'VDD', 0, 16, 270), ('6', 'VDDIO2', 2, 16, 270),
        ('15', 'GND', -1, -16, 90), ('21', 'GND', 1, -16, 90),
        ('18', 'PF6/~{RESET}', -10, 12, 0), ('19', 'PF7/UPDI', -10, 10, 0),
        ('22', 'PA0/XTALHF1', -10, 8, 0), ('23', 'PA1/XTALHF2', -10, 5, 0),
        ('26', 'PA4/TXD0', -10, -1, 0), ('27', 'PA5/RXD0', -10, -2, 0),
        ('2', 'PC0/TXD1', -10, -5, 0), ('3', 'PC1/RXD1', -10, -6, 0),
        ('16', 'PF0', -10, -9, 0), ('17', 'PF1', -10, -10, 0), ('4', 'PC2', -10, -12, 0), ('5', 'PC3', -10, -13, 0),
        ('24', 'PA2/TCA0-WO2', 10, 12, 180), ('25', 'PA3', 10, 11, 180), ('28', 'PA6', 10, 10, 180),
        ('7', 'PD1', 10, 9, 180), ('1', 'PA7/AC0-OUT', 10, 7, 180),
        ('8', 'PD2/AIN2/AC0-AINP0', 10, 4, 180), ('10', 'PD4/AIN4', 10, 3, 180), ('11', 'PD5/AIN5', 10, 2, 180),
        ('9', 'PD3', 10, 0, 180), ('12', 'PD6/DAC0', 10, -1, 180), ('13', 'PD7/VREFA', 10, -2, 180)])

    def part(ref, x, y, rot=0, mirror=None, unit=1, fields='r', fofs=(0, 0)):
        li, val, _ = P[ref]
        if ref in okreni:
            rot = (rot + 180) % 360
        return s.add(ref, lid(ref), x, y, rot, mirror, unit, val, '%s:%s' % li, fields, fofs)

    def vert(ref, x, ytop, dole=None, gore=None, fields='r', fofs=(0, 0)):
        """Dvopolni element uspravno, kraj 1 gore u (x, ytop)."""
        e = part(ref, x, ytop + 1.5, 0, fields=fields, fofs=fofs)
        if ref in okreni:
            e.pmap = {'1': '2', '2': '1'}
        if dole:
            s.pwr_pin(e, '2', dole)
        if gore:
            s.pwr_pin(e, '1', gore)
        return e

    def horiz(ref, xl, y, fields='t', fofs=(0, 0)):
        """Dvopolni element vodoravno, kraj 1 levo u (xl, y)."""
        e = part(ref, xl + 1.5, y, 90, fields=fields, fofs=fofs)
        if ref in okreni:
            e.pmap = {'1': '2', '2': '1'}
        return e

    def dioda_h(ref, xa, y, fields='t'):
        """Dioda vodoravno, anoda levo u (xa, y)."""
        return part(ref, xa + 1.5, y, 180, fields=fields)

    w, lab, pwr = s.w, s.lab, s.pwr

    def loc(pt, ime, smer='u'):
        lab(pt, ime, smer, glob=False)

    # ================================================================ 1 ULAZ + 2 BOOST
    s.okvir(4, 6, 98, 50, '1  ULAZ 24 V (21-28 V)   +   2  BOOST 34,4 V  (TPS55340, ~580 kHz)')
    yV = 14
    lab((8, yV), '+24V_IN', 'l')
    f1 = horiz('F1', 11, yV)
    w((8, yV), f1.p('1'))
    d1 = dioda_h('D1', 17, yV)
    w(f1.p('2'), d1.p('2'))
    d6 = part('D6', 15.5, yV + 1.5, 270, fields='l', fofs=(-0.3, 0))      # K gore (VIN_F), A dole
    s.pwr_pin(d6, '2', 'GND')
    s.text((5, 20), 'D6 TVS SMBJ28A\n(U1 VIN/EN max 34 V)\nD1: obrnuti polaritet', 1.0)
    for ref, x in (('C1', 25), ('C2', 30), ('C9', 35), ('C35', 40)):
        vert(ref, x, yV, dole='GND')
    u1 = part('U1', 64, 30, fields=(-7, -6.4))
    l1 = horiz('L1', u1.p('1')[0] - 3, yV, fofs=(-5, 0))
    w(d1.p('1'), l1.p('1'))
    w((22, yV), (22, 20)); lab((22, 20), 'VIN', 'd')
    s.flag((23, yV))
    w(u1.p('1'), (u1.p('1')[0], yV))
    w(u1.p('2'), (u1.p('2')[0], yV))
    w(l1.p('2'), (u1.p('2')[0], yV))
    loc((u1.p('1')[0], yV + 4), 'SW', 'l')
    d2 = dioda_h('D2', u1.p('2')[0], yV)
    # VIN / EN
    xv = u1.p('3')[0] - 2
    w(u1.p('3'), (xv, u1.p('3')[1])); w(u1.p('4'), (xv, u1.p('4')[1])); w((xv, u1.p('4')[1]), (xv, yV))
    # SS, FREQ
    xs, xf = u1.p('5')[0] - 10, u1.p('10')[0] - 5
    w(u1.p('5'), (xs, u1.p('5')[1])); vert('C8', xs, u1.p('5')[1], dole='GND', fields='l')
    w(u1.p('10'), (xf, u1.p('10')[1])); vert('R3', xf, u1.p('10')[1], dole='GND', fields='l')
    loc((xs + 2, u1.p('5')[1]), 'SS')
    loc((xf + 1, u1.p('10')[1]), 'FREQ')
    # donji pinovi -> masa
    yb = u1.p('6')[1] + 1
    for k in ('6', '7', '11', '12', '13', '14', '15'):
        w(u1.p(k), (u1.p(k)[0], yb))
    w((u1.p('6')[0], yb), (u1.p('15')[0], yb))
    pwr((u1.p('12')[0], yb), 'GND')
    s.text((u1.p('6')[0] - 12, yb + 1.5), 'SYNC, AGND, NC, PGND, PowerPAD = masa', 1.0)
    # FB delitelj
    xr1 = d2.p('1')[0] + 5
    r1 = vert('R1', xr1, yV)
    yfb = u1.p('9')[1]
    w(r1.p('2'), (xr1, yfb)); w(u1.p('9'), (xr1, yfb))
    loc((u1.p('9')[0] + 1, yfb), 'BFB', 'r')
    vert('R2', xr1, yfb, dole='GND')
    # kompenzacija COMP: R4 + C6 || C7
    xc = u1.p('8')[0] + 1
    yk = 38
    w(u1.p('8'), (xc, u1.p('8')[1]), (xc, yk), (xc + 9, yk))
    loc((xc, yk - 2), 'COMP', 'r')
    vert('C7', xc + 4, yk, dole='GND')
    vert('R4', xc + 9, yk)
    w((xc + 9, yk + 3), (xc + 9, yk + 4))
    vert('C6', xc + 9, yk + 4, dole='GND')
    loc((xc + 9, yk + 4), 'CC', 'r')
    # +34 V šina
    w(d2.p('1'), (xr1, yV))
    x = xr1 + 5
    for ref in ('C36', 'C3', 'C4', 'C5'):
        vert(ref, x, yV, dole='GND')
        x += 4.5
    w((xr1, yV), (x, yV))
    loc((xr1 + 1, yV), '+34V')
    s.flag((x - 2.5, yV))
    s.text((6, 40), 'VOUT = 1,229 V x (1 + R1/R2) = 1,229 x 28 = 34,4 V\n'
                    'f(SW) ~ 580 kHz (R3 82k), soft-start C8 47n, EN vezan na VIN\n'
                    'L1 33 uH, D2 Schottky 2 A; izlaz C36 100n (VF) + C3/C4 10u + C5 100u\n'
                    'kompenzacija: R4 2k2 + C6 100n, C7 100p\n'
                    'C1 47u / C2 10u / C9 1u / C35 100n: ulazni kondenzatori', 1.2)

    # ================================================================ 5 IZLAZ + 6 PETLJA
    s.okvir(100, 6, 162, 58, '5  IZLAZNI STEPEN 24,2 / 31,2 V   +   6  PETLJA')
    vert('C15', 103, yV, dole='GND')
    u3 = part('U3', 113, 28, fields=(1, -4.5))
    vp = u3.p('7')
    w(vp, (vp[0], yV))
    s.pwr_pin(u3, '4', 'GND')
    for n in ('1', '5', '8'):
        s.nc(u3, n)
    lab((u3.p('3')[0] - 3, u3.p('3')[1]), 'VSET', 'l')
    w((u3.p('3')[0] - 3, u3.p('3')[1]), u3.p('3'))
    o = u3.p('6')
    r10 = horiz('R10', o[0] + 2, o[1])
    w(o, r10.p('1'))
    nb = (r10.p('2')[0] + 2, o[1])
    w(r10.p('2'), nb)
    q1 = part('Q1', nb[0] + 7, nb[1], fields='r', fofs=(1, 0))
    w(nb, q1.p('1'))
    w(q1.p('2'), (q1.p('2')[0], yV))
    w((x, yV), (q1.p('2')[0], yV))
    loc((nb[0] + 1, nb[1]), 'NB')
    ne = (q1.p('3')[0], q1.p('3')[1] + 1)
    w(q1.p('3'), ne)
    loc(ne, 'NE', 'r')
    r13 = vert('R13', ne[0], ne[1])
    yld = r13.p('2')[1]
    q4 = part('Q4', ne[0] - 5, ne[1] + 1.5, mirror='y', fields='l', fofs=(-2.5, 0))
    w(q4.p('1'), (q4.p('1')[0], ne[1]), ne)
    w(q4.p('3'), (q4.p('3')[0], nb[1]))
    w(q4.p('2'), (q4.p('2')[0], yld))
    w((q4.p('2')[0], yld), r13.p('2'))
    q5 = part('Q5', nb[0] + 2, yld + 6, mirror='x', fields='r', fofs=(1, 0))
    w(nb, (nb[0], q5.p('1')[1]), q5.p('1'))
    r14 = vert('R14', q5.p('2')[0], yld, fields='r')
    w(r14.p('2'), q5.p('2'))
    s.pwr_pin(q5, '3', 'GND')
    loc((q5.p('2')[0], q5.p('2')[1]), 'PE', 'r')
    # povratna sprega
    yF = yld + 12
    xF = u3.p('2')[0] - 2
    w(u3.p('2'), (xF, u3.p('2')[1]), (xF, yF))
    loc((xF, u3.p('2')[1] + 3), 'FB', 'l')
    r11 = horiz('R11', xF + 2, yF, fields='b')
    c16 = horiz('C16', xF + 2, yF - 3, fields='t')
    w((xF, yF), r11.p('1'))
    w((xF, yF - 3), c16.p('1'))
    xk = c16.p('2')[0] + 2
    w(c16.p('2'), (xk, yF - 3), (xk, yF))
    w(r11.p('2'), (xk, yF))
    xld = r13.p('2')[0] + 3
    w((xk, yF), (xld, yF), (xld, yld))
    w(r13.p('2'), (xld, yld))
    loc((xk + 2, yF), 'LOOP_DRV', 'r')
    vert('R12', xF, yF, dole='GND', fields='l')
    s.text((xF + 1, yF + 2.5), 'A = 1 + R11/R12 = 1 + 91k/10k = 10,1', 1.1)
    # petlja: F2 -> LOOP_OUT, D3 TVS, VLOOP
    f2 = horiz('F2', xld + 4, yld)
    w((xld, yld), f2.p('1'))
    xo = f2.p('2')[0]
    d3 = part('D3', xo + 3, yld + 1.5, 270, fields='l', fofs=(0, 0.5))
    s.pwr_pin(d3, '2', 'GND')
    r15 = vert('R15', xo + 8, yld)
    yvl = r15.p('2')[1]
    vert('R16', xo + 8, yvl, dole='GND', fields='r')
    w((xo + 8, yvl), (xo + 13, yvl))
    vert('C17', xo + 13, yvl, dole='GND')
    w((xo + 13, yvl), (xo + 16, yvl)); lab((xo + 16, yvl), 'VLOOP')
    w(f2.p('2'), (xo + 18, yld)); lab((xo + 18, yld), 'LOOP_OUT')
    yli = yvl + 9
    r17 = horiz('R17', xo + 2, yli)
    lab(r17.p('1'), 'LOOP_IN', 'l')
    w(r17.p('2'), (xo + 8, yli))
    vert('R18', xo + 8, yli, dole='GND', fields='r')
    w((xo + 8, yli), (xo + 13, yli))
    vert('C18', xo + 13, yli, dole='GND')
    w((xo + 13, yli), (xo + 16, yli)); lab((xo + 16, yli), 'VRET')
    s.text((xo + 1, yli + 6), 'VLOOP, VRET = U/11 (100k/10k) -> ADC\nD3 SMBJ36A TVS, F2 PTC 750 mA', 1.1)
    s.text((101, 52), 'U3 OPA197 x10,1 -> R10 -> Q1 MJD122 Darlington (izvor) / Q5 MMBT5401 (ponor: aktivna silazna ivica)\n'
                      'Q4 + R13 2 Ohm: strujni limit ~ 0,65 V / 2 Ohm = 325 mA (Kelvin vod sa NE)\n'
                      'VSET 2,40 V -> 24,2 V (osnovni nivo),  3,094 V -> 31,2 V (impuls)', 1.1)

    # ================================================================ 9 J1
    s.okvir(164, 6, 214, 58, '9  LETVICA J1 -> maticna ploca (2x14, 2,54 mm, donja strana)')
    j1 = part('J1', 187, 30, fields=(-1.5, -9))
    J = P['J1'][2]
    for i in range(1, 29):
        n, pn = J[str(i)], str(i)
        a = j1.p(pn)
        d = j1.out(pn)
        b = (a[0] + d[0] * 3, a[1])
        if n in ('GND', '+3V3'):
            w(a, b)
            pwr(b, n, d)
        else:
            s.lab_pin(j1, pn, n, stub=3)
    s.text((166, 50), 'Pinovi: 1-4 +24 V ulaz; 5-8, 10, 19, 20, 27, 28 GND; 9 3V3;\n'
                      '11 TX, 12 RX (UART 3,3 V); 13 RUN; 14 BOOT; 15/16 USB D+/D-;\n'
                      '17/18 SWCLK/SWDIO; 21/22 ISENSE (povrat petlje kroz sant R19);\n'
                      '23/24 LOOP_IN; 25/26 LOOP_OUT', 1.1)

    # ================================================================ 3 BUCK 3,3 V
    s.okvir(4, 60, 60, 86, '3  BUCK 3,3 V  (TPS560430X3F, fiksno 3,3 V)')
    u2 = part('U2', 28, 73, fields=(-4, -4.8))
    yb3 = u2.p('5')[1]
    lab((8, yb3), 'VIN', 'l')
    w((8, yb3), u2.p('5'))
    w(u2.p('4'), (u2.p('4')[0] - 1, u2.p('4')[1]), (u2.p('4')[0] - 1, yb3))
    vert('C11', 12, yb3, dole='GND')
    vert('C37', 17, yb3, dole='GND')
    s.pwr_pin(u2, '2', 'GND')
    cb, sw, fb = u2.p('1'), u2.p('6'), u2.p('3')
    w(cb, (cb[0] + 1, cb[1]), (cb[0] + 1, cb[1] - 4), (cb[0] + 4, cb[1] - 4))
    c10 = vert('C10', cb[0] + 4, cb[1] - 4)
    w(c10.p('2'), (cb[0] + 4, sw[1]))
    w(sw, (cb[0] + 4, sw[1]))
    l2 = horiz('L2', cb[0] + 6, sw[1], fields='b', fofs=(0, 1.2))
    w((cb[0] + 4, sw[1]), l2.p('1'))
    x3 = l2.p('2')[0] + 2
    w(l2.p('2'), (x3, sw[1]))
    w(fb, (fb[0] + 1, fb[1]), (fb[0] + 1, fb[1] + 3), (x3, fb[1] + 3), (x3, sw[1]))
    loc((cb[0] + 1.5, sw[1]), 'SW3', 'r')
    loc((cb[0] + 1, cb[1] - 2), 'CB', 'l')
    pwr((x3, sw[1]), '+3V3')
    w((x3, sw[1]), (x3 + 9, sw[1]))
    vert('C12', x3 + 4, sw[1], dole='GND')
    vert('C13', x3 + 9, sw[1], dole='GND')
    # PWR_FLAG: oznaka za ERC da su +3V3 i GND napajane mreze
    pwr((50, 78), '+3V3'); w((50, 78), (50, 80)); s.flag((50, 80), 180)
    pwr((55, 81), 'GND'); w((55, 79), (55, 81)); s.flag((55, 79))
    s.text((6, 80), 'FB = VOUT (fiksna 3,3 V verzija X3F), ~1,1 MHz; C10 bootstrap 100n; L2 15 uH', 1.1)

    # ================================================================ 4 VSET
    s.okvir(62, 60, 162, 86, '4  VSET  (3,094 V impuls / 2,40 V osnovni / 0 V iskljuceno)')
    yS = 69
    vert('R5', 66, yS - 3, gore='+3V3', fields='l')
    w((66, yS), (124, yS))
    lab((124, yS), 'VSET')
    vert('R6', 71, yS, dole='GND')
    vert('C14', 76, yS, dole='GND')
    r7 = vert('R7', 83, yS)
    q2 = part('Q2', 82, yS + 7, fields='r', fofs=(1, 0))
    w(r7.p('2'), q2.p('3'))
    s.pwr_pin(q2, '2', 'GND')
    r8 = horiz('R8', q2.p('1')[0] - 5, q2.p('1')[1], fields='b')
    w(r8.p('2'), q2.p('1'))
    lab(r8.p('1'), 'NIVO', 'l')
    loc((83, yS + 4), 'Q2D', 'r')
    q3 = part('Q3', 97, yS + 2, mirror='y', fields='l', fofs=(-1, 0))
    w(q3.p('3'), (q3.p('3')[0], yS))
    s.pwr_pin(q3, '2', 'GND')
    g3 = q3.p('1')
    n3 = (g3[0] + 2, g3[1])
    w(g3, n3, (n3[0] + 3, n3[1])); lab((n3[0] + 3, n3[1]), 'EN_N')
    r9 = vert('R9', n3[0], n3[1] + 2)
    w(n3, r9.p('1'))
    s.pwr_pin(r9, '2', '+3V3')
    q6 = part('Q6', 113, yS + 2, mirror='y', fields='l', fofs=(-1, 0))
    w(q6.p('3'), (q6.p('3')[0], yS))
    s.pwr_pin(q6, '2', 'GND')
    w(q6.p('1'), (q6.p('1')[0] + 3, q6.p('1')[1])); lab((q6.p('1')[0] + 3, q6.p('1')[1]), 'OCP')
    s.text((128, 64), 'NIVO = 1 (Q2 vodi):\n  VSET = 3,3 x (15k||3k24)/(1k + 15k||3k24) = 2,40 V\n'
                      'NIVO = 0:  VSET = 3,3 x 15k/16k = 3,094 V\n'
                      'EN_N = 1 (R9 pull-up, i dok MCU ne krene)\n  ili OCP = 1:  VSET = 0 -> petlja ugasena\n'
                      'C14 10n: filtar VSET', 1.1)

    # ================================================================ 8 MCU AVR64DD28
    s.okvir(4, 88, 120, 178, '8  MCU AVR64DD28 (SOIC-28) + kristal 16 MHz   (UART0 ka maticnoj, UPDI/RESET, UART1 dijagnostika)')
    u7 = part('U7', 40, 130, fields=(11, -16.5))
    # napajanje: VDD 14, VDD 20, VDDIO2 6 -> +3V3; GND 15, 21
    yb = u7.p('20')[1] - 3
    for k in ('14', '20', '6'):
        w(u7.p(k), (u7.p(k)[0], yb))
    w((u7.p('14')[0], yb), (u7.p('6')[0], yb))
    pwr((u7.p('20')[0], yb), '+3V3')
    s.pwr_pin(u7, '15', 'GND')
    s.pwr_pin(u7, '21', 'GND')
    for i, ref in enumerate(('C25', 'C28', 'C29', 'C32')):
        vert(ref, 9 + 6 * i, 96, gore='+3V3', dole='GND')
    s.text((7, 102.5), 'blokada uz pinove (DS sl. 4-1 / 4-2): C25 VDD 14, C28 VDD 20, C29 VDDIO2 6 (MVIO = 3,3 V),\n'
                       'C32 1u opcioni', 1.0)
    # RESET (R29 pull-up, C30 filtar) i UPDI ka maticnoj ploci
    rs = u7.p('18')
    w(rs, (12, rs[1]))
    lab((12, rs[1]), 'RESET', 'l')
    vert('R29', 24, rs[1] - 3, gore='+3V3', fields='r')
    vert('C30', 15, rs[1], dole='GND', fields='r')
    s.lab_pin(u7, '19', 'UPDI', stub=2)
    # kristal 16 MHz na XTALHF1/2
    xi, xo_ = u7.p('22'), u7.p('23')
    xy = xi[0] - 6
    y1 = part('Y1', xy, (xi[1] + xo_[1]) / 2, 270, fields=(-6, 4.5))
    w(xi, (xy - 6, xi[1]))
    w(xo_, y1.p('3'))
    s.pwr_pin(y1, '2', 'GND')
    vert('C26', xy - 6, xi[1], dole='GND', fields='l')
    vert('C27', xy + 3, xo_[1], dole='GND', fields='r')
    loc((xy + 2.5, xi[1]), 'XIN', 'r')
    loc((xy + 4.5, xo_[1]), 'XO', 'r')
    # UART-ovi
    for pn, ime in (('26', 'TX'), ('27', 'RX'), ('2', 'DBG_TX'), ('3', 'DBG_RX')):
        s.lab_pin(u7, pn, ime, stub=2)
    # desna strana: upravljanje petljom i merenje
    for pn, ime in (('24', 'NIVO'), ('25', 'EN_N'), ('28', 'OC_RST'), ('7', 'OCP'),
                    ('8', 'IAMP'), ('10', 'VLOOP'), ('11', 'VRET')):
        s.lab_pin(u7, pn, ime, stub=2)
    led = u7.p('1')
    r35 = horiz('R35', led[0] + 2, led[1], fields='b')
    w(led, r35.p('1'))
    d5 = part('D5', r35.p('2')[0] + 3.5, led[1], 180, fields='b')
    w(r35.p('2'), d5.p('2'))
    s.pwr_pin(d5, '1', 'GND', stub=1)
    loc((r35.p('2')[0] + 1, led[1]), 'LED_A', 'd')
    for pn in ('16', '17', '4', '5', '9', '12', '13'):
        s.nc(u7, pn)
    s.text((63, 112), 'PA2 NIVO: TCA0 WO2 (impulsi petlje, 62,5 ns korak)\n'
                      'PD2 IAMP: AC0 AINP0, prag = interni DACREF (umesto MCP6561 + PWM)\n'
                      '   + ADC AIN2 (struja petlje); PD4 VLOOP, PD5 VRET: ADC\n'
                      'AC0 -> event sistem -> TCB capture: vreme odgovora uredjaja bez CPU\n'
                      'PA4/PA5 USART0 (ALT1) ka maticnoj ploci, PC0/PC1 USART1 dijagnostika\n'
                      'PA7 LED (moze i AC0 OUT za osciloskop)\n'
                      'UPDI (PF7) i RESET (PF6) na J1: programiranje / bootloader sa maticne\n'
                      'Kristal 16 MHz na PA0/PA1 (XOSCHF, FRQRANGE 16M)\n'
                      'EN_N ima pull-up R9: petlja ugasena dok je MCU u resetu', 1.0)

    # ================================================================ 7 MERENJE I ZAŠTITA
    s.okvir(122, 88, 226, 140, '7  MERENJE STRUJE (sant 1 Ohm, x5,02)  I  ZASTITA SA ZADRSKOM (> ~285 mA)')
    yI = 106
    lab((127, yI), 'ISENSE', 'l')
    w((127, yI), (130, yI))
    vert('R19', 130, yI, dole='GND', fields='l')
    r20 = horiz('R20', 132, yI)
    w((130, yI), r20.p('1'))
    u4a = part('U4', 146, yI + 1, unit=1, fields=(-1, -4.6))
    w(r20.p('2'), u4a.p('3'))
    loc((136, yI), 'NA')
    vert('C19', 138, yI, dole='GND', fields='r')
    nm = (u4a.p('2')[0] - 1, u4a.p('2')[1])
    w(u4a.p('2'), nm, (nm[0], yI + 6))
    loc((nm[0], yI + 4), 'NM', 'l')
    vert('R21', nm[0], yI + 6, dole='GND', fields='l')
    r22 = horiz('R22', nm[0] + 3, yI + 6, fields='b')
    w((nm[0], yI + 6), r22.p('1'))
    ia = (u4a.p('1')[0] + 2, u4a.p('1')[1])
    w(u4a.p('1'), ia, (ia[0], yI + 6), r22.p('2'))
    xu = ia[0] + 4
    w(ia, (xu, ia[1]))
    w((xu, ia[1]), (xu + 7, ia[1]))
    w((xu + 3, ia[1]), (xu + 3, ia[1] - 2)); lab((xu + 3, ia[1] - 2), 'IAMP', 'u')
    r26 = horiz('R26', xu + 7, ia[1])
    xoi = r26.p('2')[0]
    loc((xoi + 1, ia[1]), 'OC_IN')
    q7 = part('Q7', xoi + 2, ia[1] + 4, fields='r', fofs=(1, 0))
    w(q7.p('3'), (q7.p('3')[0], ia[1]))
    s.pwr_pin(q7, '2', 'GND')
    g7 = q7.p('1')
    w(g7, (g7[0] - 4, g7[1]), (g7[0] - 4, g7[1] + 4))
    lab((g7[0] - 4, g7[1] + 4), 'OC_RST', 'd')
    vert('R28', g7[0] - 2, g7[1], dole='GND', fields='r')
    vert('C24', xoi + 7, ia[1], dole='GND')
    xr27 = xoi + 10
    yz = ia[1] + 14
    w((xr27, ia[1]), (xr27, yz))
    u6 = part('U6', xoi + 19, ia[1] + 1, fields=(1, -4.8))
    w(r26.p('2'), u6.p('3'))
    nr = (u6.p('4')[0] - 1, u6.p('4')[1] + 5)
    w(u6.p('4'), (nr[0], u6.p('4')[1]), nr)
    r24 = horiz('R24', nr[0] + 2, nr[1], fields='b')
    w(nr, r24.p('1'))
    s.pwr_pin(r24, '2', '+3V3', stub=1)
    vert('R25', nr[0], nr[1], dole='GND', fields='l')
    loc((nr[0], nr[1] - 3), 'OC_REF', 'r')
    s.pwr_pin(u6, '5', '+3V3')
    s.pwr_pin(u6, '2', 'GND')
    op = (u6.p('1')[0] + 2, u6.p('1')[1])
    w(u6.p('1'), op, (op[0] + 3, op[1])); lab((op[0] + 3, op[1]), 'OCP')
    r27 = horiz('R27', xr27 + 1, yz, fields='b')
    w((xr27, yz), r27.p('1'))
    d4 = part('D4', r27.p('2')[0] + 4.5, yz, 0, fields='b')     # K levo (OC_FB), A desno (OCP)
    w(r27.p('2'), d4.p('1'))
    w(d4.p('2'), (op[0], yz), op)
    loc((r27.p('2')[0] + 1, yz), 'OC_FB')
    s.text((124, 126), 'IAMP = 5,02 x I x 1 Ohm   (pojacanje 1 + R22/R21 = 1 + 40k2/10k)\n'
                       'Prijem odgovora uredjaja: IAMP -> AC0 u MCU (prag DACREF), vidi blok 8\n'
                       'OCP = 1 kad IAMP > OC_REF = 3,3 x 10k/23k = 1,435 V  ->  I > ~285 mA\n'
                       'D4 + R27 vracaju OCP na OC_IN -> zadrska (latch) dok MCU ne posalje OC_RST (Q7)\n'
                       'OCP -> Q6 hardverski gasi VSET (petlju) i javlja se MCU (PD1)', 1.1)
    # napajanje OP/komparatora, U4B
    u4p = part('U4', 205, 108, unit=3, fields=(-6, -0.5))
    s.pwr_pin(u4p, '8', '+3V3')
    s.pwr_pin(u4p, '4', 'GND')
    vert('C20', 210, 106, gore='+3V3', dole='GND')
    vert('C23', 215, 106, gore='+3V3', dole='GND')
    s.text((200, 98), 'napajanje U4, blokada:\nC20 (U4), C23 (U6)', 1.1)
    u4b = part('U4', 210, 123, unit=2, fields=(1, -4.5))
    i6, o7 = u4b.p('6'), u4b.p('7')
    w(i6, (i6[0] - 1, i6[1]), (i6[0] - 1, i6[1] + 2), (o7[0] + 1, i6[1] + 2), (o7[0] + 1, o7[1]), o7)
    s.pwr_pin(u4b, '5', 'GND', stub=1)
    s.text((200, 116), 'U4B se ne koristi:\nsledilac, + na masi', 1.1)

    s.text((5, 181), 'Mreze istog imena (globalne oznake, +3V3, GND) su spojene.  Pinovi IC: vidi make_pcb.py.  '
                     'Netlista ove seme se automatski poredi sa netlistom plocice (apollo_sema.py).', 1.3)
    return s
