"""Dopunski prolaz na već izrutiranoj ploči: zadate mreže idu prve sa višim prioritetom (smeju da uklone manje važne
vodove koji ih blokiraju); uklonjene mreže se vraćaju u red i ponovo rutiraju. Već povezane mreže se preskaču.

Pokretanje:  RUTER_CPU=1 python rutiraj_dopuna.py NIVO[:prio] [MREZA[:prio] ...]   (podrazumevani prioritet 2)
"""
import os
import sys

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDE)
import rutiraj as R  # noqa: E402   (PLAN, VISOKI, IME; __main__ deo se ne izvršava)

zadate = {}
for a in sys.argv[1:]:
    ime, _, pr = a.partition(':')
    zadate[ime] = int(pr or 2)
plan_po_imenu = {s[0]: s for s in R.PLAN if s[0] != 'GND_FANOUT'}
prvi = []
for ime, pr in zadate.items():
    _, sir, kw = plan_po_imenu[ime]
    kw = dict(kw, prioritet=pr)
    if os.environ.get('CENA_B'):                 # skuplji B sloj: signal ostaje na F i ne seče masu
        kw['cena_B'] = float(os.environ['CENA_B'])
    prvi.append((ime, sir, kw))
ostali = [s for s in R.PLAN if s[0] != 'GND_FANOUT' and s[0] not in zadate]

if __name__ == '__main__':
    os.chdir(OVDE)
    r = R.Ruter(R.IME + '.kicad_pcb', visoki=R.VISOKI)
    r.log('Dopuna: %s prvo, zatim provera ostalih %d mreža' % (', '.join(zadate), len(ostali)))
    neuspele = r.izvrsi(prvi + ostali)
    r.snimi()
    r.log('Nepovezane mreže: %s' % (', '.join(neuspele) if neuspele else 'nema'), 'e' if neuspele else 'ok')
