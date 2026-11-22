# Projekat dakinet – uputstvo za Claude Code

Korisnik (Dalibor) radi u protivpožarnim i sigurnosnim sistemima. **Odgovaraj na srpskom, latinicom, kratko i konkretno.**
Commit poruke na engleskom, kratko zašto. Posle svake celine: commit + push, i kratko javi šta je urađeno,
šta je izmereno/provereno, a šta nije.

## Sadržaj repoa

| Folder | Šta je | Stanje |
|---|---|---|
| `apollo-loop-driver/` | Laboratorijski master za Apollo XP95 petlju (RP2040, 24,2/31,2 V, 500 mA), 130×95 mm, MicroPython | pločica gotova za JLCPCB; **ne menjati hardver bez pitanja** |
| `loopnet/PROTOCOL.md` | Sopstveni protokol LoopNet v0.2 (zamena za M-Bus, ~120 uređaja, 1 ulaz po uređaju) | gotovo |
| `loopnet/child/` | Uređaj „LoopNet 1IN“ v0.1: ATtiny1616, 30×20 mm | pločica, šema, BOM gotovi; firmver: samo dekoder + host test |
| `apollo-loop-module/` | **U RADU**: kompaktni Apollo loop driver MODUL (60×45 mm, 24 V ulaz, boost 34 V, do 250 mA, UART 3,3 V) | netlista gotova, raspored u toku – vidi `HANDOFF.md` |

Detaljno stanje, odluke i sledeći koraci: **`HANDOFF.md`**.

## Alati i tok rada (pločice se prave skriptama, ne ručno u KiCad-u)

- `hardware/pcb/make_pcb.py` – raspored + mreže (izvor istine), `--samo-proveri --slika` daje preklapanja i `raspored.png`
- `build.sh` – make_pcb → Freerouting 1.9.0 (`FREEROUTING_JAR`) → `finish_pcb.py` (uvoz SES, GND površine, šivenje) → DRC
- `jlc.py` – Gerber zip, `BOM_JLC.csv`, `CPL_JLC.csv`; `render.py` – PNG pregled vodova; `export_3d.py` – VRML za 3D
- Šeme: schemdraw skripte (`hardware/schematic/*.py`) → SVG/PNG
- Skripte su pisane za **KiCad 7** (`pcbnew` SWIG, `python3.12`, `pcbnew.WriteDRCReport`). Na KiCad 9/10 SWIG API je
  zastareo/izmenjen: proveri `import pcbnew` i po potrebi prebaci na `kicad-cli pcb drc`, `kicad-cli pcb export glb/step`,
  `kicad-cli pcb render` (3D slike) ili IPC API (`kicad-python`).
- avr-gcc 7.3 nema ATtiny1616 u avr-libc: koristi `loopnet/child/firmware/vendor/` + `crt0.S` (`-nostartfiles -nodevicelib`),
  ili na svom računaru Microchip ATtiny DFP / avr-gcc 12+.

## Pravila

- Nije protivpožarni sistem; ništa nije sertifikovano (EN 54). Apollo stvari su samo za laboratoriju.
- Pinove svih IC proveriti po datasheet-u pre rutiranja; neprovereno jasno označiti.
- LCSC brojeve označavati: potvrđeno / samo iz pretrage / nepotvrđeno. Preferirati JLC Basic delove.
