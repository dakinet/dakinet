/* Minimalni startni kod za ATtiny1616 (avrxmega3, 16 KB -> vektori od 2 reci, JMP).
   Potreban jer avr-libc 2.0 iz Ubuntu-a nema crtattiny1616.o. Gradi se sa -nostartfiles.
   26 vektora (0 = reset, 1..25 periferije, vidi vendor/avr/iotn1616.h). */

#include <avr/io.h>

    .section .vectors, "ax", @progbits
    .global __vectors
__vectors:
    jmp __init
    .irp n, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25
    .weak __vector_\n
    .set __vector_\n, __bad_interrupt
    jmp __vector_\n
    .endr

    .section .init0, "ax", @progbits
    .weak __init
__init:

    .section .init2, "ax", @progbits
    clr r1
    out 0x3F, r1            ; SREG = 0
    ldi r28, lo8(RAMEND)
    ldi r29, hi8(RAMEND)
    out 0x3D, r28           ; SPL
    out 0x3E, r29           ; SPH

    /* .init4: __do_copy_data / __do_clear_bss dolaze iz libgcc */

    .section .init9, "ax", @progbits
    call main
    jmp exit

    .text
    .global __bad_interrupt
__bad_interrupt:
    jmp __vectors

    .global exit
exit:
    cli
1:  rjmp 1b
