# Komandna linija preko USB serijskog porta (115200, bilo koji terminal ili Thonny).
#   on | off | status
#   poll <adresa> [komanda]      npr. poll 5
#   scan [od] [do]               npr. scan 1 20
#   sniff [ms]                   slusa pravu centralu (drajver ugasen)
#   set <IME> <vrednost>         npr. set T_JEDAN 650   (menja config u RAM-u)
#   get                          ispise sva vremena okvira

import sys
import config as C
from loopdrv import Drajver, analiziraj

d = Drajver()
print("Apollo XP95 drajver spreman. Petlja je UGASENA. Komande: on, off, status, poll, scan, sniff, set, get")


def _sniff(ms):
    (t, v, i), err = d.sniff(ms)
    if err:
        print("GRESKA", err)
        return
    vmin, vmax = min(v), max(v)
    imp_v = analiziraj(t, v, (vmin + vmax) // 2)
    i_mir = sorted(i)[len(i) // 2]
    prag_i = i_mir + int(C.PRAG_IZNAD_MA / 1000 * C.SHUNT_OHM * C.IAMP_GAIN / C.VREF * 65535)
    imp_i = analiziraj(t, i, prag_i)
    print("UZORAKA %d za %d ms (%.1f us/uzorak)" % (len(t), ms, t[-1] / len(t)))
    print("NAPON  min %.1f V  max %.1f V" % (vmin / 65535 * C.VREF * C.DIV_V, vmax / 65535 * C.VREF * C.DIV_V))
    print("NAPONSKI IMPULSI (pocetak_us, sirina_us, pauza_pre_us):")
    for p in imp_v:
        print("V", *p)
    print("STRUJNI IMPULSI:")
    for p in imp_i:
        print("I", *p)
    print("KRAJ")


while True:
    try:
        red = sys.stdin.readline().strip().split()
    except KeyboardInterrupt:
        break
    if not red:
        continue
    k, a = red[0].lower(), red[1:]
    try:
        if k == "on":
            print(d.ukljuci())
        elif k == "off":
            d.iskljuci()
            print(d.status())
        elif k == "status":
            print(d.status())
        elif k == "poll":
            print(d.prozovi(int(a[0]), int(a[1]) if len(a) > 1 else 0))
        elif k == "scan":
            nadjeni, err = d.skeniraj(int(a[0]) if a else 1, int(a[1]) if len(a) > 1 else 126)
            for r in nadjeni:
                print(r)
            print("NADJENO %d%s" % (len(nadjeni), (" GRESKA " + err) if err else ""))
        elif k == "sniff":
            _sniff(int(a[0]) if a else 200)
        elif k == "set":
            setattr(C, a[0], int(a[1]))
            print(a[0], "=", getattr(C, a[0]))
        elif k == "get":
            for ime in sorted(dir(C)):
                if ime.startswith("T_") or ime.startswith("ODGOVOR") or ime in ("MSB_PRVI", "N_ODGOVOR",
                                                                                 "HIGH_JE_IMPULS"):
                    print(ime, getattr(C, ime))
        else:
            print("nepoznata komanda")
    except Exception as e:
        d.iskljuci("izuzetak: %r" % e)
        print("GRESKA", repr(e), "- petlja ugasena")
