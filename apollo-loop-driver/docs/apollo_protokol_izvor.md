# Apollo protokol – izvorni opis i napomene

Prepis dokumenta **„APOLLO_PROTOCOL_DOCUMENTATION“** (Google Docs, dobijen od korisnika 23.11.2026).
Dokument opisuje Linux kernel drajver `mod_apollo.ko` (centrala pomera GPIO pin sa `gpio_set_value` / `udelay`).
Poreklo i ispravnost **nisu potvrđeni merenjem**. Vrednosti su prenete u `../firmware/config.py`.

Samo laboratorija – nije protivpožarni uređaj, ništa nije sertifikovano (EN 54).

## 1. Osnovno (iz dokumenta)

- Polu-dupleks, 2-žična petlja; centrala je master, uređaji odgovaraju samo kad su prozvani.
- Adresa 7 bita (0–127).
- Bit se kodira trajanjem LOW dela; svaki bit se završava HIGH impulsom od 300 µs.

## 2. Vremena (iz dokumenta, µs)

| Konstanta | Vrednost | Značenje |
|---|---|---|
| T0 | 500 | logička 0 ukupno: LOW 200 + HIGH 300 |
| T1 | 1150 | logička 1 ukupno: LOW 850 + HIGH 300 |
| TP | 300 | HIGH marker na kraju svakog bita |
| TI | 1650 | početni (INIT) HIGH impuls |
| TE | 1650 | „end pulse“ = TI (definisan, u kodu se ne koristi – kraj okvira je samo LOW) |
| TA | 800 | čitanje: deo A |
| TC | 250 | čitanje: prozor C |
| TD | 350 | čitanje: kašnjenje D |

**Prijemni bit (centrala čita uređaj):** LOW TD + TC/2 = 475 µs → uzorak ulaza → LOW TC/2 + TA = 925 µs → HIGH TP 300 µs.
Ukupno ~1700 µs po bitu. Uređaj odgovara strujom u prozoru TD … TD + TC = 350–600 µs od početka LOW.

## 3. Okvir

```
INIT (1650 HIGH) | komanda 3 bita | adresa 7 bita | odgovor 21 bit
                   centrala šalje                  uređaj šalje
odgovor: INT 1 | analog 7 | ulazi 3 | tip 3 | echo adrese 7
```

Kod iz dokumenta (sažeto):

```c
gpio_set_value(out, HIGH); udelay(TI);        // INIT
send_bits(cmd, 3); send_bits(addr, 7);         // LOW (200/850) + HIGH 300 po bitu
int = read_bits(1); analog = read_bits(7);      // po bitu: LOW 475, uzorak, LOW 925, HIGH 300
input = read_bits(3); type = read_bits(3); addr_echo = read_bits(7);
gpio_set_value(out, LOW);                       // kraj
```

Primer: komanda 0x01 (001), adresa 0x47 (1000111) – zapis sugeriše da se šalje **MSB prvi**.
Odgovor u primeru: INT = 1 (alarm), analog = 0x5A, ulazi = 0, tip = 2 (dimni), echo = 0x47.

Trajanje okvira: 42,5 ms (sve nule) – 49 ms (sve jedinice), prosečno ~46 ms.
126 uređaja → krug ~5,8–6,2 s.

## 4. Tvrdnje iz dokumenta koje treba proveriti

1. **Polaritet.** Dokument govori o GPIO pinu, ne o naponu petlje. Pretpostavka u firmveru:
   HIGH = impuls 31 V, LOW = osnovni nivo 24 V, između okvira LOW (`HIGH_JE_IMPULS = True`).
2. **INT bit.** Dokument kaže da Apollo „nema pravi interrupt“ i da alarm čeka svoje prozivanje (do ~6 s).
   INT je prvi bit odgovora; ako ga uređaj u alarmu (npr. ručni javljač) daje pri prozivanju **bilo koje**
   adrese, centrala saznaje za alarm posle jednog okvira (~50 ms). Ovo je naša pretpostavka – proveriti sniff-om.
3. **Polja odgovora.** Dokument: INT 1 / analog 7 / ulazi 3 / tip 3 / adresa 7. Ranije (patent): analog 7 / ulazi 2 /
   tip 5 / adresa 7. Firmver sada koristi raspored iz dokumenta.
4. **„EN 54-2: najviše 10 s za ceo krug“** je pojednostavljenje – norma propisuje vreme od signala do prikaza
   alarma, ne direktno vreme kruga.

## 5. Šta je promenjeno u firmveru

- `config.py`: `T_INIT 1650`, `T_MARKER 300`, `T_NULA 200`, `T_JEDAN 850`, `T_CITANJE 1400`,
  `ODGOVOR_POCETAK 350`, `ODGOVOR_PROZOR 250`, `N_ODGOVOR 21`, `HIGH_JE_IMPULS`, nova `POLJA_ODGOVORA`.
  Uklonjeno: `T_RESET`, `T_RESET_PAUZA`, `T_BIT_PAUZA`, `T_SYNC`, `T_SYNC_PAUZA`, `ODGOVOR_KASNJENJE`, `N_SYNC`.
- `loopdrv.py`: `okvir()` gradi INIT + (LOW, marker) po bitu; odgovor se čita u prozoru 350–600 µs od kraja
  prethodnog markera, odluka po većini uzoraka (20 µs). Proveren simulacijom na PC-u (primer 0x47 iz dokumenta,
  okvir 46,4 ms sa 0,8 ms uvoda/kraja), **nije probano na hardveru**.

## 6. Plan merenja na pravoj centrali

Sniff jednog okvira (osciloskop ili `sniff` režim mastera), pa potvrditi:
polaritet HIGH/LOW, 1650 / 200 / 850 / 300 µs, trajanje prijemnog bita 1700 µs, položaj strujnog odgovora
(350–600 µs), redosled bitova (MSB prvi) i ponašanje INT bita kod ručnog javljača.
