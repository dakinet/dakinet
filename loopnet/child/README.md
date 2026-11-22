# LoopNet 1IN v0.1 – uređaj sa jednim ulazom

Uređaj na LoopNet petlji (`../PROTOCOL.md` v0.2): napaja se sa dvožične linije, čita jedan kontakt sa EOL otpornicima,
odgovara strujnim impulsom 10 mA. Pločica 30 × 20 mm, 2 sloja, sve SMD na gornjoj strani (osim stezaljki).
**Nije protivpožarni uređaj.**

```
hardware/schematic/   kompletna.svg/png: cela šema na jednom listu, svi elementi povezani; skripta kompletna.py (schemdraw)
hardware/3d/          index.html + loopnet_1in.wrl: interaktivni 3D prikaz (three.js); pravi ga pcb/export_3d.py
hardware/pcb/         make_pcb.py (raspored + mreže) -> Freerouting -> finish_pcb.py -> DRC (build.sh)
                      jlc.py: Gerber zip, BOM_JLC.csv, CPL_JLC.csv; render.py: pcb_pregled.png
firmware/             C za ATtiny1616 (avr-gcc): ln_proto.c (dekoder okvira), crt0.S, test/test_decode.py
```

## Blokovi

| Blok | Delovi | Funkcija |
|---|---|---|
| Linija | J1 ulaz, J2 izlaz (prolazno, LA/LB), D1+D2 2× BAV99 most, D3 SMAJ40A | polaritet nebitan; TVS iza mosta |
| Izvor struje | Q1 MMBT5551, Q2 MMBT3904, R1 1M, R2 3k3, D4 BZT52C10, C1 10 µF | **konstantna** struja sa linije I = Vbe(Q2)/R2 + VP/R1 ≈ 167 + 24 µA; višak kroz Zener 10 V |
| 3,3 V | U1 HT7533-1 (SOT-89, JLC Basic), C2 10 µF, C3 100 nF | Iq 2,5 µA, ulaz do 24–30 V (VC je 10 V iza Zenera) |
| Prijem | R3, R4 4M7 sa **obe žice pre mosta** → LINE (PA7), R5 330k | čvor prati liniju i na silaznoj ivici (iza mosta bi TVS kapacitet držao vrh) |
| Prag | C4 10 nF na PA6 (AC0−), puni ga DAC0 ~50 µs svakih 10 ms | osnovni nivo (ADC na PA7) + 3,5 V |
| Odgovor | Q3 MMBT5551, R6 270 Ω, R7 1k, R8 100k | (3,3 − 0,75) V / 270 Ω ≈ 9,4 mA iz VP, samo za vreme odgovora (≤ 100 µs, ~0,27 W u impulsu) |
| Ulaz | J3, R9 2k2 sa PA3 (uključen ~50 µs), R10 1k + C5 1 nF → PA4 (ADC) | EOL 2k2 serijski + 2k2 paralelno kontaktu |
| Buđenje | PA5 (AC0 OUT) vodom na PA2 | AC0 u STANDBY-u ne postavlja zastavicu ni prekid (samo OUT pin i događaj); PA2 ima potpuno asinhronu detekciju ivice i budi CPU |
| Ostalo | D5 crvena LED + R11 1k (PB1), SW1 taster (PB2, interni pull-up), J4 UPDI 1,27 mm (VDD, PA0, GND) | |

## Odstupanja od zadatih delova (i zašto)

| Zadato | Urađeno | Razlog |
|---|---|---|
| MB6S | 2× BAV99 (SOT-23, 100 V, LCSC C2500 basic) | KiCad 7 nema MBS/TO-269AA otisak, a Vishay/Diodes datasheet-ovi nisu dostupni iz kontejnera – raspored pinova i otisak MB6S nisam mogao da proverim. BAV99 ima standardan raspored (1 A, 2 K, 3 sredina), 1,5 pF umesto ~15 pF. Struja ≤ 10 mA, napon ≤ 64 V (TVS). |
| BSS126 (~0,5 mA limiter) | izvor struje sa 2 NPN, ~180 µA | Limiter od 0,5 mA bez Zenera puni kondenzator do vrha (31 V) samo za vreme impulsa: osnovna struja u prozorima bi skakala do 60 mA za 120 uređaja i prag mastera bi bio pogrešan (PROTOCOL §0). Uz Zener uređaj vuče stalno I_CC; BSS126 ima V_GS(off) rasipanje ~2:1, pa bi I_CC bio 2:1 – Vbe/R izvor drži ±10 % (0–50 °C). |
| Referenca = „filtrirani osnovni nivo + 3 V“ (RC) | ADC meri osnovni nivo, DAC0 puni C4 (sample-hold) na +3,5 V | RC usrednjavanje zavisi od gustine impulsa; proračun u PROTOCOL §1.2 pokazuje da fiksni odnos ne radi za 15–26 V. VREF + DAC stalno uključeni ne bi stali u budžet. |

### Zamena Extended → Basic (JLC)

| Ranije (Extended) | Sada | Napomena |
|---|---|---|
| TPS7B8133DRV (WSON-6) | HT7533-1 SOT-89, C14289 | VC je ograničen Zenerom na 10 V, pa 40 V ulaz nije potreban; raspored pinova proveriti |
| BCX56-16 (SOT-89) | MMBT5551 SOT-23, C2145 | 160 V, 600 mA; ~0,27 W samo u impulsima odgovora |
| R6 240 Ω 0402 | 270 Ω 0603, C22966 | odgovor ~9,4 mA (spec 10 mA ±20 %) |
| R1 2M2 | 1M 0603, C22935 | +13 µA u izvoru struje |
| R5 330k 0402 | 330k 0603, C23137 | |
| R2, C4, C5 (bez broja) | C25890, C15195, C1523 | |
| zelena LED Everlight | KT-0603R crvena, C2286 | |

Ostaju Extended: ATtiny1616, SMAJ40A, BZT52C10, R3/R4 4M7 (Basic ide do 1 MΩ, a 1 MΩ bi trošio +25 µA), stezaljke KF350 – **5 vrsta umesto ~13**.
Basic status je iz javne liste JLC Basic delova (GitHub cpldcpu/TouchSynth, `parts/jlcpcb_basic_parts.csv`), ne direktno sa jlcpcb.com.

## Provera pinova (pre rutiranja)

| Deo | Raspored korišćen u `make_pcb.py` | Izvor |
|---|---|---|
| ATtiny1616-MNR (VQFN-20) | 1 PA2 (← AC_OUT), 2 PA3, 3 GND, 4 VDD, 5 PA4, 6 PA5, 7 PA6, 8 PA7, 9 PB5, 10 PB4, 11 PB3, 12 PB2, 13 PB1, 14 PB0, 15–18 PC0–PC3, 19 PA0/UPDI, 20 PA1, EP → GND | Microchip DS40001997C, tabela 5-1 i §4.2 (PDF pročitan), unakrsno sa ATtiny1616.atdf. AC0: PA7 = AINP0, PA6 = AINN0 (i DAC0 OUT), PA5 = AC0 OUT; ADC0: PA4 = AIN4, PA7 = AIN7 |
| HT7533-1 (SOT-89) | 1 GND, 2 VIN (+ tab), 3 VOUT | **NIJE provereno u datasheet-u** (holtek.com nedostupan); raspored iz Holtek HT75xx-1 opisa u pretrazi. Klonovi (npr. HX HT7533-1(H)) imaju 2 i 3 zamenjene – naručiti tačno C14289 (Holtek) i proveriti |
| BAV99 (SOT-23) | 1 anoda D1, 2 katoda D2, 3 katoda D1/anoda D2 | standardni Nexperia raspored (datasheet nije otvoren – nexperia.com blokiran) |
| MMBT5551, MMBT3904 (SOT-23) | 1 B, 2 E, 3 C | standardni raspored; MMBT3904 već korišćen u masteru |
| (Q3 je sada MMBT5551, isti raspored kao Q1) | 1 B, 2 E, 3 C | |
| SMAJ40A (SMA), BZT52C10 (SOD-123) | pad 1 = katoda (KiCad konvencija) | katoda na VP odnosno VC |
| TS-1187A, stezaljke 3,5 mm | 1–1 i 2–2 spojeni u tasteru | isti taster kao u masteru (C318884) |

## Potrošnja (procena iz datasheet-a ATtiny1616, tabele 37-6, 37-7, 37-9, V_DD = 3 V)

| Stavka | Proračun | µA |
|---|---|---|
| AC0 u low-power režimu (stalno) | tabela 37-9 | 45 |
| STANDBY + RTC/PIT (OSCULP32K) | 0,7 + 1,2 | 2 |
| HT7533-1 I_Q | | 3 |
| Uzorak ulaza i linije svakih 10 ms | buđenje 10 µs + ~100 µs na 5 MHz (1,7 mA) + ADC (0,33 mA); pobuda EOL 1,5 mA × 50 µs | 22 + 8 |
| Okviri: SKEN svakih 250 ms | IDLE na 5 MHz (0,4 mA) od START-a do svog para: 2,85 ms + ~127 × 0,15 ms ≈ 22 ms → 9 %; + prekidi | 40 (adresa 126: 70) |
| **Ukupno unutra** | | **≈ 120 µA (najviše ~150)** |
| Izvor struje I_CC | 0,55 V / 3,3 kΩ + 24 V / 1 MΩ (25 °C); Vbe −2 mV/°C | 191 (174 pri 50 °C) |
| Delitelj prijema (sa linije, mimo izvora) | 31 V / 4,7 MΩ | 6 |
| **Struja sa linije** | konstantna, ne zavisi od rada MCU-a | **≈ 197 µA** |

Rezerva izvora prema unutrašnjoj potrošnji je ~10–40 µA (manja na toploti). Ako merenje pokaže manjak:
R2 = 3k0 (+17 µA) ili ređi SKEN (500 ms). **Ništa od ovoga nije izmereno** – sve su tipične vrednosti iz datasheet-a.

## Pločica

- 30 × 20 mm, 2 sloja, 1,6 mm; GND površine na oba sloja, šivene via; via u centralnim padovima U1 i U2 postavljene pre rutiranja.
- Razmaci: podrazumevano 0,15 mm / vod 0,2 mm; mreže sa linije (LA, LB, VP, QB, QE) **0,3 mm** (`loopnet_1in.kicad_dru`;
  IPC-2221 B4 za 31–100 V traži 0,13 mm, izmereno najmanje 0,30 mm), vodovi linije 0,4 mm. Bakar do ivice ≥ 0,3 mm.
- DRC (`pcbnew.WriteDRCReport`): **0 grešaka, 0 nepovezanih padova**; ostaje 31 informativna napomena
  „library '' not in configuration“ (otisci učitani skriptom, isto kao kod mastera).
- R3/R4 (delitelj prijema) stoje uz MCU: visokoimpedantni vod LINE je 6,6 mm (ranije 32,4 mm); LED je premeštena levo.
- Oznake komponenti su na F.Fab (na silk sloju nema mesta); natpisi na donjoj strani.
- Tok: `cd hardware/pcb && ./build.sh && python3.12 jlc.py` (Freerouting 1.9.0 u `/tmp/claude-0/fr/fr.jar` ili `FREEROUTING_JAR`).

### Narudžbina kod JLCPCB

`loopnet_1in_gerber.zip`, `BOM_JLC.csv`, `CPL_JLC.csv`. Kolona „Provera“ u BOM-u: S = LCSC broj viđen u rezultatima pretrage
(LCSC/JLC stranica), M = deo već u BOM-u mastera, **? = nije potvrđeno** (samo R3/R4 4M7 – C23163 viđen samo u pretrazi). J4 (UPDI) se ne montira.
Rotacije u CPL su KiCad-ove – proveri u JLC pregledu (SOT-23, SOT-89, WSON, VQFN). Stezaljke Kefa KF350-3.5-2P: uporedi
crtež sa otiskom Phoenix PT 1,5/2-3,5-H (raspon 3,5 mm, rupa 1,2 mm).

## Poznata ograničenja v0.1

- Nema zaštite ulaza J3 od prenapona osim R10 1k i diodi pina; kabl ulaza treba da bude kratak / u istom kućištu.
- UPDI programiranje: ili linija priključena, ili 3,3 V na J4-1 (struja unazad kroz HT7533 nije proverena).
