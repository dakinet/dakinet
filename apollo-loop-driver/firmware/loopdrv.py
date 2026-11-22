# Apollo XP95 laboratorijski drajver - MicroPython za Raspberry Pi Pico (RP2040)
#
# Vremenski kriticne stvari rade u hardveru:
#   - PIO SM0 menja NIVO pin po listi (nivo, trajanje_us), hranjen preko DMA
#   - PIO SM1 uzorkuje NIVO, /EN i BIT pinove na svakih T_UZORAK us, prazni ga DMA
# Python samo slaze okvir, pokrece prenos i dekodira uzorke.
#
# Samo za laboratorijsku petlju. Uredjaj nije sertifikovan po EN 54.

import array
import time
import rp2
from machine import Pin, ADC, PWM, Timer

import config as C

T_UZORAK = 20          # us po uzorku (50 kHz)
UZ_PO_RECI = 10        # 10 uzoraka x 3 bita = 30 bita po reci


# ---------------------------------------------------------------- PIO programi

@rp2.asm_pio(out_init=rp2.PIO.OUT_HIGH, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def _pio_segmenti():
    # rec = nivo (bit 0) | (broj_ciklusa << 1); 1 ciklus = 1 us
    pull(block)
    out(pins, 1)
    out(x, 31)
    label("cekaj")
    jmp(x_dec, "cekaj")


@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, autopush=True, push_thresh=30)
def _pio_uzorci():
    in_(pins, 3)        # GP2 NIVO, GP3 /EN, GP4 BIT


def _rec(nivo, us):
    # 3 ciklusa (pull, out, out) + petlja od x+1 ciklusa
    return (nivo & 1) | (max(us - 4, 0) << 1)


# ---------------------------------------------------------------- pomocne

def _v_iz_adc(raw, delitelj):
    return raw / 65535 * C.VREF * delitelj


def _ma_iz_adc(raw):
    v = raw / 65535 * C.VREF
    return v / C.IAMP_GAIN / C.SHUNT_OHM * 1000.0


def _bitovi(vrednost, n):
    r = [(vrednost >> i) & 1 for i in range(n)]
    return r[::-1] if C.MSB_PRVI else r


def _vrednost(bitovi):
    b = bitovi if C.MSB_PRVI else bitovi[::-1]
    v = 0
    for x in b:
        v = (v << 1) | x
    return v


# ---------------------------------------------------------------- drajver

class Drajver:
    def __init__(self):
        self.en_n = Pin(C.PIN_EN_N, Pin.OUT, value=1)       # petlja ugasena
        self.nivo = Pin(C.PIN_NIVO, Pin.OUT, value=1)       # osnovni nivo
        self.bit = Pin(C.PIN_BIT, Pin.IN)
        self.oc_rst = Pin(C.PIN_OC_RST, Pin.OUT, value=1)    # zastita obrisana dok petlja ne krene
        self.oc_flag = Pin(C.PIN_OC_FLAG, Pin.IN)
        self.adc_i = ADC(C.ADC_IAMP)
        self.adc_v = ADC(C.ADC_VLOOP)
        self.adc_r = ADC(C.ADC_VRET)
        self.prag = PWM(Pin(C.PIN_PRAG))
        self.prag.freq(100_000)
        self.prag.duty_u16(65535)                           # prag na vrhu dok se ne izmeri
        self.sm_drv = rp2.StateMachine(0, _pio_segmenti, freq=1_000_000, out_base=self.nivo)
        self.sm_uz = rp2.StateMachine(1, _pio_uzorci, freq=1_000_000 // T_UZORAK,
                                      in_base=Pin(C.PIN_NIVO))
        self.ukljucena = False
        self.greska = None
        self._nisko = 0
        self._tajmer = Timer(period=1, mode=Timer.PERIODIC, callback=self._zastita)

    # ---- zastita: gasi petlju kod kratkog spoja ili preopterecenja
    def _zastita(self, _t):
        if not self.ukljucena:
            return
        if self.oc_flag.value():
            # hardver (U12 + Q6) je vec ugasio petlju za nekoliko us; ovde samo belezimo kvar
            self.iskljuci("kratak spoj ili preopterecenje > %.0f mA" % C.I_MAX_MA)
            return
        v = _v_iz_adc(self.adc_v.read_u16(), C.DIV_V)
        if v < C.V_MIN_PETLJE:
            self._nisko += 1
            if self._nisko >= C.V_MIN_MS:
                self.iskljuci("napon petlje %.1f V < %.1f V" % (v, C.V_MIN_PETLJE))
        else:
            self._nisko = 0

    def ukljuci(self):
        self.greska = None
        self._nisko = -50                 # 50 ms da se izlaz podigne
        self.oc_rst.value(1)              # obrisi zadrsku zastite
        self.nivo.value(1)
        self.en_n.value(0)
        self.ukljucena = True
        time.sleep_ms(C.OC_BLANK_MS)      # kapacitet petlje se puni kroz ogranicenje Q4 (~540 mA)
        self.oc_rst.value(0)              # hardverska zastita aktivna
        time.sleep_ms(100 - C.OC_BLANK_MS)
        s = self.status()
        if s["i_ma"] > C.I_MAX_MA:
            self.iskljuci("struja mirovanja %.1f mA > %.0f mA" % (s["i_ma"], C.I_MAX_MA))
        return self.status()

    def iskljuci(self, razlog=None):
        self.en_n.value(1)
        self.oc_rst.value(1)
        self.ukljucena = False
        if razlog:
            self.greska = razlog

    def status(self):
        v = _v_iz_adc(self._sr(self.adc_v), C.DIV_V)
        r = _v_iz_adc(self._sr(self.adc_r), C.DIV_V)
        return {
            "ukljucena": self.ukljucena,
            "v_petlje": round(v, 2),
            "v_povratak": round(r, 2),
            "i_ma": round(_ma_iz_adc(self._sr(self.adc_i)), 2),
            "kratak_spoj": bool(self.oc_flag.value()),
            "prekid_petlje": self.ukljucena and r < C.PREKID_ODNOS * v,
            "greska": self.greska,
        }

    @staticmethod
    def _sr(adc, n=32):
        s = 0
        for _ in range(n):
            s += adc.read_u16()
        return s // n

    def _postavi_prag(self):
        i0 = _ma_iz_adc(self._sr(self.adc_i, 64))
        v = (i0 + C.PRAG_IZNAD_MA) / 1000.0 * C.SHUNT_OHM * C.IAMP_GAIN
        self.prag.duty_u16(min(65535, int(v / C.VREF * 65535)))
        return i0

    # ---- okvir
    @staticmethod
    def _nivoi():
        # (HIGH, LOW) iz dokumenta -> vrednost NIVO pina (1 = 24 V, 0 = 31 V)
        h = 0 if C.HIGH_JE_IMPULS else 1
        return h, 1 - h

    def okvir(self, adresa, komanda=0):
        # INIT HIGH, pa za svaki bit: LOW (trajanje nosi 0/1) + HIGH marker;
        # zatim 21 prijemni bit: LOW T_CITANJE (uredjaj odgovara strujom) + HIGH marker; na kraju LOW.
        h, l = self._nivoi()
        s = [(l, 300), (h, C.T_INIT)]
        for b in _bitovi(komanda, 3) + _bitovi(adresa, 7):
            s.append((l, C.T_JEDAN if b else C.T_NULA))
            s.append((h, C.T_MARKER))
        for _ in range(C.N_ODGOVOR):
            s.append((l, C.T_CITANJE))
            s.append((h, C.T_MARKER))
        s.append((l, 500))
        return s

    def _posalji(self, segmenti):
        reci = array.array("I", [_rec(n, us) for n, us in segmenti])
        ukupno = sum(us for _, us in segmenti) + 1000
        n_reci = ukupno // (T_UZORAK * UZ_PO_RECI) + 2
        uz = array.array("I", bytes(4 * n_reci))

        for sm in (self.sm_drv, self.sm_uz):
            sm.active(0)
            sm.restart()
        dma_uz, dma_drv = rp2.DMA(), rp2.DMA()
        try:
            dma_uz.config(read=self.sm_uz, write=uz, count=n_reci,
                          ctrl=dma_uz.pack_ctrl(size=2, inc_read=False, treq_sel=5), trigger=True)
            self.sm_uz.active(1)
            dma_drv.config(read=reci, write=self.sm_drv, count=len(reci),
                           ctrl=dma_drv.pack_ctrl(size=2, inc_write=False, treq_sel=0), trigger=True)
            self.sm_drv.active(1)
            rok = time.ticks_add(time.ticks_ms(), ukupno // 1000 + 200)
            while (dma_uz.active() or dma_drv.active()) and time.ticks_diff(rok, time.ticks_ms()) > 0:
                time.sleep_ms(1)
        finally:
            self.sm_drv.active(0)
            self.sm_uz.active(0)
            self.nivo.init(Pin.OUT, value=1)     # vrati pin na osnovni nivo
            self.sm_drv = rp2.StateMachine(0, _pio_segmenti, freq=1_000_000, out_base=self.nivo)
            dma_uz.close()
            dma_drv.close()

        nivo, bit = bytearray(), bytearray()
        for w in uz:
            for k in range(UZ_PO_RECI):
                x = (w >> (27 - 3 * k)) & 7
                nivo.append(x & 1)
                bit.append((x >> 2) & 1)
        return nivo, bit

    @staticmethod
    def _impulsi(nivo, h=0):
        # impuls = niz uzoraka sa NIVO = h (HIGH iz dokumenta); vraca (pocetak, kraj) u uzorcima
        r, start = [], None
        for i, n in enumerate(nivo):
            if n == h and start is None:
                start = i
            elif n != h and start is not None:
                r.append((start, i))
                start = None
        return r

    def prozovi(self, adresa, komanda=0, sirovo=False):
        if not self.ukljucena:
            return {"adresa": adresa, "greska": "petlja nije ukljucena (ukljuci())"}
        i0 = self._postavi_prag()
        nivo, bit = self._posalji(self.okvir(adresa, komanda))
        imp = self._impulsi(nivo, self._nivoi()[0])
        n_imp = 1 + 10 + C.N_ODGOVOR              # INIT + 10 predajnih markera + 21 prijemni marker
        if len(imp) < n_imp:
            return {"adresa": adresa, "greska": "uhvaceno %d impulsa umesto %d" % (len(imp), n_imp)}
        # prijemni bit k pocinje krajem markera 10+k (poslednji predajni marker za k = 0)
        pocetci = [kraj for _, kraj in imp[10:10 + C.N_ODGOVOR]]
        d0 = C.ODGOVOR_POCETAK // T_UZORAK
        d1 = (C.ODGOVOR_POCETAK + C.ODGOVOR_PROZOR) // T_UZORAK
        odg = []
        for p0 in pocetci:
            prozor = bit[p0 + d0:p0 + d1]
            # vecina uzoraka u prozoru (dokument uzorkuje sredinu, TD + TC/2) - otporno na kratke smetnje
            odg.append(1 if prozor and 2 * sum(prozor) >= len(prozor) else 0)
        rez = {"adresa": adresa, "komanda": komanda, "i_mirovanja_ma": round(i0, 2),
               "bitovi": "".join(str(b) for b in odg)}
        p = 0
        for ime, n in C.POLJA_ODGOVORA:
            rez[ime] = _vrednost(odg[p:p + n])
            p += n
        rez["prisutan"] = any(odg)
        rez["adresa_ok"] = rez.get("adresa") == adresa and rez["prisutan"]
        rez["adresa"] = adresa
        rez["potvrda_adrese"] = _vrednost(odg[-7:])
        if sirovo:
            rez["nivo"] = nivo
            rez["bit"] = bit
        return rez

    def skeniraj(self, od=1, do=126, komanda=0):
        nadjeni = []
        for a in range(od, do + 1):
            r = self.prozovi(a, komanda)
            if r.get("greska"):
                return nadjeni, r["greska"]
            if r["prisutan"]:
                nadjeni.append(r)
            time.sleep_us(C.T_IZMEDJU_PROZIVANJA)
        return nadjeni, None

    # ---- slusanje prave centrale (drajver ugasen, centrala napaja petlju)
    def sniff(self, ms=200):
        if self.ukljucena:
            return None, "iskljuci drajver pre slusanja"
        t, v, i = array.array("I"), array.array("H"), array.array("H")
        av, ai = self.adc_r, self.adc_i
        t0 = time.ticks_us()
        kraj = time.ticks_add(t0, ms * 1000)
        while time.ticks_diff(kraj, time.ticks_us()) > 0:
            t.append(time.ticks_diff(time.ticks_us(), t0))
            v.append(av.read_u16())
            i.append(ai.read_u16())
        return (t, v, i), None


def analiziraj(t, signal, prag):
    # vraca listu (pocetak_us, sirina_us, pauza_pre_us) za delove signala iznad praga
    r, start, kraj_pret = [], None, None
    for k in range(len(t)):
        iznad = signal[k] > prag
        if iznad and start is None:
            start = t[k]
        elif not iznad and start is not None:
            r.append((start, t[k] - start, None if kraj_pret is None else start - kraj_pret))
            kraj_pret = t[k]
            start = None
    return r
