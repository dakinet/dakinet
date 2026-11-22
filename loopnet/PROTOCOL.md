# LoopNet – protokol dvožične petlje za ~120 uređaja sa jednim ulazom

Status: **nacrt v0.1** (predlog, vrednosti se potvrđuju na prototipu)

Cilj: zameniti M-Bus tamo gde treba očitati mnogo binarnih ulaza na jednoj dvožičnoj liniji,
uz **10× manju potrošnju** i stanje cele petlje za ~30 ms. Princip je preuzet od Apollo XP95
(master menja napon, uređaj odgovara strujom, svi bitovi u taktu mastera), ali okvir, kodiranje
i komande su naši. Nije protivpožarni sistem i ne pretenduje na EN 54.

Master je postojeća pločica `apollo-loop-driver` (RP2040, nivoi 24,2 / 31,2 V, šant 1 Ω + MCP6002 ×5,02,
komparator MCP6561, hardverska zaštita 500 mA) – hardver se ne menja, samo firmver.

## 1. Fizički sloj

| Parametar | Vrednost |
|---|---|
| Kabl | 2 žice, upredena parica (npr. J-Y(St)Y 2×2×0,8); magistrala, stablo ili prsten |
| Polaritet | nebitan (mostni ispravljač u uređaju) |
| Osnovni nivo (mirovanje, logička pauza) | 24 V (master: 24,2 V) |
| Impuls master → uređaj | 31 V (master: 31,2 V), ivice ~20 µs |
| Odgovor uređaj → master | strujni ponor **10 mA ±20 %** (konstantna struja) |
| Prag prijema kod mastera | struja mirovanja (merena u pauzi) + 5 mA |
| Zabrana merenja posle ivice napona | 30 µs (punjenje kapaciteta kabla i uređaja) |
| Potrošnja uređaja u mirovanju | cilj ≤ 200 µA, uključujući punjenje kondenzatora na ivicama |
| Najmanji napon na uređaju | 14 V osnovni nivo (radi i sa ~3 km kabla 0,8 mm pri 120 uređaja) |
| Adrese | 1–126; 0 = broadcast; 127 = nedodeljena (fabričko stanje) |

## 2. Okvir

```
napon  31V ┌──START──┐  ┌┐ ┌─┐ ┌┐ ...11 bita...      ┌┐  ┌┐  ┌┐ ...N taktova
       24V ┘ 600 µs  └──┘└─┘ └─┘└───────────────────┘└──┘└──┘└──
struja                                                   ▄▄      ▄▄   ← +10 mA = bit 1
```

| Element | Vreme (početne vrednosti, podesive) |
|---|---|
| START impuls | 600 µs (uređaj prihvata 450–900 µs) |
| pauza posle START-a | 200 µs |
| bit 0 | impuls 100 µs (prihvata 60–140 µs) |
| bit 1 | impuls 200 µs (prihvata 160–260 µs) |
| pauza između bitova | 100 µs |
| takt odgovora | impuls 30 µs, zatim prozor 70 µs na osnovnom nivou |
| uređaj uključuje ponor | 5 µs posle silazne ivice takta, drži do 60 µs |
| master uzorkuje struju | 35–60 µs posle silazne ivice takta |
| razmak između okvira | ≥ 300 µs |

Zaglavlje: **3 bita komande (MSB prvi), 7 bita adrese (MSB prvi), 1 bit parne parnosti** = 11 bita.
Uređaj koji primi neispravnu parnost ili dužinu impulsa van opsega ignoriše okvir do sledećeg START-a.

## 3. Komande

| Kod | Ime | Adresa | Odgovor (taktova) |
|---|---|---|---|
| 0 | SKEN | 0 | 256: par prozora po adresi (vidi §4) |
| 1 | DOGAĐAJI | 0 | 256: prozor 2N = ima zapamćen događaj, 2N+1 = nema |
| 2 | STATUS | 1–126 | 16 (§5) |
| 3 | POTVRDI | 0 ili 1–126 | 0 (briše zapamćen događaj) |
| 4 | INFO | 1–126 | 32: tip 8 b, verzija fw 8 b, napon na uređaju 8 b (×0,2 V), CRC-8 |
| 5 | DODELI ADRESU | nova adresa | 1: potvrda; prihvata samo uređaj sa pritisnutim tasterom (ili adresom 127) |
| 6 | LED/IZLAZ | 1–126 | 0; sledeći okvir istoj adresi sa bitom 0 gasi (detalji u v0.2) |
| 7 | rezerva | | |

## 4. SKEN – stanje cele petlje u jednom okviru

Uređaj sa adresom N (1–126) odgovara u prozorima **2N** i **2N+1** (prozori 0–255; 0, 1, 254, 255 se ne koriste):

- prozor 2N: struja ako je ulaz **aktivan**
- prozor 2N+1: struja ako je ulaz **neaktivan**

Ispravan uređaj daje tačno jedan impuls po paru. Master tumači:

| 2N | 2N+1 | Značenje |
|---|---|---|
| 1 | 0 | ulaz aktivan |
| 0 | 1 | ulaz neaktivan |
| 0 | 0 | uređaj odsutan / prekid kabla |
| 1 | 1 | sukob: dupla adresa ili uređaj izgubio brojanje taktova |

Trajanje: ~2,75 ms zaglavlje + 256 × 100 µs ≈ **28 ms** (≈35 skenova u sekundi).
Kombinacija **1 1** je rezervisana za grešku na petlji. Greška na liniji ulaza (kratak spoj ili prekid EOL
kola) javlja se u SKEN-u kao „aktivan“ uz zapamćen događaj, a vrsta greške se čita STATUS-om.

## 5. STATUS (16 bita, LSB prvi)

| Bitovi | Sadržaj |
|---|---|
| 0–1 | ulaz: 00 otvoren, 01 zatvoren, 10 kratak spoj linije ulaza, 11 prekid linije ulaza |
| 2 | zapamćen događaj (promena od poslednje POTVRDE) |
| 3 | nizak napon napajanja uređaja |
| 4–7 | brojač promena ulaza (mod 16) |
| 8–14 | eho adrese |
| 15 | parna parnost bitova 0–14 |

## 6. Ponašanje uređaja

- Ulaz se uzorkuje svakih 10 ms (otpornik za čitanje uključen samo ~50 µs), filter od smetnji 3 uzastopna uzorka.
- Svaka potvrđena promena: ažurira stanje, uvećava brojač, postavlja „zapamćen događaj“.
- Bez okvira duže od 2 s → uređaj trepne LED-om (gubitak komunikacije), nastavlja da sluša.
- Adresa u EEPROM-u; fabrički 127. Taster: kratko = trepni adresu LED-om, dugo (3 s) = spreman za DODELI ADRESU.

## 7. Budžet (120 uređaja)

| | LoopNet | M-Bus |
|---|---|---|
| Struja linije u mirovanju | ≈ 24 mA | 180 mA |
| Snaga mastera | ≈ 1 W | ≈ 7 W |
| Pad napona, 1 km kabla 0,8 mm (70 Ω po paru) | ≈ 2,4 V | ≈ 14 V |
| Stanje svih uređaja | ≈ 28 ms | ≈ 6–25 s |

## 8. Otvorena pitanja za prototip

- Stvarna potrošnja uređaja i strujni udari na ivicama sa 120 uređaja i 1 km kabla.
- Da li 100 µs po prozoru drži sa ATtiny1616 na internom oscilatoru (latencija prekida) – inače 150 µs.
- Kapacitet kabla i usporenje ivica: ugao ivice mastera vs. vreme zabrane merenja.
- CRC umesto parnosti u zaglavlju (v0.2).
