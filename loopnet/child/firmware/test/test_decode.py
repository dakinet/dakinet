#!/usr/bin/env python3
"""Host test dekodera LoopNet (ln_proto.c) – simulacija okvira po PROTOCOL.md v0.2.

Prevodi ln_proto.c za racunar (gcc -shared), pa za svaki okvir:
  - master (ovaj skript) pravi uzlazne ivice: START, zaglavlje, parametar, prozori T_W;
  - model uredjaja: oscilator ±3 %, kasnjenje detekcije ivice 10–14 µs, 16-bitni TCB na 5 MHz;
  - linija ostaje iznad praga (impuls + silazna ivica do praga) -> provera START-a posle 300 µs;
  - master uzorkuje struju u 0,70–0,87 T_W; ponor mora pokriti ceo interval uzorkovanja.
Pokretanje:  python3 test/test_decode.py
"""
import ctypes
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'ln_proto.c')
SHIM = os.path.join(HERE, 'shim.c')
TICKS_PER_US = 5

SKEN, DOGADJAJI, STATUS, POTVRDI, INFO, DODELI, LED = range(7)
K_WIN = {SKEN: 254, DOGADJAJI: 254, STATUS: 16, POTVRDI: 1, INFO: 32, DODELI: 1, LED: 1}
LN_SINK, LN_ARM_START, LN_FRAME_DONE, LN_FRAME_ERR = 1, 2, 4, 8


def build():
    so = os.path.join(tempfile.mkdtemp(), 'ln.so')
    subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-shared', '-fPIC',
                    '-DLN_TICKS_PER_US=%d' % TICKS_PER_US, SRC, SHIM, '-o', so], check=True)
    return ctypes.CDLL(so)


L = build()


def parity(v):
    return bin(v).count('1') & 1


# ---------------------------------------------------------------- master: okvir

def frame(cmd, addr, param=None, tw=150, k=None, bad_parity=False, bit_us=(150, 250)):
    """Vraca listu (vreme_uzlazne_ivice_us, trajanje_impulsa_us) i vremena ivica prozora."""
    hdr = (cmd << 8) | (addr << 1)
    hdr |= parity(hdr) ^ (1 if bad_parity else 0)
    bits = [(hdr >> (10 - i)) & 1 for i in range(11)]
    if param is not None:
        p = (param << 1) | parity(param)
        bits += [(p >> (8 - i)) & 1 for i in range(9)]
    t = 0.0
    edges = [(t, 500.0)]
    t += 650
    for b in bits:
        edges.append((t, 40.0))
        t += bit_us[b]
    if k is None:
        k = K_WIN.get(cmd, 0)
    wins = []
    for _ in range(k + 1):             # prozor 0 + K prozora
        edges.append((t, 40.0))
        wins.append(t)
        t += tw
    return edges, wins, t + 500        # razmak posle okvira


class Uredjaj:
    def __init__(self, addr, osc=1.0, seed=0):
        self.osc = osc
        self.rnd = random.Random(seed)
        L.ln_init(addr)
        L.set_type(1)
        L.set_fw(2)

    def ticks(self, t_us):
        return int(round(t_us * TICKS_PER_US * self.osc)) & 0xFFFF

    def run(self, t0, edges, fall_us=22.0):
        """Pusta ivice kroz dekoder; vraca listu (t_on_us, t_off_us) intervala ponora (vreme mastera)."""
        sink = []
        for i, (t, high) in enumerate(edges):
            d = self.rnd.uniform(10.0, 14.0)            # polovina uzlazne ivice + kabl
            td = t0 + t + d
            r = L.ln_rise(self.ticks(td))
            if r & LN_SINK:
                on = L.get_sink_on() / (TICKS_PER_US * self.osc)
                off = L.get_sink_off() / (TICKS_PER_US * self.osc)
                lat = self.rnd.uniform(1.0, 5.0)        # buđenje + ulaz u prekid
                sink.append((td + max(on, lat), td + off + self.rnd.uniform(0.0, 1.0)))
            if r & LN_ARM_START:
                # provera posle 300 µs vremena uredjaja: linija iznad praga?
                t_chk = td + 300.0 / self.osc
                nxt = edges[i + 1][0] + t0 if i + 1 < len(edges) else 1e18
                if t_chk < nxt and t_chk < t0 + t + high + fall_us:
                    L.ln_long_high()
        return sink


def master_citaj(t0, wins, tw, sink, prvi=1, n=None):
    """Bitovi koje master vidi u prozorima (1..); 'x' = ponor samo delimicno pokriva uzorkovanje."""
    out = []
    n = len(wins) - 1 if n is None else n
    for k in range(prvi, prvi + n):
        a, b = t0 + wins[k] + 0.70 * tw, t0 + wins[k] + 0.87 * tw
        full = any(on <= a and off >= b for on, off in sink)
        part = any(on < b and off > a for on, off in sink)
        out.append(1 if full else ('x' if part else 0))
    return out


# ---------------------------------------------------------------- testovi

greske = []


def proveri(uslov, poruka):
    if not uslov:
        greske.append(poruka)
        print('  GRESKA:', poruka)


def okvir_za(dev, cmd, addr, param=None, tw=150, t0=1000.0, **kw):
    fall = kw.pop('fall_us', 22.0)
    edges, wins, kraj = frame(cmd, addr, param, tw, **kw)
    sink = dev.run(t0, edges, fall)
    return wins, sink, t0 + kraj


def test_sken():
    print('SKEN, sve adrese, oscilator ±3 %, T_W 150/250/400')
    for tw in (150, 250, 400):
        for osc in (0.97, 1.0, 1.03):
            for addr in (1, 2, 63, 126, 127):
                for inp in (0, 1, 2, 3):
                    d = Uredjaj(addr, osc, seed=addr * 7 + inp)
                    L.set_input(inp)
                    wins, sink, _ = okvir_za(d, SKEN, 0, tw=tw)
                    bits = master_citaj(1000.0, wins, tw, sink)
                    exp = [0] * 254
                    exp[(2 * addr - 1 if inp else 2 * addr) - 1] = 1
                    proveri(bits == exp, 'SKEN tw=%d osc=%.2f addr=%d in=%d: %s' % (
                        tw, osc, addr, inp, [i + 1 for i, b in enumerate(bits) if b]))


def test_status_info():
    print('STATUS i INFO')
    for osc in (0.97, 1.03):
        d = Uredjaj(42, osc, seed=3)
        L.set_input(2); L.set_event(1); L.set_changes(9); L.set_low_voltage(0); L.set_vline(117)
        wins, sink, _ = okvir_za(d, STATUS, 42)
        b = master_citaj(1000.0, wins, 150, sink)
        v = sum(x << i for i, x in enumerate(b))
        proveri('x' not in b and parity(v) == 0 and (v & 3) == 2 and (v >> 2) & 1 and ((v >> 4) & 15) == 9
                and ((v >> 8) & 0x7F) == 42, 'STATUS %s' % b)
        wins, sink, _ = okvir_za(d, INFO, 42)
        b = master_citaj(1000.0, wins, 150, sink)
        v = sum(x << i for i, x in enumerate(b))
        by = [(v >> (8 * i)) & 0xFF for i in range(4)]
        crc = 0
        for x in by[:3]:
            crc ^= x
            for _ in range(8):
                crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
        proveri(by[0] == 1 and by[1] == 2 and by[2] == 117 and by[3] == crc, 'INFO %s' % by)
        # STATUS drugoj adresi: uredjaj cuti
        wins, sink, _ = okvir_za(d, STATUS, 43)
        proveri(sink == [], 'STATUS za 43 a odgovara 42')


def test_dogadjaji_potvrdi():
    print('DOGADJAJI / POTVRDI')
    d = Uredjaj(10, 1.01, seed=5)
    L.set_input(1); L.set_event(1)
    wins, sink, _ = okvir_za(d, DOGADJAJI, 0)
    b = master_citaj(1000.0, wins, 150, sink)
    proveri(b[19 - 1] == 1 and sum(1 for x in b if x) == 1, 'DOGADJAJI sa dogadjajem')
    wins, sink, _ = okvir_za(d, POTVRDI, 10)
    b = master_citaj(1000.0, wins, 150, sink)
    proveri(b == [1] and L.get_event() == 0 and L.get_acked() == 1, 'POTVRDI adresirano: %s' % b)
    wins, sink, _ = okvir_za(d, DOGADJAJI, 0)
    b = master_citaj(1000.0, wins, 150, sink)
    proveri(b[20 - 1] == 1 and sum(1 for x in b if x) == 1, 'DOGADJAJI posle potvrde')
    L.set_event(1)
    wins, sink, _ = okvir_za(d, POTVRDI, 0, k=0)
    proveri(sink == [] and L.get_event() == 0, 'POTVRDI broadcast')


def test_dodeli_led():
    print('DODELI ADRESU i LED')
    d = Uredjaj(127, 0.98, seed=9)
    L.set_assign_armed(0)
    wins, sink, _ = okvir_za(d, DODELI, 0, param=55)
    proveri(sink == [] and L.get_new_addr() == 0, 'DODELI bez tastera prihvacena')
    L.set_assign_armed(1)
    wins, sink, _ = okvir_za(d, DODELI, 0, param=55)
    b = master_citaj(1000.0, wins, 150, sink)
    proveri(b == [1] and L.get_new_addr() == 55, 'DODELI sa tasterom: %s %d' % (b, L.get_new_addr()))
    d = Uredjaj(55, 1.02, seed=11)
    wins, sink, _ = okvir_za(d, LED, 55, param=2)
    b = master_citaj(1000.0, wins, 150, sink)
    proveri(b == [1] and L.get_led_cmd() == 0x82, 'LED adresirano')
    L.set_led_cmd(0)
    wins, sink, _ = okvir_za(d, LED, 0, param=1, k=0)
    proveri(sink == [] and L.get_led_cmd() == 0x81, 'LED broadcast')


def test_greske():
    print('Greske: parnost, period van opsega, pogresan T_W, sporа silazna ivica')
    d = Uredjaj(5, 1.0, seed=1)
    L.set_input(1)
    e0 = L.get_frames_err()
    wins, sink, _ = okvir_za(d, SKEN, 0, bad_parity=True)
    proveri(sink == [] and L.get_frames_err() == e0 + 1, 'losa parnost prihvacena')
    wins, sink, _ = okvir_za(d, SKEN, 0, bit_us=(90, 250))
    proveri(sink == [], 'bit 0 od 90 µs prihvacen')
    wins, sink, _ = okvir_za(d, DOGADJAJI, 0, bit_us=(150, 340))
    proveri(sink == [], 'bit 1 od 340 µs prihvacen')
    wins, sink, _ = okvir_za(d, DOGADJAJI, 0, bit_us=(150, 200))
    proveri(sink == [], 'bit 1 od 200 µs prihvacen')
    wins, sink, _ = okvir_za(d, SKEN, 0, tw=120)
    proveri(sink == [], 'T_W 120 µs prihvacen')
    # ispravan okvir odmah posle losih
    wins, sink, _ = okvir_za(d, SKEN, 0)
    b = master_citaj(1000.0, wins, 150, sink)
    proveri(b[9 - 1] == 1 and sum(1 for x in b if x) == 1, 'oporavak posle gresaka')
    # silazna ivica 200 µs (malo opterecenje): START se i dalje prepoznaje, bitovi takodje (mere se uzlazne ivice)
    wins, sink, _ = okvir_za(d, SKEN, 0, fall_us=200.0)
    proveri(any(sink), 'spora silazna ivica')


def test_niz_okvira():
    print('Niz okvira jedan za drugim (razmak 500 µs), mesovite komande')
    d = Uredjaj(77, 1.025, seed=21)
    L.set_input(0); L.set_event(0)
    t0 = 1000.0
    rnd = random.Random(4)
    for i in range(200):
        cmd = rnd.choice([SKEN, DOGADJAJI, STATUS, INFO, POTVRDI])
        addr = 0 if cmd in (SKEN, DOGADJAJI) else rnd.choice([77, 78, 1])
        if cmd == POTVRDI and addr == 77:
            pass
        edges, wins, kraj = frame(cmd, addr)
        sink = d.run(t0, edges)
        b = master_citaj(t0, wins, 150, sink)
        if cmd == SKEN:
            proveri(b[153] == 1 and sum(1 for x in b if x) == 1, 'niz %d SKEN' % i)
        elif cmd == STATUS and addr == 77:
            v = sum(x << j for j, x in enumerate(b))
            proveri(((v >> 8) & 0x7F) == 77 and parity(v) == 0, 'niz %d STATUS' % i)
        elif addr != 77 and cmd not in (DOGADJAJI,):
            proveri(not any(b), 'niz %d odgovor tudjoj adresi' % i)
        t0 += kraj
    proveri(L.get_frames_err() == 0, 'greske u nizu: %d' % L.get_frames_err())


def test_margina():
    print('Vremenska rezerva ponora prema uzorkovanju mastera (najgori slucaj)')
    worst = 1e9
    for tw in (150, 200, 300, 400):
        for osc in (0.97, 1.03):
            on = int(tw * TICKS_PER_US * osc) * 3 // 10 / (TICKS_PER_US * osc)
            off = int(tw * TICKS_PER_US * osc) * 19 // 20 / (TICKS_PER_US * osc)
            # T_W u tikovima uredjaja meri se njegovim oscilatorom -> pomaci su u pravom vremenu ~ tw*0,30 i tw*0,95
            for d in (10.0, 14.0):
                m1 = 0.70 * tw - (d + max(on, 5.0))
                m2 = (d + off) - 0.87 * tw
                worst = min(worst, m1, m2)
    print('  najmanja rezerva: %.1f µs' % worst)
    proveri(worst >= 5.0, 'rezerva < 5 µs')


if __name__ == '__main__':
    for f in (test_sken, test_status_info, test_dogadjaji_potvrdi, test_dodeli_led, test_greske,
              test_niz_okvira, test_margina):
        f()
    print('\n%s: %d gresaka' % ('PROSLO' if not greske else 'PALO', len(greske)))
    sys.exit(1 if greske else 0)
