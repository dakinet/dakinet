/* Pristup polju ln_t iz Python-a (ctypes), bez preslikavanja strukture. */
#include "../ln_proto.h"
#define SETGET(f) void set_##f(int v){ ln.f = (uint8_t)v; } int get_##f(void){ return ln.f; }
SETGET(addr) SETGET(input) SETGET(event) SETGET(changes) SETGET(low_voltage) SETGET(assign_armed)
SETGET(vline) SETGET(type) SETGET(fw) SETGET(new_addr) SETGET(led_cmd) SETGET(acked) SETGET(st)
int get_sink_on(void){ return ln.sink_on; }
int get_sink_off(void){ return ln.sink_off; }
int get_frames_ok(void){ return ln.frames_ok; }
int get_frames_err(void){ return ln.frames_err; }
