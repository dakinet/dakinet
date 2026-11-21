# Apollo XP95 laboratorijski drajver - podesavanja
#
# Sva vremena su u mikrosekundama. Vrednosti oznacene sa "?" nisu poznate iz
# javnih izvora: izmeri ih na pravoj centrali (rezim sniff) pa ih upisi ovde.

# --- Pinovi (Raspberry Pi Pico) ---
PIN_NIVO = 2      # 1 = osnovni nivo 24 V, 0 = impuls 31 V (Q2 na listu 2)
PIN_EN_N = 3      # 0 = petlja ukljucena, 1 = ugasena (R18 je pull-up)
PIN_BIT = 4       # izlaz komparatora: 1 = strujni impuls uredjaja
PIN_PRAG = 16     # PWM prag komparatora (RC filter R20/C9)
ADC_IAMP = 0      # GP26: struja petlje (1 ohm x 6,1)
ADC_VLOOP = 1     # GP27: napon izlaza petlje (/11)
ADC_VRET = 2      # GP28: napon na povratku petlje (/11)

# --- Analogni lanac ---
VREF = 3.3
DIV_V = 11.0             # delitelji R10/R11 i R12/R13: 100k / 10k
SHUNT_OHM = 1.0
IAMP_GAIN = 6.1            # 1 + 51k/10k
PRAG_IZNAD_MA = 10.0     # prag komparatora = struja mirovanja + 10 mA

# --- Zastita ---
V_MIN_PETLJE = 18.0      # ispod ovoga (duze od V_MIN_MS) petlja se gasi
V_MIN_MS = 2
I_MAX_MA = 500.0         # iznad ovoga u mirovanju petlja se gasi

# --- XP95 okvir (patent US8428153) ---
T_RESET = 1500           # reset impuls
T_RESET_PAUZA = 800      # pauza posle reseta
T_BIT_PAUZA = 200        # pauza izmedju bitova komande/adrese
T_JEDAN = 700            # ? sirina impulsa za logicku 1
T_NULA = 300             # ? sirina impulsa za logicku 0
MSB_PRVI = True          # ? redosled bitova u polju

N_SYNC = 21
T_SYNC = 300             # ? sirina taktnog impulsa
T_SYNC_PAUZA = 500       # ? pauza posle taktnog impulsa (u njoj uredjaj odgovara)
ODGOVOR_KASNJENJE = 50   # ? od kraja taktnog impulsa do pocetka prozora
ODGOVOR_PROZOR = 350     # ? duzina prozora u kome se trazi strujni impuls

T_IZMEDJU_PROZIVANJA = 5000

# --- Raspored polja u 21-bitnom odgovoru (patent) ---
POLJA_ODGOVORA = (("analog", 7), ("ulazi", 2), ("tip", 5), ("adresa", 7))
