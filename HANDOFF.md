# Predaja posla (stanje 22.11.2026, grana `ccr-b67126b8-43iho2`)

## 1. Šta je gotovo

**LoopNet** (`loopnet/`)
- `PROTOCOL.md` v0.2: bitovi kodirani periodom između uzlaznih ivica (master nema aktivno spuštanje – silazna ivica zavisi
  od opterećenja), uređaji vuku konstantnu struju (~195 µA), prozor 0 referentni, par prozora 2N−1/2N po adresi, T_W 150–400 µs.
- `child/` LoopNet 1IN v0.1: šema na jednom listu (`hardware/schematic/kompletna.*`), pločica 30×20 mm izrutirana, DRC čist
  (samo „library ''“ napomene), JLC Gerber/BOM/CPL, 3D prikaz (`hardware/3d/`, objavljen kao artifact).
  JLC Basic gde može; Extended: ATtiny1616, SMAJ40A, BZT52C10, 4M7, KF350.
  **Proveriti pre narudžbine:** raspored pinova HT7533-1 (1 GND, 2 VIN, 3 VOUT – nije iz datasheet-a), LCSC za 4M7.
- `child/firmware/`: `ln_proto.c` dekoder + `test/test_decode.py` (prolazi). **Nema još `main.c`** (sleep, ADC/DAC prag
  sample-hold na PA6, TCB0 capture, EEPROM, taster, LED) – tačka 3 originalnog zadatka.

**Nije urađeno iz originalnog zadatka:** 3 (firmver uređaja `main.c`), 4 (LoopNet režim u master firmveru: PIO program po
PROTOCOL §2, SKEN tabela 127 adresa, UART/USB komande, merenje silazne ivice i izbor T_W), 5 (plan testa: 5–10 uređaja na
kolutu 500 m–1 km + simulacija 120 uređaja otpornicima/kondenzatorima).

## 2. Nađena greška u masteru (nije ispravljeno – čeka odobrenje)

`apollo-loop-driver/hardware/pcb/make_pcb.py`: RP2040 pin 8 (GP6) je na mreži `OC_FLAG`, koja nije povezana ni sa čim,
a izlaz zaštite je mreža `OCP`. Šema (`schematic/other.py`) kaže OCP → GP6. Posledica: firmver ne vidi okidanje
hardverske zaštite. Ispravka: u `U9` promeniti `'8': 'OC_FLAG'` u `'8': 'OCP'`, ponovo `build.sh` + `jlc.py`.

## 3. U radu: Apollo loop driver MODUL (`apollo-loop-module/`)

Zahtevi (od korisnika): 24 V ulaz (21–28 V) + boost, petlja do 250 mA, samo UART 3,3 V ka hostu, laboratorija.

Odluke (sve u docstring-u `hardware/pcb/make_pcb.py`, netlista `P` je kompletna):
- Boost **TPS55340PWPR** (HTSSOP-14, pinovi iz TI datasheet-a): 34,4 V (R1 270k/R2 10k, Vref 1,229 V), ~580 kHz (R3 82k),
  L1 33 µH SRN6045, D2 SS210, C3/C4 10 µF/50 V + C5 100 µF/50 V, komp. R4 2k2 + C6 100n + C7 100p, SS 47n.
- Pinovi U1/U2 potvrđeni po datasheet-u 22.11.2026: TPS55340 SLVSBD4E (sep 2021) tabela 5-1 HTSSOP-14,
  TPS560430 SLVSE22B (jun 2018) Pin Functions DBV; X3F = fiksno 3,3 V, 1,1 MHz, FPWM (Device Comparison Table).
  Pažnja: TPS55340 VIN/EN apsolutni max 34 V (preporučeno do 32 V) → dodat TVS **D6 SMBJ28A** na VIN_F (23.11.2026);
  pri velikom udaru klampuje iznad 34 V – za pravu centralu razmotriti filtar/zaštitu VIN pina U1.
- 3,3 V: **TPS560430X3FDBVR** (SOT-23-6: 1 CB, 2 GND, 3 FB=VOUT, 4 EN, 5 VIN, 6 SW), L2 15 µH SRN4018.
- VSET iz 3,3 V (bez REF3033): R5 1k / R6 15k / R7 3k24 preko Q2 → 3,094 V (impuls) / 2,40 V (osnovni); Q3 gasi petlju.
- Izlaz: OPA197 (×10,1: R11 91k / R12 10k) → R10 470 Ω → **MJD122** Darlington DPAK (izvor) + **MMBT5401** PNP (aktivni
  ponor za silaznu ivicu, R14 10 Ω) – push-pull; ograničenje Q4 + R13 2 Ω ≈ 325 mA; latch zaštita ≈ 285 mA (R24 13k/R25 10k).
  Termika: MJD122 ~ (34−24,2) V × I → kontinualno ≤ 150 mA bez hladnjaka, 250 mA kratkotrajno; dodati bakarnu površinu +34 V
  ispod taba (F/B + via) u `finish_pcb.py`.
- Merenje: šant R19 1 Ω, MCP6002 ×5,02; VLOOP/VRET delitelji; hardverska zaštita U6 MCP6561 ostaje.
- **MCU (23.11.2026): AVR64DD28-I/SO + kristal 16 MHz** umesto RP2040 (otpali U8 flash, U5 komparator BIT, R23/C22 PWM
  prag, ~11 blokadnih C, USB). 131 → 86 elemenata. Pinovi po DS40002315A (prelim., sl. 2-1 + tab. 3-1), komentar kod U7:
  PA2 NIVO (TCA0 WO2), PA3 EN_N, PA6 OC_RST, PD1 OCP, PD2 IAMP = AC0 AINP0 (prag interni DACREF) + ADC AIN2,
  PD4 VLOOP, PD5 VRET, PA4/PA5 USART0 ALT1 ka matičnoj, PC0/PC1 USART1 dijagnostika, PA0/PA1 XTALHF, PA7 LED,
  PF6 RESET (R29 10k + C30 10n), PF7 UPDI. VDDIO2 (MVIO) na 3,3 V. 2 USART-a potvrđena u tabeli 2 datasheet-a.
  Kristal 16 MHz X322516MLB4SI, C26/C27 27p za pretpostavljeni CL 20 pF – **proveriti CL i LCSC** pre narudžbine.
- Letvica J1 2×14: 13 RESET, 14 UPDI, 15/16 DBG_TX/DBG_RX, 17/18 GND (ranije RUN/BOOT/USB/SWD za RP2040).
  Ažuriranje firmvera sa matične ploče: UART bootloader + UPDI kao rezerva.
- Firmver mastera (`apollo-loop-driver/firmware`, MicroPython/RP2040) NE radi na modulu – modul traži novi C firmver.

Sledeći koraci:
1. Raspored: `make_pcb.py --samo-proveri --slika` (radi i sa KiCad 10: `"C:/Program Files/KiCad/10.0/bin/python.exe"`)
   → 0 preklapanja posle prelaska na AVR (U7 rot 270, kristal/RESET/LED u pojasu ispod, D6 uz levu ivicu).
   Rutiranje i DRC nisu urađeni za novu verziju.
2. `finish_pcb.py` i `jlc.py` su kopirani iz LoopNet-a: **promeniti dimenzije ploče** (OKVIR, granice 130/120 → 160/145,
   mreža šivenja 30×20 → 60×45) i tabelu LCSC u `jlc.py` (sve stavke modula).
3. `.kicad_dru` (razmak 0,3 mm za +34V/LOOP mreže), `build.sh`, DRC bez grešaka.
4. Šema: važeća je KiCad `apollo-loop-module/hardware/schematic/kicad/apollo_module.kicad_sch` (KiCad 10, A1),
   generiše `apollo_sema.py` (+ `raspored.py`, `kisch.py`, sopstveni simboli u `apollo.kicad_sym`: TPS55340,
   TPS560430, AVR64DD28); netlista iz kicad-cli = P (0 grešaka), ERC 0/0. Stara schemdraw `kompletna.py` je ZASTARELA
   (RP2040). Ostaje README, 3D.
5. Firmver modula: novi, C (avr-gcc / DxCore): Apollo okvir po `apollo-loop-driver/docs/apollo_protokol_izvor.md`,
   AC0 + DACREF + event → TCB za prijem, ADC, UART protokol ka matičnoj, UART bootloader.

## 4. Napomene o okruženju (cloud sesija)

- jlcpcb.com, lcsc.com, microchip.com, nexperia, vishay, diodes su bili blokirani; ti.com i GitHub raw su radili.
  JLC Basic lista korišćena iz `cpldcpu/TouchSynth/parts/jlcpcb_basic_parts.csv` (može biti zastarela).
- Freerouting ne poštuje razmak do ivice – zato pojas 0,35 mm (rule area) u `make_pcb.py`.

## 5. Apollo modul – ručni tok završen (`apollo-loop-module/hardware/pcb_rucno/`, 22.11.2026)

- Ploča 76×54 mm, 2 sloja, letvica 2×14 / 2,54 mm dole, centrirana na donjoj ivici (modul se utiče u matičnu ploču).
- **DRC (kicad-cli): 0 grešaka, 0 nepovezanih padova.** Gerber + drill: `apollo_module_gerber.zip`; 3D: `pcb_gore.png`, `pcb_dole.png`.
- Tok: `make_pcb.py` (raspored + ručni strujni putevi + `rucni_vodovi.py`) → `finish_pcb.py` (GND F/B, +34V ispod Q1,
  šivenje 2 mm) → `ostrva.py` (via za odsečena ostrva mase) → DRC. Svaka izmena ide kroz `rucno_alat.primeni()`
  (preklapanja + širine po netlisti + DRC, inače se vraća). Ruter/postavljač: `C:\Users\Filip\claude\PCB\tools\ruter` (van repoa).
- RP2040 okrenut 90°, flash dole-levo: svih 6 QSPI na F.Cu bez via; zona 15×15 mm oko MCU samo za neophodne delove;
  DVDD/IOVDD desno kroz tented via ispod tela (kao Pico); ostale strane ispod tela bez vodova.
- Boost/buck po TI smernicama; analogni deo boost-a po redosledu pinova (COMP | FB | FREQ); dugi GPIO vodovi vraćeni
  na F.Cu jer su na B.Cu sekli masu u ostrva.
- BOM/CPL: `jlc.py` → `BOM_JLC.csv`, `CPL_JLC.csv`, `bom.csv` (55 stavki, 102 dela; J1 se lemi ručno). LCSC brojevi
  označeni S/M/?; nepotvrđeni: L1 (LCSC ima SRN6045 bez TA, 1,4 A; vrh L1 ≈0,71 A @20 V ulaz, 34,4 V/250 mA, 580 kHz – dovoljno), L2 (zamena 3L SNR4018K-150M, 0,92 A), 15 pF (C1644).
- **Proveriti pre narudžbine:** stanje i cene u JLC katalogu (TPS560430 ~300-400 kom), tented via ispod
  RP2040 (JLC opcija „tented vias“).
- TPS55340PWPR = TI PWP0014K (crtež 4229706/B, datasheet SLVSBD4E): bakar 3,4×5 se slaže; maska i pasta footprint-a
  bile su veće od pada (3,155×3,255 / 2,9×2,89) – `finish_pcb.py` ih svodi na TI 2,6×2,59 (pasta 4 × 1,2×1,195).
