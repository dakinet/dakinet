/* LoopNet – dekoder okvira, vidi ln_proto.h i PROTOCOL.md v0.2 §2–§5. */
#include "ln_proto.h"

ln_t ln;

enum { S_IDLE = 0, S_START, S_HDR, S_W0, S_WIN };

void ln_init(uint8_t addr)
{
    uint8_t *p = (uint8_t *)&ln;
    for (uint16_t i = 0; i < sizeof ln; i++)
        p[i] = 0;
    ln.addr = addr;
    ln.st = S_IDLE;
}

uint8_t ln_has_param(uint8_t cmd)
{
    return cmd == LN_DODELI || cmd == LN_LED;
}

uint8_t ln_crc8(const uint8_t *p, uint8_t n)
{
    uint8_t c = 0;
    while (n--) {
        c ^= *p++;
        for (uint8_t i = 0; i < 8; i++)
            c = (c & 0x80) ? (uint8_t)((c << 1) ^ 0x07) : (uint8_t)(c << 1);
    }
    return c;
}

static uint8_t parity(uint16_t v)
{
    uint8_t p = 0;
    while (v) {
        p ^= v & 1;
        v >>= 1;
    }
    return p;
}

uint16_t ln_status_word(void)
{
    uint16_t s = (uint16_t)(ln.input & 3)
               | (uint16_t)((ln.event ? 1 : 0) << 2)
               | (uint16_t)((ln.low_voltage ? 1 : 0) << 3)
               | (uint16_t)((ln.changes & 0x0F) << 4)
               | (uint16_t)((uint16_t)(ln.addr & 0x7F) << 8);
    return s | (uint16_t)(parity(s) << 15);
}

static uint8_t fail(void)
{
    ln.st = S_IDLE;
    ln.frames_err++;
    return LN_FRAME_ERR | LN_ARM_START;
}

static void respond(uint8_t first, uint8_t len, uint32_t bits)
{
    ln.r_first = first;
    ln.r_len = len;
    ln.r_bits = bits;
}

/* Zaglavlje (i parametar) primljeni: odluci sta uredjaj radi u prozorima.
 * Vraca 1 ako uredjaj ucestvuje u prozorima ovog okvira. */
static uint8_t execute(void)
{
    uint8_t me = ln.addr;
    uint8_t mine = (ln.a == me) && me >= 1 && me <= 126;
    uint8_t bcast = (ln.a == 0);
    ln.r_len = 0;

    switch (ln.cmd) {
    case LN_SKEN:
        if (!bcast) return 0;
        ln.k_total = 254;
        respond((uint8_t)(ln.input != 0 ? 2 * me - 1 : 2 * me), 1, 1);   /* aktivan = zatvoren ili greska */
        return 1;
    case LN_DOGADJAJI:
        if (!bcast) return 0;
        ln.k_total = 254;
        respond((uint8_t)(ln.event ? 2 * me - 1 : 2 * me), 1, 1);
        return 1;
    case LN_STATUS:
        if (!mine) return 0;
        ln.k_total = 16;
        respond(1, 16, ln_status_word());
        return 1;
    case LN_POTVRDI:
        if (!(mine || bcast)) return 0;
        ln.event = 0;
        ln.acked = 1;
        if (bcast) { ln.k_total = 0; return 0; }
        ln.k_total = 1;
        respond(1, 1, 1);
        return 1;
    case LN_INFO: {
        if (!mine) return 0;
        uint8_t b[4] = { ln.type, ln.fw, ln.vline, 0 };
        b[3] = ln_crc8(b, 3);
        ln.k_total = 32;
        respond(1, 32, (uint32_t)b[0] | ((uint32_t)b[1] << 8) | ((uint32_t)b[2] << 16) | ((uint32_t)b[3] << 24));
        return 1;
    }
    case LN_DODELI:
        if (!bcast || !ln.assign_armed || ln.param < 1 || ln.param > 126) return 0;
        ln.new_addr = ln.param;
        ln.k_total = 1;
        respond(1, 1, 1);
        return 1;
    case LN_LED:
        if (!(mine || bcast)) return 0;
        ln.led_cmd = (uint8_t)(0x80 | ln.param);
        if (bcast) { ln.k_total = 0; return 0; }
        ln.k_total = 1;
        respond(1, 1, 1);
        return 1;
    default:
        return 0;
    }
}

uint8_t ln_rise(uint16_t t)
{
    uint16_t per = (uint16_t)(t - ln.t_last);
    ln.t_last = t;

    switch (ln.st) {
    case S_IDLE:
        return LN_ARM_START;

    case S_START:                        /* ivica posle START impulsa = prvi simbol zaglavlja */
        if (per < LN_START_PER_MIN || per > LN_START_PER_MAX)
            return fail();
        ln.st = S_HDR;
        ln.nbits = 0;
        ln.hdr = 0;
        return LN_ARM_START;

    case S_HDR: {
        uint8_t bit;
        if (per >= LN_BIT0_MIN && per <= LN_BIT0_MAX) bit = 0;
        else if (per >= LN_BIT1_MIN && per <= LN_BIT1_MAX) bit = 1;
        else return fail();
        ln.hdr = (uint16_t)((ln.hdr << 1) | bit);
        ln.nbits++;
        if (ln.nbits == 11) {
            if (parity(ln.hdr)) return fail();
            ln.cmd = (uint8_t)(ln.hdr >> 8);
            ln.a = (uint8_t)((ln.hdr >> 1) & 0x7F);
            ln.param = 0;
            if (ln_has_param(ln.cmd)) { ln.hdr = 0; return LN_ARM_START; }
        } else if (ln.nbits == 20) {
            if (parity(ln.hdr & 0x1FF)) return fail();
            ln.param = (uint8_t)((ln.hdr >> 1) & 0xFF);
        } else {
            return LN_ARM_START;
        }
        /* zaglavlje (+ parametar) kompletno; ova ivica je pocetak prozora 0 */
        ln.frames_ok++;
        if (!execute()) {
            ln.st = S_IDLE;
            return LN_FRAME_DONE | LN_ARM_START;
        }
        ln.st = S_W0;
        return LN_ARM_START;
    }

    case S_W0:                           /* ivica prozora 1: period W0 -> W1 = T_W */
        if (per < LN_TW_MIN || per > LN_TW_MAX)
            return fail();
        ln.tw = per;
        ln.win = 1;
        break;

    case S_WIN: {
        uint16_t d = ln.tw >> 3;         /* period prozora mora biti T_W ±12,5 % */
        if (per < ln.tw - d || per > ln.tw + d)
            return fail();
        ln.win++;
        break;
    }
    default:
        return fail();
    }

    /* u prozoru ln.win (S_W0 ili S_WIN) */
    ln.st = S_WIN;
    uint8_t r = LN_ARM_START;
    uint8_t k = (uint8_t)(ln.win - ln.r_first);
    if (ln.win >= ln.r_first && k < ln.r_len && ((ln.r_bits >> k) & 1)) {
        ln.sink_on = (uint16_t)((uint32_t)ln.tw * 3 / 10);
        ln.sink_off = (uint16_t)((uint32_t)ln.tw * 19 / 20);
        r |= LN_SINK;
    }
    if (ln.win >= ln.r_first + ln.r_len - 1 || ln.win >= ln.k_total) {
        ln.st = S_IDLE;                  /* ostatak okvira uredjaja ne zanima */
        r |= LN_FRAME_DONE;
    }
    return r;
}

void ln_long_high(void)
{
    ln.st = S_START;                     /* t_last je uzlazna ivica START impulsa */
}
