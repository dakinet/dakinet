# Apollo XP95 laboratorijski drajver petlje

Elektronika koja sama napaja Apollo adresabilnu petlju, proziva uređaje XP95/Discovery protokolom
i čita njihove strujne odgovore. **Samo za laboratoriju** – uređaj nije sertifikovan po EN 54 i ne sme
se priključiti na petlju koja štiti ljude ili objekat.

| | |
|---|---|
| Napajanje | 24 V DC (21–28 V), kao protivpožarna centrala |
| Petlja | 24,2 V osnovni nivo, 31,2 V impuls, do ≈ 540 mA (ograničenje), PTC 750 mA |
| Mozak | RP2040 na ploči (flash W25Q16, kristal 12 MHz), MicroPython, PIO + DMA |
| USB | USB-B, galvanski odvojen preko ADuM3160 (posebna masa GND_USB) |
| Pločica | 130 × 95 mm, 2 sloja, sve na ploči (bez modula), 9 funkcionalnih blokova |

## Sadržaj

```
hardware/schematic/   električna šema u 4 lista (SVG/PNG) i skripte koje je crtaju (schemdraw)
hardware/pcb/         KiCad 7 pločica, Gerber + drill (apollo_loop_driver_gerber.zip), BOM, DRC izveštaj
  make_pcb.py         raspored komponenti i mreže (izvor istine za pločicu)
  finish_pcb.py       uvoz vodova iz Freerouting-a, GND površine i šivenje
  build.sh            ceo tok: raspored -> rutiranje -> DRC
firmware/             MicroPython za Pico: config.py, loopdrv.py, main.py
```

## Pločica (v0.2)
Sve je na ploči, bez spoljnih modula. Blokovi (okviri i nazivi na F.Fab sloju):

| Blok | Sadržaj | Pravila rasporeda |
|---|---|---|
| 1 USB izolacija | USB-B, ADuM3160, 27 Ω | posebna masa GND_USB, traka 2,3 mm bez bakra ispod U8 |
| 2 Ulaz 24 V | stezaljka, osigurač 3 A, SS34 | na ivici, kratki vodovi |
| 3 Boost 34 V | LM2587S-ADJ, 100 µH, SS56, 2×470 µF + 10 µF + 1 µF | po TI referenci „24-V To 36-V Boost“ (slika 20) i rasporedu sa slike 63: C31 4,2 mm od VIN, L1 4,7 mm od SW, C5/C63 4–5 mm od katode, FB/COMP otpornici 6–8 mm od pinova, 16 termalnih via ispod tab-a |
| 4 Napajanje 5V/3V3 | R-78E5.0, AP2112K-3.3 | ulazni/izlazni kondenzatori uz pinove |
| 5 MCU | RP2040, W25Q16, 12 MHz, BOOTSEL/RESET, SWD | 100 nF uz svaki IOVDD, kristal uz XIN/XOUT, 9 via u centralnom padu |
| 6 Referenca i nivo | REF3033, delitelj, 2N7002 | daleko od SW čvora |
| 7 Drajver 34 V | OPA197, TIP122 položen na hladnjak Aavid TV5G, BC847, 1,2 Ω | V+ OPA197 okrenut ka C13/C58 |
| 8 Izlaz i zaštita | PTC 750 mA, SMBJ36A, delitelj VLOOP + 1 nF | |
| 9 Merenje struje | šant 1 Ω, MCP6002 (×5,02), MCP6561, VRET + 1 nF | odvojeno od boost-a |
| 10 Zaštita KS | MCP6561 + zadrška (D6/R36), Q6 gasi VSET, Q7 briše | prag ≈ 494 mA, reakcija u µs |

Razmaci: signali 0,15 mm / 0,2 mm vod; mreže do 34 V **0,6 mm** (IPC-2221 B2, spoljni sloj);
USB strana prema ostatku **2 mm** (`apollo_loop_driver.kicad_dru`). GND površine na oba sloja,
šivene via na 5 mm.

Razdvajanje i filtri: 100 nF uz svaki IC (RP2040 ×8, flash, ADuM ×2, op-pojačavači, REF3033),
1 µF na VREG/DVDD, ADuM VBUS/VDD 1–10 µF; boost 1 µF + 100 µF ulaz, 1 µF + 2×220 µF izlaz;
RC filteri na ADC ulazima (VLOOP, VRET 1 nF, IAMP 1 kΩ/1 nF), PWM prag 10 kΩ/1 µF.

**Pre naručivanja proveri** raspored pinova iz datasheet-a: LM2587 (TO-263-5: 1 COMP, 2 FB, 3 GND/tab, 4 SW, 5 VIN),
ADuM3160 (SOIC-16W), RP2040 (QFN-56), W25Q16JV (SOIC-8 208 mil), AP2112K (SOT-23-5), REF3033, MCP6561,
2N7002/BC847 i TIP122. Pločica je napravljena programski (`make_pcb.py`), bez KiCad šeme (.kicad_sch).

## Narudžbina kod JLCPCB
`python3.12 hardware/pcb/jlc.py` (posle `build.sh`) pravi:
- `apollo_loop_driver_gerber.zip` – Gerber + drill za izradu pločice (2 sloja, 1,6 mm)
- `BOM_JLC.csv` – sve stavke sa LCSC brojevima (kolone Comment, Designator, Footprint, LCSC Part #)
- `CPL_JLC.csv` – pozicije delova (Designator, Mid X, Mid Y, Layer, Rotation)

Zamene zbog JLC kataloga: L1 SRR1280-101M (isti otisak kao SRR1260, Isat 2,0 A, vršna struja ≈ 1,4 A),
Q4 MMBT3904 umesto BC847, tasteri XKB TS-1187A, kondenzatori kristala 33 pF (kristal C9002, CL 20 pF).
Hladnjak TV5G nije u katalogu – montira se ručno. Montažne rupe H1–H4: Ø3,2 mm za M3, pometalisane sa prstenom 6,4 mm na obe strane, nisu povezane na masu (kućište ne sme da napravi zemljospoj kad je pločica na petlji centrale). Rotacije u CPL su KiCad-ove: proveri ih u JLC pregledu
pre potvrde (najčešće treba okrenuti SOT-23, SOIC i QFN). USB-B10-BRW: pre narudžbine uporedi crtež
otiska sa OST USB-B1HSxx. Malo na stanju: ADuM3160 i LM2587S-ADJ.

## Kratak spoj i prekid petlje
- **Kratak spoj / preopterećenje:** šant R14 (1 Ω) meri struju petlje; kad pređe ≈ 500 mA, U12 okida za nekoliko µs,
  Q6 spušta VSET i petlja se gasi bez učešća procesora. D6/R36 drže stanje (latch) dok firmver ne pusti OC_RST.
  Do okidanja struju ograničava Q4/R7 na ≈ 540 mA. Firmver javlja `kratak_spoj` i petlja se pali ponovo komandom `on`.
- **Prekid linije (otvoreno kolo):** napon na povratku petlje (J3, VRET) < 50 % izlaza → `prekid_petlje`.
- Posle uključenja zaštita je blokirana 20 ms (punjenje kapaciteta petlje, do 0,5 µF).

## Snaga delova
| Deo | Normalno (0,5 A) | Kratak spoj (≤ 0,54 A do okidanja) | Izabrano |
|---|---|---|---|
| R7 1,2 Ω | 0,30 W | 0,35 W | 2512, 1 W (pulsni, npr. Vishay WSL2512 / Yageo PE2512) |
| R14 1 Ω | 0,25 W | 0,29 W | 2512, 1 W, 1 % |
| TIP122 | (34 − 24 V) × I = 5 W pri 500 mA, 0,5 W pri 50 mA | kratko, do okidanja | TO-220 položen + TV5G |

**Hladnjak:** Aavid TV5G ima ≈ 21 °C/W. Uz TIP122 (θjc 1,92 °C/W) i 40 °C okoline, TV5G je dovoljan do ≈ 200 mA
trajno (Tj ≈ 90 °C). Za trajnih 500 mA treba hladnjak ≤ 8 °C/W ili ventilator (Tj bi sa TV5G bila ≈ 157 °C).
Tab TIP122 je kolektor (+34 V) – hladnjak ne sme dodirivati masu, ili koristi izolacionu podlošku.

## Firmver
Prvo uključenje: drži BOOTSEL, priključi USB i prevuci MicroPython UF2 za RP2040 (Raspberry Pi Pico build radi, isti pinovi). Zatim kopiraj `firmware/*.py` (npr. Thonny). Na USB serijskom portu:

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
- centrala L− → GND pločice (J1-2), ploča napajana sa 24 V na J1
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
