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
  Pažnja: TPS55340 VIN/EN apsolutni max 34 V (preporučeno do 32 V), na ulazu nema TVS-a.
- 3,3 V: **TPS560430X3FDBVR** (SOT-23-6: 1 CB, 2 GND, 3 FB=VOUT, 4 EN, 5 VIN, 6 SW), L2 15 µH SRN4018.
- VSET iz 3,3 V (bez REF3033): R5 1k / R6 15k / R7 3k24 preko Q2 → 3,094 V (impuls) / 2,40 V (osnovni); Q3 gasi petlju.
- Izlaz: OPA197 (×10,1: R11 91k / R12 10k) → R10 470 Ω → **MJD122** Darlington DPAK (izvor) + **MMBT5401** PNP (aktivni
  ponor za silaznu ivicu, R14 10 Ω) – push-pull; ograničenje Q4 + R13 2 Ω ≈ 325 mA; latch zaštita ≈ 285 mA (R24 13k/R25 10k).
  Termika: MJD122 ~ (34−24,2) V × I → kontinualno ≤ 150 mA bez hladnjaka, 250 mA kratkotrajno; dodati bakarnu površinu +34 V
  ispod taba (F/B + via) u `finish_pcb.py`.
- Merenje: šant R19 1 Ω, MCP6002 ×5,02, MCP6561 sa PWM pragom – isto kao master; VLOOP/VRET delitelji.
- RP2040: isti GPIO kao master (firmver radi bez izmena), + GP0/GP1 UART0, **GP6 = OCP** (ispravljena greška iz mastera).
- Letvica J4 (1×8, 2,54): GND, 3V3, TX, RX, RUN, BOOT, USB D+, USB D− (za prvo snimanje MicroPython-a); J5 SWD.

Sledeći koraci:
1. Završiti raspored: `python3.12 make_pcb.py --samo-proveri --slika` – trenutno ~23 preklapanja (C1 van ivice, oko U4,
   U8/C11/C25, C27/J4, C5/D2, D1/U1…). Boost petlja (U1–L1–D2–C3/C4) mora biti kratka (TI layout smernice).
2. `finish_pcb.py` i `jlc.py` su kopirani iz LoopNet-a: **promeniti dimenzije ploče** (OKVIR, granice 130/120 → 160/145,
   mreža šivenja 30×20 → 60×45) i tabelu LCSC u `jlc.py` (sve stavke modula).
3. `.kicad_dru` (razmak 0,3 mm za +34V/LOOP mreže), `build.sh`, DRC bez grešaka.
4. ~~Šema na jednom listu~~ GOTOVO: `apollo-loop-module/hardware/schematic/kompletna.py` (+ `alat.py`) → `.svg/.png`;
   skripta čita `P` iz `make_pcb.py` i proverava povezanost (0 grešaka). Ostaje README, 3D.
   KiCad šema: `apollo-loop-module/hardware/schematic/kicad/apollo_module.kicad_sch` (KiCad 10, A1), generiše
   `apollo_sema.py` (+ `raspored.py`, `kisch.py`); netlista iz kicad-cli = P (0 grešaka), ERC 0/0.
5. Firmver: postojeći `apollo-loop-driver/firmware` + UART komande (umesto USB REPL-a).

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
