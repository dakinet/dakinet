# LoopNet – protokol dvožične petlje za ~120 uređaja sa jednim ulazom

Status: **nacrt v0.2** (vremena i pragovi su proračunati; potvrđuju se na prototipu, §10)

Cilj: zameniti M-Bus tamo gde treba očitati mnogo binarnih ulaza na jednoj dvožičnoj liniji,
uz **~7× manju potrošnju** i stanje cele petlje za ~42 ms. Princip je preuzet od Apollo XP95
(master menja napon, uređaj odgovara strujom, svi bitovi u taktu mastera), ali okvir, kodiranje
i komande su naši. Nije protivpožarni sistem i ne pretenduje na EN 54.

Master je postojeća pločica `apollo-loop-driver` (RP2040, nivoi 24,2 / 31,2 V, šant 1 Ω + MCP6002 ×5,02,
komparator MCP6561 sa PWM pragom, hardverska zaštita 500 mA) – hardver se ne menja, samo firmver.
Uređaj je „LoopNet 1IN“ (`child/`): ATtiny1616, jedan ulaz sa EOL otpornicima, taster, LED.

## 0. Šta se promenilo u odnosu na v0.1 (i zašto)

| # | v0.1 | v0.2 | Razlog |
|---|---|---|---|
| 1 | Bitovi kodirani **širinom** impulsa, odgovor od **silazne** ivice | Bitovi kodirani **periodom između uzlaznih ivica**; sva vremena uređaja mere se od uzlazne ivice | Izlaz mastera je emiter-sledilac (TIP122) **bez aktivnog spuštanja**: silazna ivica traje C_kabla·ΔU / I_opterećenja – 35 µs pri 120 uređaja, ali > 250 µs pri 10 uređaja na 1 km. Uzlaznu ivicu master gura aktivno (~20 µs, nezavisno od opterećenja). |
| 2 | Uređaj troši „do 200 µA“, zavisno od trenutka | Uređaj vuče sa linije **konstantnu struju** I_CC ≈ 195 µA (izvor struje + Zener), nezavisno od napona i od rada MCU-a | Prag mastera je „struja mirovanja + 5 mA“. Kad bi uređaji punili kondenzatore samo na 31 V (vršni detektor), osnovna struja bi u prozorima skakala do 120 × 0,5 mA = 60 mA i prag bi bio pogrešan. Konstantna struja = mirna osnovna linija i nema strujnih udara na ivicama. |
| 3 | Fiksni prozor 100 µs (30 + 70) | Prozor T_W = 150 µs podrazumevano, master ga bira 150–400 µs; uređaj ga meri u prozoru 0 | 100 µs ne ostavlja mesta za silaznu ivicu + smirivanje strujne petlje mastera; T_W se produžava kod dugog kabla i malog opterećenja. |
| 4 | Prozori 0–255, „0, 1, 254, 255 se ne koriste“, ali 2N+1 za N=126 je 253 | Prozor 0 = referentni (niko ne odgovara); uređaj N koristi **2N−1** i **2N** (N = 1…127) → prozori 1…254 | Doslednost brojanja; par za adresu 127 otkriva nedodeljene uređaje; prozor 0 daje master-u proveru praga i uređaju meru T_W. |
| 5 | Zaglavlje „~2,75 ms“ | 2,85 ms prosečno, najviše 3,4 ms (§2) | Ponovo sabrano. |
| 6 | LED „detalji u v0.2“, DODELI ADRESU prihvata i adresu 127 | Komande sa **parametrom** (8 b + parnost); DODELI prihvata **samo** uređaj kom je taster držan 3 s | Više nedodeljenih uređaja (127) bi istovremeno uzelo istu adresu. |
| 7 | 3 km pri 120 uređaja | 1 km pri T_W = 150 µs; duže samo uz duži T_W | Kapacitet 3 km ≈ 300 nF: puna silazna ivica ≈ 85 µs. |
| 8 | Prag prijema u uređaju nije definisan | Prag = izmereni osnovni nivo + 3,5 V (ADC + DAC u ATtiny1616), §1.2 | Napon na uređaju je 15–24 V zavisno od pada na kablu; obično RC usrednjavanje pomera prag sa gustinom saobraćaja (proračun u §1.2). |

## 1. Fizički sloj

| Parametar | Vrednost |
|---|---|
| Kabl | 2 žice, upredena parica (npr. J-Y(St)Y 2×2×0,8: 34 Ω/km po žici, ≤ 100 nF/km); magistrala ili stablo; prsten se vraća na LOOP IN samo radi nadzora prekida |
| Dužina | do 1 km pri T_W = 150 µs (§1.3); duže uz veći T_W |
| Polaritet | nebitan (mostni ispravljač u uređaju) |
| Osnovni nivo (mirovanje, pauza) | 24,2 V na masteru |
| Impuls master → uređaj | +7,0 V (31,2 V); uzlazna ivica 10–90 % ≈ 20 µs (VSET τ ≈ 9 µs), aktivno |
| Silazna ivica | pasivna: pražnjenje kabla kroz opterećenje, t ≈ C·ΔU/I (§1.3) |
| Potrošnja uređaja | **konstantna** I_CC ≈ 195 µA (180–215 µA za 0–50 °C: izvor Vbe/R sa dva NPN + delitelj prijema), ne zavisi od rada MCU-a; između 24 i 31 V raste ~7 µA |
| Odgovor uređaj → master | dodatni strujni ponor **10 mA ±20 %** (konstantna struja, NPN + R_E) |
| Najmanji napon na uređaju | 15 V u osnovnom nivou (14,3 V za vreme sopstvenog odgovora) |
| Adrese | 1–126 radne; 0 = broadcast; 127 = nedodeljena (fabričko stanje) |

### 1.1 Prijem kod mastera

- Prag komparatora: **I_0 + 5 mA**, gde je I_0 struja mirovanja izmerena ADC-om (IAMP) neposredno pre okvira
  (PWM prag ima τ = 10 ms, pa se postavlja jednom pre okvira, ne u toku njega).
- Pošto uređaji vuku konstantnu struju, struja u osnovnom nivou za vreme okvira jednaka je I_0. Prozor 0 služi kao provera:
  ako je komparator u prozoru 0 „1“, okvir se odbacuje (pogrešan prag ili smetnja).
- Rezerva: odgovor 8–12 mA prema pragu 5 mA (±3 mA); offset MCP6561 ±10 mV / 5,02 = ±2 mA.
- Master uzorkuje komparator u intervalu **0,70–0,87 T_W** od svoje uzlazne ivice takta (105–130 µs pri T_W = 150 µs),
  i to tek kad je linija sišla na osnovni nivo i strujna petlja mastera se smirila (dok linija pada, master ne daje struju
  i šant ne vidi ni opterećenje ni odgovor).

### 1.2 Prijem kod uređaja

- Delitelj sa **obe žice pre mosta** (2 × 4,7 MΩ ka čvoru, 330 kΩ ka masi uređaja): čvor prati liniju bez obzira na polaritet i ne „pamti“
  vrh kao čvor iza mosta (kapacitet TVS-a iza mosta bi držao 31 V stotinama µs). Odnos ≈ 1/17, Thevenin ≈ 290 kΩ, τ ≈ 3 µs sa ulazom AC-a.
- Komparator AC0 u ATtiny1616 (PA7 = AINP0, PA6 = AINN0, low-power režim 45 µA): + ulaz = delitelj, − ulaz = kondenzator 10 nF na PA6
  koji puni DAC0 (izlaz na PA6). Firmver svakih 10 ms meri osnovni nivo ADC-om na PA7 (samo dok je linija na osnovnom nivou),
  na ~50 µs uključi DAC0 na **osnovni nivo + 3,5 V** (korak ≈ 0,17 V linije) i ponovo ga isključi – „sample-hold“, jer VREF + DAC
  ne bi stali u budžet kad bi radili stalno. Histerezis AC 25 mV ≈ 0,4 V linije.
- Zašto ne RC filter (analogni „usrednjeni nivo + ofset“): srednja vrednost linije zavisi od gustine impulsa (u okviru do ~35 % trajanja na 31 V)
  i od pada na kablu (osnovni nivo 15–24 V). Za prag fiksnog odnosa r = U_ref/U_ulaz uslovi „prag ≥ osnovni + 1,5 V pri 15 V bez saobraćaja“ i
  „prag ≤ osnovni + 5,5 V pri 26 V usred okvira“ daju r > 1,107 i r < 1,107 – nema rešenja. Merenje osnovnog nivoa ADC-om nema taj problem.

### 1.3 Ivice, kapacitet i opterećenje (1 km, 120 uređaja)

| Veličina | Proračun | Vrednost |
|---|---|---|
| Kapacitet kabla | 1 km × ≤ 100 nF/km | ≤ 100 nF |
| Kapacitet uređaja | 120 × ~200 pF (most + TVS + delitelj) | ≈ 24 nF |
| Ukupno C | | ≈ 125 nF |
| Struja punjenja na uzlaznoj ivici | 125 nF × 7 V / 20 µs | ≈ 44 mA (+ opterećenje), master daje do 540 mA |
| RC kabla (68 Ω petlja) | 0,4 × 68 Ω × 125 nF | ≈ 3,5 µs kašnjenja na kraju |
| Opterećenje | 120 × 0,18 mA + master 0,6 mA (R8/R9, R10/R11) | ≈ 22 mA |
| Silazna ivica do praga (−3,9 V) | 125 nF × 3,9 V / 22 mA | ≈ 22 µs |
| Silazna ivica do osnovnog nivoa (−7 V) | 125 nF × 7 V / 22 mA | ≈ 40 µs |

**Pravilo za malo opterećenje.** Silazna ivica do praga mora da stane u pauzu bita 0 (110 µs) sa rezervom:
**I_opt [mA] ≥ 0,04 × C [nF]**. Primer: 10 uređaja na 1 km (C ≈ 102 nF, I ≈ 2,4 mA) traži ≥ 4,1 mA → na kraj linije
**završni otpornik 15 kΩ / 0,25 W** (1,6 mA). Sa ≥ 25 uređaja na 1 km otpornik nije potreban.
Za prozore važi strože (puna ivica + smirivanje ≤ 0,6 T_W): master pri uključenju meri pad VLOOP posle impulsa i bira T_W (150, 200, 300 ili 400 µs).

## 2. Okvir

```
napon  31V ┌──START 500──┐   ┌┐     ┌┐         ┌┐   ┌┐   ┌┐   ┌┐        ┌┐
       24V ┘             └───┘└─────┘└─────────┘└───┘└───┘└───┘└── ... ─┘└──
           |<----- 650 ----->|<150>|<-- 250 -->|  ..11 simbola..  |W0 |W1 |W2 ...
                              bit 0   bit 1                        T_W  T_W
struja                                                                  ▄▄     ← +10 mA = odgovor
```

Svaki simbol posle START-a je impuls 31 V dužine **40 µs**; vrednost nosi **period do sledeće uzlazne ivice**.

| Element | Master šalje | Uređaj prihvata |
|---|---|---|
| START | 500 µs na 31 V, zatim 150 µs pauze (period 650 µs) | impuls ≥ 250 µs na svom komparatoru |
| Simbol (bit zaglavlja, parametra, takt prozora) | 40 µs na 31 V | – |
| bit 0 | period 150 µs | 100–195 µs |
| bit 1 | period 250 µs | 205–330 µs |
| period > 330 µs ili < 100 µs u zaglavlju | – | greška: čeka sledeći START |
| prozor odgovora | period T_W (150 µs podr., 150–400) | T_W meri u prozoru 0 (period W0→W1), prihvata 130–450 µs |
| ponor uređaja uključen | – | od **0,30 T_W** do **0,95 T_W** posle svoje uzlazne ivice (45–143 µs) |
| uzorkovanje mastera | **0,70–0,87 T_W** posle svoje uzlazne ivice (105–130 µs) | – |
| razmak između okvira | ≥ 500 µs na osnovnom nivou | – |

Zaglavlje: **3 bita komande (MSB prvi), 7 bita adrese (MSB prvi), 1 bit parne parnosti** = 11 simbola.
Komande sa parametrom (§3) posle zaglavlja šalju još **8 bita parametra (MSB prvi) + 1 bit parne parnosti**.
Posle toga ide **prozor 0** (niko ne odgovara) i prozori odgovora 1…K. Okvir se završava poslednjim prozorom
(uređaj zna K iz komande); sledeći okvir počinje START-om.

Trajanje: START 650 µs + 11 simbola × 150–250 µs = **2,3–3,4 ms** (prosek 2,85 ms) + (1 + K) × T_W.

Vremenske rezerve uređaja (ATtiny1616 na 10 MHz iz OSC20M, tolerancija ±3 %):
- dužine i periodi mere se **hardverski** (TCB u režimu merenja perioda/širine, događaj iz AC0) – latencija prekida ne utiče na merenje;
- odluka o odgovoru u prekidu: buđenje iz IDLE + ulaz u prekid ≈ 2 µs, obrada ≤ 15 µs, a prvi ponor kreće tek na 0,30 T_W = 45 µs;
- ±3 % na 143 µs = ±4 µs; ponor je sigurno uključen u 55–135 µs, master uzorkuje 105–130 µs;
- tačka detekcije uzlazne ivice (polovina ivice + kašnjenje kabla) kasni 10–14 µs za ivicom mastera; to je uračunato u 0,30/0,70 T_W.

## 3. Komande

| Kod | Ime | Adresa | Parametar | Odgovor (prozori 1…K) |
|---|---|---|---|---|
| 0 | SKEN | 0 | – | K = 254: par prozora po adresi (§4) |
| 1 | DOGAĐAJI | 0 | – | K = 254: prozor 2N−1 = ima zapamćen događaj, 2N = nema |
| 2 | STATUS | 1–126 | – | K = 16 (§5) |
| 3 | POTVRDI | 0 ili 1–126 | – | adresirano: K = 1 (potvrda); broadcast: K = 0. Briše zapamćen događaj |
| 4 | INFO | 1–126 | – | K = 32: tip 8 b, verzija fw 8 b, napon na uređaju 8 b (×0,2 V), CRC-8 (poli 0x07, poč. 0) prva 3 bajta; LSB prvi |
| 5 | DODELI ADRESU | 0 | nova adresa 1–126 | K = 1: potvrda; prihvata **samo** uređaj čiji je taster držan 3 s (mod dodele traje 60 s) |
| 6 | LED | 1–126 ili 0 | 0 = ugasi, 1 = upali (trepće 50 ms / 1 s), 2 = identifikacija (brzo trepće 10 s), ostalo rezerva | adresirano K = 1 (potvrda); broadcast K = 0 |
| 7 | rezerva (KONFIG) | | | |

Uređaj koji primi neispravnu parnost, period van opsega ili prekinut okvir ignoriše okvir do sledećeg START-a.
Posle uspešne DODELE uređaj odmah koristi novu adresu i upisuje je u EEPROM; master proverava SKEN-om.

## 4. SKEN – stanje cele petlje u jednom okviru

Uređaj sa adresom N (1–127) odgovara u prozorima **2N−1** i **2N** (prozori 1–254; prozor 0 je referentni):

- prozor 2N−1: struja ako je ulaz **aktivan**
- prozor 2N: struja ako je ulaz **neaktivan**

Ispravan uređaj daje tačno jedan impuls po paru. Master tumači:

| 2N−1 | 2N | Značenje |
|---|---|---|
| 1 | 0 | ulaz aktivan |
| 0 | 1 | ulaz neaktivan |
| 0 | 0 | uređaj odsutan / prekid kabla |
| 1 | 1 | sukob: dupla adresa ili uređaj izgubio brojanje taktova |

- „Aktivan“ = kontakt zatvoren **ili** greška linije ulaza (kratak spoj / prekid EOL kola). Vrsta greške se čita STATUS-om, a greška postavlja zapamćen događaj.
- Par za **N = 127** (prozori 253, 254): odgovaraju svi nedodeljeni uređaji → „1 1“ ili „0 1“ znači da na petlji ima nedodeljenih uređaja.
- Trajanje pri T_W = 150 µs: 2,85 ms + 255 × 150 µs ≈ **41 ms** (do ~24 skena u sekundi). Podrazumevano master šalje SKEN svakih
  **250 ms** i DOGAĐAJI po potrebi; ostatak vremena petlja miruje (uređaji spavaju, §6.1).

## 5. STATUS (16 bita, LSB prvi)

| Bitovi | Sadržaj |
|---|---|
| 0–1 | ulaz: 00 otvoren, 01 zatvoren, 10 kratak spoj linije ulaza, 11 prekid linije ulaza |
| 2 | zapamćen događaj (promena od poslednje POTVRDE) |
| 3 | nizak napon na uređaju (osnovni nivo < 15 V) |
| 4–7 | brojač promena ulaza (mod 16) |
| 8–14 | eho adrese |
| 15 | parna parnost bitova 0–14 |

## 6. Ponašanje uređaja

- Ulaz se uzorkuje svakih 10 ms: pin za čitanje (2,2 kΩ ka liniji ulaza) uključen ~50 µs, ADC meri napon; filter: 3 uzastopna ista uzorka.
- Pragovi (EOL 2 × 2,2 kΩ: serijski + paralelno kontaktu; U/VDD): < 0,18 kratak spoj; 0,18–0,58 zatvoren (2,2 kΩ → 0,50); 0,58–0,83 otvoren (4,4 kΩ → 0,67); > 0,83 prekid.
- Svaka potvrđena promena: ažurira stanje, uvećava brojač, postavlja „zapamćen događaj“.
- Bez ispravnog okvira duže od 2 s → kratak blesak LED-a svake 2 s (gubitak komunikacije), nastavlja da sluša.
- Adresa u EEPROM-u; fabrički 127. Taster: kratko = trepni adresu LED-om (desetice dugo, jedinice kratko), dugo (3 s) = mod DODELE 60 s (LED trepće).

### 6.1 Spavanje

- Između okvira: STANDBY, rade samo AC0 (low-power) i RTC/PIT (10 ms za ulaz i osvežavanje praga). AC0 u STANDBY-u ne budi CPU sam (bez CLK_PER ne postavlja prekid), pa njegov izlaz PA5 ide vodom na PA2 (asinhroni prekid pina). Buđenje uzlaznom ivicom; ako linija posle 300 µs i dalje stoji na 31 V → START.
- U okviru: IDLE, TCB meri periode hardverski; CPU se budi na svakoj uzlaznoj ivici zaglavlja.
- SKEN/DOGAĐAJI: posle zaglavlja TCA0 broji uzlazne ivice (događaj iz AC0) do prozora 2N−2, CPU spava; budi se samo za svoj par.
- Okvir koji nije za uređaj: CPU gasi buđenje i spava do procenjenog kraja okvira (K × T_W − 10 %), zatim ponovo čeka START.

## 7. Budžet (120 uređaja, 1 km 0,8 mm)

| | LoopNet | M-Bus |
|---|---|---|
| Struja linije u mirovanju | 120 × 0,18 mA ≈ **22 mA** | 120 × 1,5 mA = 180 mA |
| Snaga na petlji | 24,2 V × 22 mA ≈ 0,53 W | 36 V × 180 mA ≈ 6,5 W |
| Pad napona, sve na kraju kabla (68 Ω) | 1,5 V (+0,7 V za vreme odgovora) | 12 V |
| Pad napona, uređaji ravnomerno | ≈ 0,75 V | ≈ 6 V |
| Najmanji napon na uređaju | 24,2 − 1,5 − 0,7 = 22 V (zahtev ≥ 15 V) | |
| Stanje svih uređaja | ≈ 41 ms (SKEN) | ≈ 6–25 s |

Potrošnja uređaja: struja sa linije je konstantna I_CC (izvor struje), a unutrašnja potrošnja mora biti manja od
najmanjeg I_CC (~160 µA kroz izvor pri 50 °C); višak odlazi kroz Zener. Procena unutrašnje potrošnje je u `child/README.md`.

## 8. Granice i rezerve

- 127 adresa (126 radnih), 254 prozora po SKEN-u.
- Na liniji ne sme biti drugih potrošača sa promenljivom strujom većom od ~1 mA (pomera I_0).
- Dužina kabla × broj uređaja: proveriti pravilom iz §1.3; master pri pokretanju javlja izmerenu silaznu ivicu i izabrani T_W.

## 9. Greške i oporavak

- Uređaj: bilo koji period van opsega → čeka START. Okvir koji traje duže od očekivanog → isto.
- Master: „1“ u prozoru 0 → okvir odbačen, prag ponovo izmeren. „1 1“ u SKEN-u → sukob adresa ili greška brojanja; ponavlja SKEN,
  pa STATUS te adrese (eho adrese).
- Zaštita mastera (kratak spoj > 500 mA, prekid petlje VRET) je ista kao u Apollo režimu.

## 10. Otvorena pitanja za prototip

- Izmeriti I_CC po primerku (BSS126 V_GS(off) rasipanje) i unutrašnju potrošnju u svim režimima.
- Izmeriti silaznu ivicu sa 10 uređaja na kolutu 500 m / 1 km sa i bez završnog otpornika; potvrditi pravilo I ≥ 0,04·C.
- Pad napona na C4 (prag) između dva osvežavanja (curenje AC ulaza) i stvarna potrošnja AC0 u STANDBY-u.
- CRC umesto parnosti u zaglavlju (greška obično pomera brojanje, što hvata provera perioda i par prozora).
