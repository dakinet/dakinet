/* LoopNet – dekoder okvira (PROTOCOL.md v0.2), nezavisan od hardvera.
 *
 * Hardverski sloj (main.c) poziva:
 *   ln_rise(t)       na svakoj uzlaznoj ivici linije; t = vremenska oznaka u tikovima (16 bita, sme da se prelije)
 *   ln_long_high()   kad je linija i dalje na 31 V 300 µs posle poslednje uzlazne ivice (START)
 * ln_rise vraca LN_SINK kad uredjaj treba da ukljuci ponor u prozoru koji pocinje ovom ivicom;
 * tada su u ln.sink_on / ln.sink_off pomaci (tikovi od t) za ukljucenje i iskljucenje.
 *
 * Isti kod se prevodi i za racunar (test/test_decode.py preko ctypes).
 */
#ifndef LN_PROTO_H
#define LN_PROTO_H
#include <stdint.h>

#ifndef LN_TICKS_PER_US
#define LN_TICKS_PER_US 5u          /* TCB0 na CLK_PER/2 = 5 MHz */
#endif
#define LN_US(x) ((uint16_t)((x) * LN_TICKS_PER_US))

/* vremena iz PROTOCOL.md §2 */
#define LN_START_PER_MIN  LN_US(550)
#define LN_START_PER_MAX  LN_US(900)
#define LN_BIT0_MIN       LN_US(100)
#define LN_BIT0_MAX       LN_US(195)
#define LN_BIT1_MIN       LN_US(205)
#define LN_BIT1_MAX       LN_US(330)
#define LN_TW_MIN         LN_US(130)
#define LN_TW_MAX         LN_US(450)

enum { LN_SKEN = 0, LN_DOGADJAJI, LN_STATUS, LN_POTVRDI, LN_INFO, LN_DODELI, LN_LED, LN_KONFIG };

/* povratne vrednosti ln_rise (bitovi) */
#define LN_SINK        0x01   /* ukljuci ponor u ovom prozoru */
#define LN_ARM_START   0x02   /* proveri liniju za 300 µs (moguci START) */
#define LN_FRAME_DONE  0x04   /* okvir zavrsen ispravno */
#define LN_FRAME_ERR   0x08   /* okvir odbacen */

#define LN_ADDR_NONE   127

typedef struct {
    /* ---- ulaz u dekoder (puni main.c) */
    uint8_t addr;           /* 1..126, 127 = nedodeljena */
    uint8_t input;          /* 0 otvoren, 1 zatvoren, 2 kratak spoj, 3 prekid */
    uint8_t event;          /* zapamcen dogadjaj */
    uint8_t changes;        /* brojac promena (mod 16) */
    uint8_t low_voltage;
    uint8_t assign_armed;   /* taster drzan 3 s, mod dodele aktivan */
    uint8_t vline;          /* napon na uredjaju, x0,2 V */
    uint8_t type, fw;
    /* ---- izlaz iz dekodera (cita main.c, brise ga) */
    uint8_t new_addr;       /* != 0: DODELI ADRESU prihvacena */
    uint8_t led_cmd;        /* 0x80 | parametar LED komande */
    uint8_t acked;          /* POTVRDI primljena (dogadjaj vec obrisan) */
    uint16_t sink_on, sink_off;
    /* ---- interno stanje */
    uint8_t st, nbits, cmd, a, param;
    uint16_t hdr;
    uint16_t t_last;
    uint16_t tw;
    uint8_t win, k_total;
    uint8_t r_first, r_len;
    uint32_t r_bits;
    uint16_t frames_ok, frames_err;
} ln_t;

extern ln_t ln;

void ln_init(uint8_t addr);
uint8_t ln_rise(uint16_t t);
void ln_long_high(void);
uint16_t ln_status_word(void);
uint8_t ln_crc8(const uint8_t *p, uint8_t n);
uint8_t ln_has_param(uint8_t cmd);

#endif
