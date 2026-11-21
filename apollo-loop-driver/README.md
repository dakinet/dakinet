# Apollo XP95 laboratorijski drajver petlje

Elektronika koja sama napaja Apollo adresabilnu petlju, proziva uređaje XP95/Discovery protokolom
i čita njihove strujne odgovore. **Samo za laboratoriju** – uređaj nije sertifikovan po EN 54 i ne sme
se priključiti na petlju koja štiti ljude ili objekat.

| | |
|---|---|
| Napajanje | 24 V DC (21–28 V), kao protivpožarna centrala |
| Petlja | 24,2 V osnovni nivo, 31,2 V impuls, do ≈ 540 mA (ograničenje), PTC 750 mA |
| Mozak | Raspberry Pi Pico (MicroPython, PIO + DMA za vremenski kritične delove) |
| Pločica | 120 × 85 mm, 2 sloja, rutirana (Freerouting), GND površine na oba sloja |

## Sadržaj

```
hardware/schematic/   električna šema u 4 lista (SVG/PNG) i skripte koje je crtaju (schemdraw)
hardware/pcb/         KiCad 7 pločica, Gerber + drill (apollo_loop_driver_gerber.zip), BOM, DRC izveštaj
  make_pcb.py         raspored komponenti i mreže (izvor istine za pločicu)
  finish_pcb.py       uvoz vodova iz Freerouting-a, GND površine i šivenje
  build.sh            ceo tok: raspored -> rutiranje -> DRC
firmware/             MicroPython za Pico: config.py, loopdrv.py, main.py
```

## Pločica
- DRC: 0 nepovezanih vodova, 0 grešaka razmaka. Ostala su upozorenja o natpisima (silkscreen)
  i jedna GND termalna veza sa jednim krakom – ne utiču na rad.
- **Boost modul 24 → 34 V (≥ 20 W)** je van pločice, vezan na J4: `VIN, GND, VOUT, GND`.
  Pre povezivanja ga podesi trimerom na 34,0 V.
- **Q3 (TIP122)** stoji na gornjoj ivici zbog hladnjaka. Pri 500 mA petlje greje se ≈ 5 W.
- Pico se utiče u dva podnožja 1×20 (U7A pinovi 1–20, U7B pinovi 21–40), USB konektor levo.
- USB ka računaru ide kroz spoljni USB izolator, da masa petlje ostane odvojena od računara.

**Pre naručivanja proveri** raspored pinova iz datasheet-a za: REF3033 (SOT-23: 1 IN, 2 OUT, 3 GND),
MCP6561 (SOT-23-5: 1 OUT, 2 VSS, 3 +IN, 4 −IN, 5 VDD), OPA197 i MCP6002 (SOIC-8, standardni),
2N7002/BC847 (SOT-23: 1 G/B, 2 S/E, 3 D/C) i TIP122 (TO-220: B, C, E).

## Firmver
Kopiraj `firmware/*.py` na Pico sa MicroPython-om (npr. Thonny). Na USB serijskom portu:

```
on | off | status
poll 5            prozove adresu 5
scan 1 126        traži sve uređaje
sniff 300         sluša pravu centralu 300 ms (drajver ugašen)
set T_JEDAN 650   menja vreme u RAM-u
get               ispiše vremena okvira
```

Vremena označena sa `?` u `config.py` nisu objavljena (širina impulsa za 0 i 1, takt, prozor odgovora).
Izmeri ih na pravoj centrali u režimu **sniff**:

- centrala L+ → J3-1 (LOOP IN +) i dalje ka uređajima
- centrala L− → GND pločice (J1-2)
- L− uređaja → J3-2 (ide kroz šant R14)
- **J2 (LOOP OUT) ostaje nepovezan**, drajver ugašen (`off`)

## Soteria / CoreProtocol
Soteria javljači su kompatibilni unazad: na XP95/Discovery petlji rade kao Discovery uređaji
(analogna vrednost, tip, adresa, LED). Ova pločica ih zato podržava u tom režimu.
Funkcije samo za CoreProtocol (soft adresiranje, serijski broj, checksum, adrese do 254, režim 35 V)
traže nepoznatu specifikaciju i izlazni stepen do ≈ 48 V – to je plan za v2.

## Izvori
- US8428153B2 – opis XP95 okvira (reset 1,5 ms, 10 bitova, 21 takt, 21-bitni strujni odgovor)
- Apollo Test Set PP2625, Loop Interface PP5099, XP95 I.S. PP1095
