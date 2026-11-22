"""Kompletna električna šema Apollo loop driver MODULA v0.1 na jednom listu.

Pokretanje:  python kompletna.py   -> kompletna.svg, kompletna.png  (+ izveštaj provere na izlazu)
Oznake, vrednosti i pinovi se čitaju iz ../pcb/make_pcb.py (rečnik P – izvor istine za pločicu), a skripta na kraju
iz nacrtanih žica izračuna mreže i uporedi ih sa P. Šema se ne snima ako provera nađe grešku.
Samo laboratorija – nije protivpožarni uređaj (EN 54).
"""
import sys

import schemdraw
import schemdraw.elements as elm

from alat import Sema, ucitaj_P, ACC, SIVA

P = ucitaj_P()


def crtaj(fname):
    with schemdraw.Drawing(file=fname, show=False) as d:
        d.config(fontsize=7.5, lw=1.0, font='DejaVu Sans')
        S = Sema(d, P)
        w, g, tag, dv, txt = S.w, S.gnd, S.tag, S.dv, S.txt

        def naslov(p, t):
            txt(p, t, fontsize=10, halign='left', valign='bottom', color='#1d4e89')

        # =====================================================================================================
        # 1 ULAZ 24 V  +  2 BOOST 34 V
        # =====================================================================================================
        yV = 60.0
        naslov((3, yV + 2.2), '1  ULAZ 24 V (21–28 V)            2  BOOST 34,4 V  (TPS55340, ≈580 kHz)')
        tag((6.0, yV), '+24V_IN', 'l')
        dv('F1', (6.0, yV), (9.5, yV))
        dv('D1', (9.5, yV), (13.0, yV), t='t')
        txt((11.25, yV - 0.5), 'zaštita od\nobrnutog pol.', fontsize=6, color=SIVA, valign='top')
        # U1
        u1 = S.ic('U1', {
            'top': [None, None, None, None, None, ('1', 'SW'), ('2', 'SW')],
            'left': [('3', 'VIN'), ('4', 'EN'), ('5', 'SS'), ('10', 'FREQ')],
            'right': [('9', 'FB'), ('8', 'COMP'), None, None],
            'bottom': [('6', 'SYNC'), ('7', 'AGND'), ('11', 'NC'), ('12', 'PGND'), ('13', 'PGND'), ('14', 'PGND'),
                       ('15', 'PAD')],
        }, pinspacing=1.0)
        u1 = S.ic_dodaj('U1', u1.anchor('p1').at((32.0, yV - 3.0)))
        p = u1.absanchors
        xs1, xs2 = p['p1'][0], p['p2'][0]
        xl = xs1 - 4.0
        # VIN šina
        w((13.0, yV), (xl, yV))
        for ref, x in (('C1', 14.5), ('C2', 16.5), ('C9', 18.5), ('C35', 20.5)):
            dv(ref, (x, yV), (x, yV - 2.6), t='r' if ref != 'C35' else 'r')
            g((x, yV - 2.6))
        dv('L1', (xl, yV), (xs1, yV), t='t')
        w(p['p1'], (xs1, yV)); w(p['p2'], (xs2, yV)); w((xs1, yV), (xs2, yV))
        txt((xs1 + 0.2, yV + 0.25), 'SW', color=ACC, halign='left', valign='bottom', fontsize=6.5)
        xd2 = xs2 + 3.6
        dv('D2', (xs2, yV), (xd2, yV), t='t')
        # VIN, EN
        xv = p['p3'][0] - 1.2
        w(p['p3'], (xv, p['p3'][1])); w(p['p4'], (xv, p['p4'][1])); w((xv, p['p4'][1]), (xv, yV))
        txt((xv - 0.15, p['p4'][1] - 0.1), 'EN=VIN', fontsize=6, color=SIVA, halign='right', valign='top')
        # SS, FREQ
        xss, xfr = p['p5'][0] - 4.4, p['p10'][0] - 2.4
        w(p['p5'], (xss, p['p5'][1])); dv('C8', (xss, p['p5'][1]), (xss, p['p5'][1] - 2.6), t='l'); g((xss, p['p5'][1] - 2.6))
        w(p['p10'], (xfr, p['p10'][1])); dv('R3', (xfr, p['p10'][1]), (xfr, p['p10'][1] - 2.6), t='l'); g((xfr, p['p10'][1] - 2.6))
        # donji pinovi -> masa
        yb = p['p6'][1] - 0.8
        for k in ('6', '7', '11', '12', '13', '14', '15'):
            w(p['p' + k], (p['p' + k][0], yb))
        w((p['p6'][0], yb), (p['p15'][0], yb)); g(((p['p6'][0] + p['p15'][0]) / 2, yb))
        # FB delitelj, kompenzacija
        xr1 = xd2 + 1.6
        yfb = p['p9'][1]
        dv('R1', (xr1, yV), (xr1, yfb), t='r')
        w(p['p9'], (xr1, yfb))
        dv('R2', (xr1, yfb), (xr1, yfb - 3.0), t='r'); g((xr1, yfb - 3.0))
        txt((xr1 - 0.2, yfb + 0.15), 'BFB', fontsize=6.5, color=ACC, halign='right', valign='bottom')
        yc = p['p8'][1]
        xc7, xr4 = p['p8'][0] + 1.0, p['p8'][0] + 2.6
        w(p['p8'], (xr4, yc))
        dv('C7', (xc7, yc), (xc7, yc - 2.6), t='l'); g((xc7, yc - 2.6))
        dv('R4', (xr4, yc), (xr4, yc - 2.4), t='r')
        dv('C6', (xr4, yc - 2.4), (xr4, yc - 4.6), t='r'); g((xr4, yc - 4.6))
        txt((xr4 + 0.15, yc - 2.4), 'CC', fontsize=6, color=ACC, halign='left', valign='center')
        txt((p['p8'][0] + 0.15, yc + 0.12), 'COMP', fontsize=6, color=ACC, halign='left', valign='bottom')
        # +34 V šina i izlazni kondenzatori
        xc = xr1 + 1.8
        for ref in ('C36', 'C3', 'C4', 'C5'):
            dv(ref, (xc, yV), (xc, yV - 2.6), t='r'); g((xc, yV - 2.6))
            xc += 2.2
        txt((xr1 + 1.0, yV + 0.3), '+34V  (1,229 V·(1+270k/10k) = 34,4 V)', color=ACC, halign='left', valign='bottom')

        # =====================================================================================================
        # 5 IZLAZNI STEPEN  +  6 PETLJA
        # =====================================================================================================
        X5 = 62.0
        naslov((X5 - 4, yV + 2.2), '5  IZLAZ 24,2 / 31,2 V  (OPA197 ×10,1 + MJD122 izvor + MMBT5401 ponor)        6  PETLJA')
        u3 = S.oa('U3', elm.Opamp(leads=True).flip().anchor('in2').at((X5, 52.0)),
                  {'in1': '2', 'in2': '3', 'out': '6'}, 'U3A  OPA197')
        o = u3.absanchors
        xnb = o['out'][0] + 3.2
        nby = o['out'][1]
        dv('R10', o['out'], (xnb, nby), t='t')
        q1 = S.tr('Q1', elm.BjtNpn(circle=True).anchor('base').at((xnb + 3.0, nby)),
                  {'base': '1', 'collector': '2', 'emitter': '3'}, t='r')
        w((xnb, nby), q1.absanchors['base'])
        qc, qe = q1.absanchors['collector'], q1.absanchors['emitter']
        w(qc, (qc[0], yV))
        w((xd2, yV), (qc[0], yV))                      # +34 V šina do kolektora Q1
        NE = (qe[0], qe[1] - 0.6)
        w(qe, NE)
        yLD = NE[1] - 3.0
        dv('R13', NE, (NE[0], yLD), t='r')
        txt((NE[0] + 0.2, NE[1] + 0.1), 'NE', fontsize=6, color=ACC, halign='left', valign='bottom')
        q4 = S.tr('Q4', elm.BjtNpn().reverse().anchor('base').at((NE[0] - 1.0, NE[1])),
                  {'base': '1', 'emitter': '2', 'collector': '3'}, t='l', ofs=(-0.1, -0.9))
        w(q4.absanchors['base'], NE)
        c4, e4 = q4.absanchors['collector'], q4.absanchors['emitter']
        w(c4, (xnb, c4[1]))
        w(e4, (e4[0], yLD))
        yq5 = yLD - 3.0
        q5 = S.tr('Q5', elm.BjtPnp().anchor('base').at((xnb + 0.8, yq5)),
                  {'base': '1', 'emitter': '2', 'collector': '3'}, t='r')
        w((xnb, nby), (xnb, yq5), q5.absanchors['base'])
        e5, c5 = q5.absanchors['emitter'], q5.absanchors['collector']
        dv('R14', e5, (e5[0], yLD), t='l')
        g(c5)
        xld = NE[0] + 1.2
        w((e5[0], yLD), (xld, yLD))
        txt((xnb - 0.15, nby + 0.15), 'NB', fontsize=6, color=ACC, halign='right', valign='bottom')
        txt((NE[0] + 0.3, yLD + 0.15), 'LOOP_DRV', fontsize=6, color=ACC, halign='left', valign='bottom')
        txt((e5[0] + 0.15, e5[1] - 0.05), 'PE', fontsize=6, color=ACC, halign='left', valign='top')
        # povratna sprega: LOOP_DRV -> R11 || C16 -> FB, R12 -> GND
        yF = yq5 - 3.3
        xF = o['in1'][0] - 0.6
        w(o['in1'], (xF, o['in1'][1]), (xF, yF))
        dv('R11', (xF, yF), (xF + 4.4, yF), t='b')
        dv('C16', (xF, yF + 1.3), (xF + 4.4, yF + 1.3), t='t')
        w((xF + 4.4, yF + 1.3), (xF + 4.4, yF))
        w((xF + 4.4, yF), (xld, yF), (xld, yLD))
        dv('R12', (xF, yF), (xF, yF - 2.6), t='l'); g((xF, yF - 2.6))
        txt((xF - 0.15, o['in1'][1] - 0.1), 'FB', fontsize=6, color=ACC, halign='right', valign='top')
        txt((xF + 2.2, yF - 1.7), 'A = 1 + 91k/10k = 10,1', fontsize=6, color=SIVA, halign='center', valign='top')
        # napajanje U3 (pinovi 7, 4) + C15
        xu3p = X5 + 0.5
        u3p = S.ic('U3', {'top': [('7', 'V+')], 'bottom': [('4', 'V−')]}, naziv='U3B\nOPA197', pinspacing=1.0, edgepadW=0.5, rot=0,
                   edgepadH=0.4)
        u3p = d.add(u3p.theta(0).anchor('p7').at((xu3p, yV - 0.0)))
        S._pin('U3', '7', u3p.absanchors['p7']); S._pin('U3', '4', u3p.absanchors['p4'])
        g(u3p.absanchors['p4'])
        dv('C15', (xu3p + 2.2, yV), (xu3p + 2.2, yV - 2.6), t='r'); g((xu3p + 2.2, yV - 2.6))
        for k in ('1', '5', '8'):
            pass
        txt((xu3p - 1.6, u3p.absanchors['p4'][1] - 0.2), 'U3 pinovi\n1, 5, 8 NC', fontsize=6, color=SIVA,
            halign='right', valign='top')

        # petlja: LOOP_DRV -> F2 -> LOOP_OUT, TVS, delitelji
        xo = xld + 4.2
        dv('F2', (xld, yLD), (xo, yLD), t='t')
        xd3, xr15 = xo + 1.4, xo + 3.6
        dv('D3', (xd3, yLD - 3.0), (xd3, yLD), t='l')
        g((xd3, yLD - 3.0))
        dv('R15', (xr15, yLD), (xr15, yLD - 3.0), t='r')
        yvl = yLD - 3.0
        dv('R16', (xr15, yvl), (xr15, yvl - 2.6), t='l'); g((xr15, yvl - 2.6))
        w((xr15, yvl), (xr15 + 2.0, yvl))
        dv('C17', (xr15 + 2.0, yvl), (xr15 + 2.0, yvl - 2.6), t='r'); g((xr15 + 2.0, yvl - 2.6))
        w((xr15 + 2.0, yvl), (xr15 + 4.0, yvl)); tag((xr15 + 4.0, yvl), 'VLOOP')
        xlo = xr15 + 6.5
        w((xo, yLD), (xlo, yLD)); tag((xlo, yLD), 'LOOP_OUT')
        txt((xr15 + 0.3, yvl + 0.6), 'VLOOP = U/11', fontsize=6, color=SIVA, halign='left', valign='bottom')
        # LOOP_IN -> VRET
        yli = yvl - 5.0
        xli = xr15 - 4.5
        tag((xli, yli), 'LOOP_IN', 'l')
        dv('R17', (xli, yli), (xr15, yli), t='t')
        dv('R18', (xr15, yli), (xr15, yli - 2.6), t='l'); g((xr15, yli - 2.6))
        w((xr15, yli), (xr15 + 2.0, yli))
        dv('C18', (xr15 + 2.0, yli), (xr15 + 2.0, yli - 2.6), t='r'); g((xr15 + 2.0, yli - 2.6))
        w((xr15 + 2.0, yli), (xr15 + 4.0, yli)); tag((xr15 + 4.0, yli), 'VRET')

        # =====================================================================================================
        # 3 BUCK 3,3 V
        # =====================================================================================================
        yB = 40.0
        naslov((3, yB + 2.4), '3  BUCK 3,3 V  (TPS560430X3F, fiksnih 3,3 V)')
        w((13.0, yV), (13.0, yB))                     # VIN sa izlaza D1
        txt((12.8, yB + 3.0), 'VIN', fontsize=6.5, color=ACC, halign='right', valign='center')
        u2 = S.ic('U2', {
            'left': [('5', 'VIN'), ('4', 'EN')],
            'right': [('1', 'CB'), ('6', 'SW'), ('3', 'FB')],
            'bottom': [('2', 'GND')],
        }, pinspacing=1.4, edgepadW=2.2)
        u2 = S.ic_dodaj('U2', u2.anchor('p5').at((21.0, yB)))
        q = u2.absanchors
        w((13.0, yB), q['p5'])
        xen = q['p5'][0] - 0.8
        w(q['p4'], (xen, q['p4'][1]), (xen, yB))
        dv('C11', (15.0, yB), (15.0, yB - 2.6), t='r'); g((15.0, yB - 2.6))
        dv('C37', (17.4, yB), (17.4, yB - 2.6), t='r'); g((17.4, yB - 2.6))
        g(q['p2'])
        xcb = q['p1'][0] + 1.2
        w(q['p1'], (xcb, q['p1'][1]))
        dv('C10', (xcb, q['p1'][1]), (xcb, q['p6'][1]), t='r')
        w(q['p6'], (xcb, q['p6'][1]))
        x33 = xcb + 4.4
        dv('L2', (xcb, q['p6'][1]), (x33, q['p6'][1]), t='t', ofs=0.3)
        w(q['p3'], (x33, q['p3'][1]), (x33, q['p6'][1]))
        w((x33, q['p6'][1]), (x33 + 3.6, q['p6'][1]))
        S.vcc((x33, q['p6'][1]), '+3V3')
        dv('C12', (x33 + 1.6, q['p6'][1]), (x33 + 1.6, q['p6'][1] - 2.6), t='r'); g((x33 + 1.6, q['p6'][1] - 2.6))
        dv('C13', (x33 + 3.6, q['p6'][1]), (x33 + 3.6, q['p6'][1] - 2.6), t='r'); g((x33 + 3.6, q['p6'][1] - 2.6))
        txt((xcb + 0.2, q['p6'][1] - 0.2), 'SW3', fontsize=6, color=ACC, halign='left', valign='top')

        # =====================================================================================================
        # 4 VSET
        # =====================================================================================================
        yS = 36.0
        xS0 = 39.0
        naslov((xS0 - 1, yB + 2.4), '4  VSET  (3,094 V impuls / 2,40 V osnovni / 0 V isključeno)')
        S.vcc((xS0, yB), '+3V3')
        dv('R5', (xS0, yB), (xS0, yS), t='l')
        xvs = X5 - 2.2                                  # uspon VSET ka U3+
        w((xS0, yS), (xvs, yS))
        dv('R6', (xS0 + 1.8, yS), (xS0 + 1.8, yS - 2.6), t='r'); g((xS0 + 1.8, yS - 2.6))
        dv('C14', (xS0 + 4.0, yS), (xS0 + 4.0, yS - 2.6), t='r'); g((xS0 + 4.0, yS - 2.6))
        # Q2 + R7 (NIVO)
        xq2 = xS0 + 7.0
        dv('R7', (xq2, yS), (xq2, yS - 2.6), t='l')
        q2 = S.tr('Q2', elm.NFet().anchor('drain').at((xq2, yS - 2.6)), {'gate': '1', 'source': '2', 'drain': '3'},
                  t='l', ofs=(0, -0.2))
        g(q2.absanchors['source'])
        gq = q2.absanchors['gate']
        w(gq, (gq[0] + 0.5, gq[1]), (gq[0] + 0.5, gq[1] - 0.8))
        dv('R8', (gq[0] + 0.5, gq[1] - 0.8), (gq[0] + 0.5, gq[1] - 3.4), t='r')
        tag((gq[0] + 0.5, gq[1] - 3.4), 'NIVO', 'l')
        txt((xq2 + 0.2, yS - 2.75), 'Q2D', fontsize=6, color=ACC, halign='left', valign='top')
        # Q3 (EN_N, R9 pull-up -> petlja isključena dok MCU ne krene)
        xq3 = xS0 + 12.0
        w((xq3, yS), (xq3, yS - 1.0))
        q3 = S.tr('Q3', elm.NFet().anchor('drain').at((xq3, yS - 1.0)), {'gate': '1', 'source': '2', 'drain': '3'},
                  t='l', ofs=(0, -0.2))
        g(q3.absanchors['source'])
        g3 = q3.absanchors['gate']
        n3 = (g3[0] + 0.6, g3[1])
        w(g3, n3)
        dv('R9', n3, (n3[0] + 3.0, n3[1]), t='b')
        S.vcc((n3[0] + 3.0, n3[1]), '+3V3')
        w(n3, (n3[0], n3[1] - 3.2)); tag((n3[0], n3[1] - 3.2), 'EN_N')
        # Q6 (OCP)
        xq6 = xS0 + 18.6
        w((xq6, yS), (xq6, yS - 1.0))
        q6 = S.tr('Q6', elm.NFet().anchor('drain').at((xq6, yS - 1.0)), {'gate': '1', 'source': '2', 'drain': '3'},
                  t='l', ofs=(0, -0.2))
        g(q6.absanchors['source'])
        g6 = q6.absanchors['gate']
        w(g6, (g6[0] + 0.5, g6[1]), (g6[0] + 0.5, g6[1] - 3.2)); tag((g6[0] + 0.5, g6[1] - 3.2), 'OCP')
        w((xvs, yS), (xvs, o['in2'][1]), o['in2'])
        txt((xvs + 0.15, yS + 0.15), 'VSET', color=ACC, halign='left', valign='bottom', fontsize=6.5)
        txt((xS0 + 0.5, yS - 6.6),
            'Q2 uključen (NIVO=1): 3,3·(15k‖3k24)/(1k+15k‖3k24) = 2,40 V → 24,2 V na petlji\n'
            'Q2 isključen: 3,3·15k/16k = 3,094 V → 31,2 V\n'
            'Q3 (EN_N=1, R9) ili Q6 (OCP=1): VSET = 0 → petlja isključena',
            fontsize=6, color=SIVA, halign='left', valign='top')

        # =====================================================================================================
        # 7 MERENJE STRUJE I ZAŠTITA
        # =====================================================================================================
        yM = 27.4
        XM = 64.0
        naslov((XM - 1, 34.5), '7  MERENJE STRUJE (šant 1 Ω, ×5,02) I ZAŠTITA SA ZADRŠKOM (> ≈285 mA)')
        tag((XM, yM + 0.6), 'ISENSE', 'l')
        yI = yM + 0.6
        dv('R19', (XM + 1.5, yI), (XM + 1.5, yI - 2.8), t='l'); g((XM + 1.5, yI - 2.8))
        w((XM, yI), (XM + 1.5, yI))
        dv('R20', (XM + 1.5, yI), (XM + 5.0, yI), t='t')
        u4 = S.oa('U4', elm.Opamp(leads=True).flip().anchor('in2').at((XM + 8.0, yI)),
                  {'in1': '2', 'in2': '3', 'out': '1'}, 'U4A  MCP6002')
        a4 = u4.absanchors
        w((XM + 5.0, yI), a4['in2'])
        dv('C19', (XM + 5.8, yI), (XM + 5.8, yI - 2.6), t='l'); g((XM + 5.8, yI - 2.6))
        txt((XM + 5.0, yI + 0.15), 'NA', fontsize=6, color=ACC, halign='left', valign='bottom')
        xnm = a4['in1'][0] - 0.6
        yr22 = a4['in1'][1] - 2.0
        w(a4['in1'], (xnm, a4['in1'][1]), (xnm, yr22))
        xia = a4['out'][0] + 0.6
        dv('R22', (xnm, yr22), (xia, yr22), t='b')
        w(a4['out'], (xia, a4['out'][1]), (xia, yr22))
        dv('R21', (xnm, yr22), (xnm, yr22 - 2.6), t='l'); g((xnm, yr22 - 2.6))
        txt((xnm - 0.15, a4['in1'][1] - 0.1), 'NM', fontsize=6, color=ACC, halign='right', valign='top')
        yA = a4['out'][1]
        txt((xia + 0.2, yA + 0.15), 'IAMP', fontsize=6.5, color=ACC, halign='left', valign='bottom')
        # U5 komparator BIT (prag PRAG = PWM filtriran R23/C22)
        xu5r = xia + 3.0
        u5 = S.oa('U5', elm.Opamp(leads=True).anchor('in2').at((xu5r + 0.6, yA + 3.6)),
                  {'in1': '4', 'in2': '3', 'out': '1'}, 'U5  MCP6561')
        a5 = u5.absanchors
        w((xia, yA), (xu5r, yA), (xu5r, a5['in2'][1]), a5['in2'])
        xpf = a5['in1'][0] - 1.3
        w(a5['in1'], (xpf, a5['in1'][1]))
        dv('C22', (xpf, a5['in1'][1]), (xpf, a5['in1'][1] - 2.4), t='l'); g((xpf, a5['in1'][1] - 2.4))
        dv('R23', (xpf, a5['in1'][1]), (xpf - 3.6, a5['in1'][1]), t='t')
        tag((xpf - 3.6, a5['in1'][1]), 'PRAG', 'l')
        txt((xpf + 0.1, a5['in1'][1] + 0.15), 'PRAG_F', fontsize=6, color=ACC, halign='left', valign='bottom')
        w(a5['out'], (a5['out'][0] + 0.6, a5['out'][1])); tag((a5['out'][0] + 0.6, a5['out'][1]), 'BIT')
        # IAMP ka MCU
        xr26 = xia + 1.6 + 4.6
        # IAMP oznaka nadole
        w((xu5r + 1.0, yA), (xu5r + 1.0, yA - 3.0)); tag((xu5r + 1.0, yA - 3.0), 'IAMP', 'l')
        w((xu5r, yA), (xu5r + 1.0, yA))
        dv('R26', (xu5r + 1.0, yA), (xr26 + 0.6, yA), t='t')
        xoi = xr26 + 0.6
        # U6 zaštita
        u6 = S.oa('U6', elm.Opamp(leads=True).anchor('in2').at((xoi + 6.4, yA)),
                  {'in1': '4', 'in2': '3', 'out': '1'}, 'U6  MCP6561')
        a6 = u6.absanchors
        w((xoi, yA), a6['in2'])
        txt((xoi + 0.1, yA + 0.15), 'OC_IN', fontsize=6, color=ACC, halign='left', valign='bottom')
        # Q7 reset zadrške
        xq7 = xoi + 1.0
        w((xq7, yA), (xq7, yA - 0.8))
        q7 = S.tr('Q7', elm.NFet().reverse().anchor('drain').at((xq7, yA - 0.8)),
                  {'gate': '1', 'source': '2', 'drain': '3'}, t='r', ofs=(0, -0.3))
        g(q7.absanchors['source'])
        g7 = q7.absanchors['gate']
        n7 = (g7[0] - 0.5, g7[1])
        w(g7, n7)
        dv('R28', n7, (n7[0], n7[1] - 2.6), t='l'); g((n7[0], n7[1] - 2.6))
        w(n7, (n7[0] - 1.0, n7[1])); tag((n7[0] - 1.0, n7[1]), 'OC_RST', 'l')
        # C24
        xc24 = xoi + 3.4
        dv('C24', (xc24, yA), (xc24, yA - 2.6), t='r'); g((xc24, yA - 2.6))
        # referenca OC_REF
        xrf = a6['in1'][0] - 0.8
        yrf = a6['in1'][1] + 2.4
        w(a6['in1'], (xrf, a6['in1'][1]), (xrf, yrf))
        dv('R24', (xrf, yrf + 2.6), (xrf, yrf), t='r'); S.vcc((xrf, yrf + 2.6), '+3V3')
        w((xrf, yrf), (xrf - 1.6, yrf))
        dv('R25', (xrf - 1.6, yrf), (xrf - 1.6, yrf - 2.0), t='l'); g((xrf - 1.6, yrf - 2.0))
        txt((xrf + 0.15, yrf - 0.1), 'OC_REF\n1,435 V', fontsize=6, color=ACC, halign='left', valign='top')
        # izlaz OCP, zadrška D4 + R27
        xop = a6['out'][0] + 0.8
        w(a6['out'], (xop, a6['out'][1]))
        w((xop, a6['out'][1]), (xop + 1.0, a6['out'][1])); tag((xop + 1.0, a6['out'][1]), 'OCP')
        yzd = yA - 5.0
        xr27 = xc24 + 1.6
        w((xop, a6['out'][1]), (xop, yzd))
        dv('D4', (xop, yzd), (xop - 3.6, yzd), t='b')
        dv('R27', (xop - 3.6, yzd), (xr27, yzd), t='b')
        w((xr27, yzd), (xr27, yA))
        txt((xop - 3.6, yzd + 0.15), 'OC_FB', fontsize=6, color=ACC, halign='center', valign='bottom')
        txt((XM, yzd - 2.2),
            'IAMP = 5,02·I·1 Ω  (R22/R21: 1+40k2/10k).  BIT: IAMP > PRAG_F (PWM GP16 → R23/C22).\n'
            'OCP: IAMP > 1,435 V ⇒ I > ≈285 mA; D4+R27 drže OC_IN visoko (zadrška) dok MCU ne da OC_RST (Q7).\n'
            'OCP → Q6 gasi VSET (hardverski), i ide na GP6.  Q4 + R13 2 Ω: strujni limit ≈325 mA.',
            fontsize=6, color=SIVA, halign='left', valign='top')

        # napajanje OP/komparatora i blokada
        yP = 8.0
        xP = XM + 1.0
        naslov((XM - 1, yP + 4.8), 'NAPAJANJE OP / KOMPARATORA')
        for ref, vp, vn, cref, ime in (('U4', '8', '4', 'C20', 'U4C MCP6002'), ('U5', '5', '2', 'C21', 'U5'),
                                       ('U6', '5', '2', 'C23', 'U6')):
            e = S.ic(ref, {'top': [(vp, 'V+')], 'bottom': [(vn, 'V−')]}, naziv=ime, pinspacing=1.0, edgepadW=0.5, rot=0,
                     edgepadH=0.4)
            e = d.add(e.theta(0).anchor('p' + vp).at((xP, yP + 2.6)))
            S._pin(ref, vp, e.absanchors['p' + vp]); S._pin(ref, vn, e.absanchors['p' + vn])
            S.vcc((xP, yP + 2.6), '+3V3'); g(e.absanchors['p' + vn])
            w((xP, yP + 2.6), (xP + 1.8, yP + 2.6))
            dv(cref, (xP + 1.8, yP + 2.6), (xP + 1.8, yP), t='r'); g((xP + 1.8, yP))
            xP += 7.0
        # U4B nekorišćen: sledilac sa + na masi
        u4b = S.oa('U4', elm.Opamp(leads=True).anchor('in1').at((xP + 0.6, yP + 2.0)),
                   {'in1': '6', 'in2': '5', 'out': '7'}, 'U4B (ne koristi se)', t_ofs=(0, 0.9))
        b4 = u4b.absanchors
        w(b4['in1'], (b4['in1'][0] - 0.5, b4['in1'][1]), (b4['in1'][0] - 0.5, b4['in1'][1] + 1.2),
          (b4['out'][0] + 0.5, b4['in1'][1] + 1.2), (b4['out'][0] + 0.5, b4['out'][1]), b4['out'])
        w(b4['in2'], (b4['in2'][0] - 0.5, b4['in2'][1])); g((b4['in2'][0] - 0.5, b4['in2'][1]))

        # =====================================================================================================
        # 8 RP2040 + FLASH + KVARC
        # =====================================================================================================
        X7 = 30.0
        Y7 = 21.0
        naslov((3, Y7 + 7.4), '8  RP2040 + W25Q16JV + 12 MHz   (GPIO isti kao apollo-loop-driver; GP0/GP1 = UART0)')
        lev = [('1', 'IOVDD'), ('10', 'IOVDD'), ('22', 'IOVDD'), ('33', 'IOVDD'), ('42', 'IOVDD'), ('49', 'IOVDD'),
               ('48', 'USB_VDD'), ('43', 'ADC_AVDD'), ('44', 'VREG_VIN'), None,
               ('45', 'VREG_VOUT'), ('23', 'DVDD'), ('50', 'DVDD'), None, None, None,
               ('47', 'USB_DP'), ('46', 'USB_DM'), None, None, None, None, None, None, None, None, None,
               ('20', 'XIN'), ('21', 'XOUT'), None, None, None, None, None, None]
        gp = [('2', 0), ('3', 1), ('4', 2), ('5', 3), ('6', 4), ('7', 5), ('8', 6), ('9', 7), ('11', 8), ('12', 9),
              ('13', 10), ('14', 11), ('15', 12), ('16', 13), ('17', 14), ('18', 15), ('27', 16), ('28', 17),
              ('29', 18), ('30', 19), ('31', 20), ('32', 21), ('34', 22), ('35', 23), ('36', 24), ('37', 25),
              ('38', 26), ('39', 27), ('40', 28), ('41', 29)]
        ADC = {26: '/ADC0', 27: '/ADC1', 28: '/ADC2', 29: '/ADC3'}
        des = [(pn, 'GPIO%d%s' % (n, ADC.get(n, ''))) for pn, n in gp[:7]] + [None] + \
              [(pn, 'GPIO%d%s' % (n, ADC.get(n, ''))) for pn, n in gp[7:]] + [None, ('24', 'SWCLK'), ('25', 'SWDIO'),
                                                                             ('26', 'RUN')]
        lev.append(None); des.append(None)
        assert len(lev) == len(des), (len(lev), len(des))
        dno = [('57', 'GND'), ('19', 'TESTEN'), None, ('53', 'QSPI_SD0'), ('55', 'QSPI_SD1'), ('54', 'QSPI_SD2'),
               ('51', 'QSPI_SD3'), ('52', 'QSPI_SCLK'), ('56', 'QSPI_SS'), None]
        u7 = S.ic('U7', {'left': lev, 'right': des, 'bottom': dno}, pinspacing=0.8, edgepadW=1.4, edgepadH=0.6)
        u7 = S.ic_dodaj('U7', u7.anchor('p1').at((X7, Y7)))
        r = u7.absanchors
        xL = r['p1'][0]
        # +3V3 pinovi -> sabirnica -> blokada iznad
        xb = xL - 1.2
        for k in ('1', '10', '22', '33', '42', '49', '48', '43', '44'):
            w(r['p' + k], (xb, r['p' + k][1]))
        ytop = Y7 + 4.6
        w((xb, r['p44'][1]), (xb, ytop))
        xc = xb + 1.6
        blok = [('C31', 'IOVDD 1'), ('C28', 'IOVDD 10'), ('C40', 'IOVDD 22'), ('C29', 'IOVDD 33'), ('C38', 'IOVDD 42'),
                ('C30', 'USB_VDD 48\n+IOVDD 49'), ('C39', 'ADC_AVDD 43'), ('C32', 'VREG_VIN 44')]
        for ref, opis in blok:
            dv(ref, (xc, ytop), (xc, ytop - 2.2), t='r'); g((xc, ytop - 2.2))
            xc += 2.1
        w((xb - 2.0, ytop), (xc - 2.1, ytop))
        S.vcc((xb - 2.0, ytop), '+3V3')
        txt((xb + 1.0, ytop + 0.25), 'blokada 100n uz svaki IOVDD, 1µ uz VREG_VIN (RP2040 datasheet 2.10)',
            fontsize=6, color=SIVA, halign='left', valign='bottom')
        # DVDD
        xdv = xL - 1.2
        w(r['p45'], (xdv, r['p45'][1])); w(r['p23'], (xdv, r['p23'][1])); w(r['p50'], (xdv, r['p50'][1]))
        w((xdv, r['p45'][1]), (xdv, r['p50'][1]))
        xdc = xL - 3.6
        w((xdv, r['p45'][1]), (xdc - 4.4, r['p45'][1]))
        for ref in ('C34', 'C33', 'C41'):
            dv(ref, (xdc, r['p45'][1]), (xdc, r['p45'][1] - 2.2), t='r'); g((xdc, r['p45'][1] - 2.2))
            xdc -= 2.2
        txt((xL - 3.0, r['p45'][1] + 0.15), 'DVDD 1,1 V', fontsize=6, color=ACC, halign='left', valign='bottom')
        # USB
        dv('R33', r['p47'], (xL - 3.6, r['p47'][1]), t='t'); tag((xL - 3.6, r['p47'][1]), 'DP_H', 'l')
        dv('R34', r['p46'], (xL - 3.6, r['p46'][1]), t='b'); tag((xL - 3.6, r['p46'][1]), 'DM_H', 'l')
        # kvarc
        yxi, yxo = r['p20'][1], r['p21'][1]
        xy1 = xL - 7.0
        xr32 = xL - 3.4
        w(r['p20'], (xy1 - 3.2, yxi))
        w(r['p21'], (xr32, yxo))
        dv('R32', (xr32, yxo), (xr32, yxo - 2.4), t='r')
        yxo2 = yxo - 2.4
        w((xr32, yxo2), (xy1 - 0.0, yxo2))
        y1 = dv('Y1', (xy1, yxi), (xy1, yxo2), t='l', ofs=0.0)
        txt((xr32 + 0.2, yxo2 + 0.05), 'XO', fontsize=6, color=ACC, halign='left', valign='bottom')
        cyy = (yxi + yxo2) / 2
        w((xy1 + 0.45, cyy), (xy1 + 1.2, cyy)); g((xy1 + 1.2, cyy))
        S.pin_rucno('Y1', '2', (xy1 + 0.45, cyy)); S.pin_rucno('Y1', '4', (xy1 + 0.45, cyy))
        txt((xy1 + 0.5, cyy + 0.1), '2,4', fontsize=5.5, color=SIVA, halign='left', valign='bottom')
        dv('C26', (xy1 - 3.2, yxi), (xy1 - 3.2, yxi - 2.4), t='l'); g((xy1 - 3.2, yxi - 2.4))
        dv('C27', (xy1 + 1.8, yxo2), (xy1 + 1.8, yxo2 - 2.4), t='r'); g((xy1 + 1.8, yxo2 - 2.4))
        w((xy1, yxo2), (xy1 + 1.8, yxo2))
        # GND, TESTEN
        yg7 = r['p57'][1] - 0.8
        w(r['p57'], (r['p57'][0], yg7)); w(r['p19'], (r['p19'][0], yg7)); w((r['p57'][0], yg7), (r['p19'][0], yg7))
        g((r['p57'][0], yg7))
        # flash U8 ispod
        u8 = S.ic('U8', {'top': [('5', 'IO0'), ('2', 'IO1'), ('3', 'IO2'), ('7', 'IO3'), ('6', 'CLK'), ('1', '/CS')],
                         'left': [('8', 'VCC')], 'bottom': [('4', 'GND')]}, pinspacing=0.8, edgepadW=0.6,
                  edgepadH=0.7)
        u8 = S.ic_dodaj('U8', u8.anchor('p5').at((r['p53'][0], r['p53'][1] - 5.0)))
        f = u8.absanchors
        for a, b in (('53', '5'), ('55', '2'), ('54', '3'), ('51', '7'), ('52', '6'), ('56', '1')):
            w(r['p' + a], f['p' + b])
        g(f['p4'])
        w(f['p8'], (f['p8'][0] - 1.0, f['p8'][1]))
        S.vcc((f['p8'][0] - 1.0, f['p8'][1]), '+3V3')
        dv('C25', (f['p8'][0] - 1.0, f['p8'][1]), (f['p8'][0] - 1.0, f['p8'][1] - 2.4), t='l')
        g((f['p8'][0] - 1.0, f['p8'][1] - 2.4))
        # QSS: R29 pull-up, R30 -> BOOT
        xss_ = r['p56'][0]
        y29, y30 = r['p56'][1] - 1.4, r['p56'][1] - 3.0
        dv('R30', (xss_, y29), (xss_ + 3.4, y29), t='t'); tag((xss_ + 3.4, y29), 'BOOT')
        dv('R29', (xss_, y30), (xss_ + 3.4, y30), t='b')
        w((xss_ + 3.4, y30), (xss_ + 6.4, y30)); S.vcc((xss_ + 6.4, y30), '+3V3')
        txt((xss_ + 0.2, y29 + 0.85), 'QSS', fontsize=6, color=ACC, halign='left', valign='bottom')
        # desna strana: GPIO
        xR = r['p2'][0]
        sig = {'2': 'TX', '3': 'RX', '4': 'NIVO', '5': 'EN_N', '6': 'BIT', '7': 'OC_RST', '8': 'OCP',
               '27': 'PRAG', '38': 'IAMP', '39': 'VLOOP', '40': 'VRET', '24': 'SWCLK', '25': 'SWDIO'}
        for pn, ime in sig.items():
            w(r['p' + pn], (xR + 1.4, r['p' + pn][1])); tag((xR + 1.4, r['p' + pn][1]), ime)
        # LED
        dv('R35', r['p37'], (xR + 3.6, r['p37'][1]), t='t')
        dv('D5', (xR + 3.6, r['p37'][1]), (xR + 6.2, r['p37'][1]), t='b', ofs=0.3)
        g((xR + 6.2, r['p37'][1]))
        txt((xR + 3.7, r['p37'][1] - 0.2), 'LED_A', fontsize=5.5, color=ACC, halign='left', valign='top')
        # RUN: R31 pull-up + oznaka
        nr = (xR + 1.2, r['p26'][1])
        w(r['p26'], nr)
        dv('R31', nr, (nr[0] + 3.4, nr[1]), t='t')
        S.vcc((nr[0] + 3.4, nr[1]), '+3V3')
        w(nr, (nr[0], nr[1] - 1.2)); tag((nr[0], nr[1] - 1.2), 'RUN')
        # nekorišćeni GPIO
        for pn, n in gp:
            if pn not in sig and pn != '37':
                S.nepovezan('U7', pn)

        # =====================================================================================================
        # 9 LETVICA J1 2x14 (donja strana, ka matičnoj ploči)
        # =====================================================================================================
        J = P['J1'][2]
        imena = {'+24V_IN': '24V', 'GND': 'GND', '+3V3': '3V3', 'DP_H': 'USB D+', 'DM_H': 'USB D−'}
        lj = [(str(i), imena.get(J[str(i)], J[str(i)])) for i in range(1, 29)]
        j1 = S.ic('J1', {'right': lj}, naziv=' ', pinspacing=0.8, edgepadW=1.0,
                  edgepadH=0.5)
        XJ, YJ = 104.0, 31.0
        j1 = S.ic_dodaj('J1', j1.anchor('p1').at((XJ, YJ)))
        jj = j1.absanchors
        xj = jj['p1'][0]
        naslov((xj - 6.5, YJ + 1.6), '9  LETVICA J1 – MATIČNA 2×14, 2,54 mm (donja strana)')
        txt((xj - 2.0, jj['p28'][1] - 1.0), 'J1  MATICNA 2x14', fontsize=8.5, halign='center', valign='top')
        grupe = {}
        for i in range(1, 29):
            grupe.setdefault(J[str(i)], []).append(str(i))
        for net, pins in grupe.items():
            if net == 'GND':
                for pn in pins:
                    w(jj['p' + pn], (xj + 1.2, jj['p' + pn][1])); g((xj + 1.2, jj['p' + pn][1]))
                continue
            # spojeni pinovi iste mreže
            for pn in pins:
                w(jj['p' + pn], (xj + 1.0, jj['p' + pn][1]))
            if len(pins) > 1:
                w((xj + 1.0, jj['p' + pins[0]][1]), (xj + 1.0, jj['p' + pins[-1]][1]))
            y0 = jj['p' + pins[0]][1]
            w((xj + 1.0, y0), (xj + 2.4, y0))
            if net == '+3V3':
                S.vcc((xj + 2.4, y0), '+3V3')
            else:
                tag((xj + 2.4, y0), net)

        # =====================================================================================================
        # naslov / napomene
        # =====================================================================================================
        txt((3, -24.0),
            'APOLLO LOOP DRIVER MODUL v0.1 — kompletna električna šema (jedan list).  Samo laboratorija: nije protivpožarni '
            'uređaj, nije sertifikovano (EN 54).\n'
            'Netlista = hardware/pcb/make_pcb.py (P); ova šema je proverena skriptom prema njoj (svi pinovi, mreže, NC).  '
            'Mreže istog imena (zastavice, +3V3, +34V, GND) su spojene.\n'
            'Pinovi: TPS55340PWP i TPS560430X3F po TI datasheet-u; MJD122 1 B, 2/tab C, 3 E; SOT-23 1 B/G, 2 E/S, 3 C/D; '
            'MCP6561 1 OUT 2 VSS 3 + 4 − 5 VDD; OPA197/MCP6002 SOIC-8 standard.',
            fontsize=7, halign='left', valign='top')

        greske, upoz = S.proveri()
        return greske, upoz


if __name__ == '__main__':
    schemdraw.use('svg')
    greske, upoz = crtaj('kompletna.svg')
    for u in upoz:
        print('UPOZORENJE:', u)
    for e in greske:
        print('GRESKA:', e)
    print('%d grešaka, %d upozorenja' % (len(greske), len(upoz)))
    schemdraw.use('matplotlib')
    crtaj('kompletna.png')
    sys.exit(1 if greske else 0)
