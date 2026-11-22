"""Rutiranje Apollo modula po mom planu (ne autorouter): prioriteti, redosled, širine, razmaci, slojevi.

Motor (tools/ruter/motor.py, GPU talasno širenje + rip-up) samo nalazi geometriju svake veze po ovim pravilima.
Tok:  python make_pcb.py  ->  python rutiraj.py  ->  python finish_pcb.py  ->  kicad-cli pcb drc
Pregled uživo: python tools/ruter/pregled.py  ->  http://127.0.0.1:8765

Pravila (dobra praksa):
  - prvo funkcionalne celine u kojima blizina i masa odlučuju: boost i buck (strujni putevi su već ručno nacrtani
    u make_pcb.py), GND via tik uz svaki kondenzator konvertera, pa njihov analogni deo (FB, COMP, FREQ, SS)
  - zatim MCU celina (kristal, QSPI, USB, blokada sa sopstvenim GND via), pa raspodela napajanja,
    izlazni stepen i petlja (34 V, razmak 0,3 mm), analogno merenje i na kraju dugi GPIO signali
  - prioritet: mreža sme da ukloni (rip-up) samo mrežu istog ili manjeg značaja; zaključani vodovi se ne diraju
  - F.Cu je sloj za vodove; B.Cu je masa – samo za ukrštanja (skuplji) i nikad ispod konvertera (MASA_B)
"""
import os
import sys

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(OVDE, '../../../../tools/ruter'))
from motor import Ruter, GPU  # noqa: E402

IME = 'apollo_module'
VISOKI = ['+34V', 'SW', 'NE', 'NB', 'U3OUT', 'LOOP_DRV', 'LOOP_OUT', 'LOOP_IN', 'PE']   # isto kao .kicad_dru


def p(ime, sirine, prio, **kw):
    kw['prioritet'] = prio
    return (ime, sirine, kw)


def gnd(refs, opis, prio=1):
    return ('GND_FANOUT', set(refs) if refs else None, dict(opis=opis, prioritet=prio))


SIG = [0.2]
HV = dict(razmak=0.3)

PLAN = [
    # ---- 1. KONVERTERI: masa i blizina (prioritet 1)
    gnd(['C1', 'C2', 'C9', 'C35', 'C36', 'C3', 'C4', 'C5'], 'boost: ulazni i izlazni kondenzatori'),
    gnd(['C37', 'C11', 'C12', 'C13'], 'buck: Cin i Cout'),
    p('SW', [0.8, 0.6], 1), p('SW3', [0.5, 0.4], 1), p('CB', [0.4, 0.3], 1),          # provera ručno nacrtanih
    p('BFB', SIG, 1), p('COMP', SIG, 1), p('CC', SIG, 1), p('FREQ', SIG, 1), p('SS', SIG, 1),
    gnd(['R2', 'R3', 'C6', 'C7', 'C8'], 'boost: analogna masa uz FB/COMP/FREQ/SS'),
    # ---- 2. MCU celina i napajanja (prioritet 2)
    p('XIN', SIG, 2), p('XOUT', SIG, 2), p('XO', SIG, 2),
    p('QSCLK', SIG, 2), p('QSS', SIG, 2), p('QSD0', SIG, 2), p('QSD1', SIG, 2), p('QSD2', SIG, 2), p('QSD3', SIG, 2),
    p('USB_DP', SIG, 2), p('USB_DM', SIG, 2),
    gnd(['C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C38', 'C39', 'C40', 'C41', 'C25', 'C26', 'C27', 'U8', 'U7'],
        'MCU: blokada i kristal', 2),
    p('DVDD', [0.3, 0.25, 0.2], 2),
    p('+24V_IN', [1.0, 0.8, 0.6], 2), p('VIN_F', [1.0, 0.8, 0.6], 2),
    p('VIN', [0.8, 0.6, 0.5, 0.4], 2, cena_B=3.0),
    p('+34V', [0.6, 0.5, 0.4, 0.3], 2, cena_B=3.0, **HV),
    p('+3V3', [0.4, 0.3, 0.25, 0.2], 2, cena_B=2.5),
    # ---- 3. izlazni stepen i petlja, 34 V (prioritet 3)
    p('NE', [0.8, 0.6, 0.4], 3, **HV), p('LOOP_DRV', [0.6, 0.5, 0.4], 3, **HV), p('PE', [0.4, 0.3], 3, **HV),
    p('NB', [0.3, 0.25], 3, **HV), p('U3OUT', [0.3, 0.25], 3, **HV),
    p('LOOP_OUT', [0.6, 0.5, 0.4], 3, **HV), p('LOOP_IN', [0.5, 0.4, 0.3], 3, **HV), p('ISENSE', [0.6, 0.5, 0.4], 3),
    gnd(['C15', 'C16', 'R12', 'Q5', 'D3'], 'izlazni stepen i TVS', 3),
    # ---- 4. analogno: VSET, povratna sprega, merenje i zaštita (prioritet 4)
    p('VSET', [0.25, 0.2], 4), p('FB', SIG, 4), p('Q2D', SIG, 4), p('NIVO_G', SIG, 4),
    p('NA', SIG, 4), p('NM', SIG, 4), p('IAMP', [0.25, 0.2], 4), p('U4B', SIG, 4), p('PRAG_F', SIG, 4),
    p('OC_IN', SIG, 4), p('OC_REF', SIG, 4), p('OC_FB', SIG, 4), p('VLOOP', SIG, 4), p('VRET', SIG, 4),
    p('LED_A', SIG, 4),
    # ---- 5. dugi GPIO signali RP2040 i letvica (prioritet 5)
    p('OCP', SIG, 5), p('OC_RST', SIG, 5), p('BIT', SIG, 5), p('PRAG', SIG, 5), p('NIVO', SIG, 5), p('EN_N', SIG, 5),
    p('LED', SIG, 5), p('TX', SIG, 5), p('RX', SIG, 5), p('RUN', SIG, 5), p('BOOT', SIG, 5),
    p('SWCLK', SIG, 5), p('SWDIO', SIG, 5), p('DP_H', SIG, 5), p('DM_H', SIG, 5),
    # ---- 6. ostali padovi mase
    gnd(None, 'ostali', 6),
]

if __name__ == '__main__':
    os.chdir(OVDE)
    if os.path.exists(IME + '.ses'):
        os.remove(IME + '.ses')          # stari Freerouting rezultat se više ne koristi
    r = Ruter(IME + '.kicad_pcb', visoki=VISOKI)
    r.log('Plan: %d koraka, %s' % (len(PLAN), 'GPU' if GPU else 'CPU'))
    neuspele = r.izvrsi(PLAN)
    r.snimi()
    r.log('Nepovezane mreže: %s' % (', '.join(neuspele) if neuspele else 'nema'), 'e' if neuspele else 'ok')
