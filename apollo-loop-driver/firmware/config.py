# Apollo XP95 laboratorijski drajver - podesavanja
#
# Sva vremena su u mikrosekundama. Vrednosti oznacene sa "?" nisu poznate iz
# javnih izvora: izmeri ih na pravoj centrali (rezim sniff) pa ih upisi ovde.

# --- Pinovi (Raspberry Pi Pico) ---
PIN_NIVO = 2      # 1 = osnovni nivo 24 V, 0 = impuls 31 V (Q2 na listu 2)
PIN_EN_N = 3      # 0 = petlja ukljucena, 1 = ugasena (R18 je pull-up)
PIN_BIT = 4       # izlaz komparatora: 1 = strujni impuls uredjaja
PIN_PRAG = 16     # PWM prag komparatora (RC filter R20/C9)
PIN_OC_RST = 5    # 1 = brise/blokira hardversku zastitu (Q7), 0 = zastita aktivna
PIN_OC_FLAG = 6   # 1 = hardverska zastita je okinula (> ~500 mA), petlja je ugasena (Q6)
ADC_IAMP = 0      # GP26: struja petlje (1 ohm x 6,1)
ADC_VLOOP = 1     # GP27: napon izlaza petlje (/11)
ADC_VRET = 2      # GP28: napon na povratku petlje (/11)

# --- Analogni lanac ---
VREF = 3.3
DIV_V = 11.0             # delitelji R10/R11 i R12/R13: 100k / 10k
SHUNT_OHM = 1.0
IAMP_GAIN = 5.02           # 1 + 40k2/10k; 500 mA -> 2,51 V
PRAG_IZNAD_MA = 10.0     # prag komparatora = struja mirovanja + 10 mA

# --- Zastita ---
V_MIN_PETLJE = 18.0      # ispod ovoga (duze od V_MIN_MS) petlja se gasi
V_MIN_MS = 2
I_MAX_MA = 500.0         # hardverski prag (U12, R33/R34 = 2,48 V) i softverska provera
OC_BLANK_MS = 20         # posle ukljucenja: punjenje kapaciteta petlje, zastita blokirana
PREKID_ODNOS = 0.5       # povratak petlje ispod 50 % izlaza = prekid linije

# --- Apollo okvir ---
# Izvor: dokument "APOLLO_PROTOCOL_DOCUMENTATION" (opis Linux drajvera mod_apollo, Google Docs korisnika),
# prepisano u ../docs/apollo_protokol_izvor.md. NIJE IZMERENO na pravoj centrali - proveriti sniff-om/osciloskopom.
# Ranije vrednosti (patent US8428153: reset 1500+800, bit 300/700 + 200, takt 300+500) su zamenjene ovim.
#
# Dokument opisuje stanje izlaznog pina centrale (HIGH/LOW), ne napon petlje.
# Pretpostavka: HIGH = impuls 31 V (NIVO = 0), LOW = osnovni nivo 24 V (NIVO = 1); idle izmedju okvira = LOW.
# Ako sniff pokaze obrnuto, postavi HIGH_JE_IMPULS = False.
HIGH_JE_IMPULS = True

T_INIT = 1650            # TI: pocetni HIGH impuls okvira
T_MARKER = 300           # TP: HIGH impuls kojim se zavrsava svaki bit (i predajni i prijemni)
T_NULA = 200             # T0 - TP: LOW pre markera za logicku 0 (bit ukupno 500 us)
T_JEDAN = 850            # T1 - TP: LOW pre markera za logicku 1 (bit ukupno 1150 us)
MSB_PRVI = True          # ? redosled bitova u polju (dokument ne kaze; primer 0x47 = 1000111 sugerise MSB prvi)

N_ODGOVOR = 21           # bitova odgovora uredjaja
T_CITANJE = 1400         # TD + TC + TA: LOW deo prijemnog bita (bit ukupno 1700 us sa markerom)
ODGOVOR_POCETAK = 350    # TD: od pocetka LOW (kraj prethodnog markera) do pocetka prozora odgovora
ODGOVOR_PROZOR = 250     # TC: duzina prozora; centrala u dokumentu uzorkuje sredinu (TD + TC/2 = 475 us)

T_IZMEDJU_PROZIVANJA = 5000   # LOW posle okvira (dokument: TE = 1650 definisan, ali se u kodu ne koristi)

# --- Raspored polja u 21-bitnom odgovoru (isti dokument) ---
POLJA_ODGOVORA = (("interrupt", 1), ("analog", 7), ("ulazi", 3), ("tip", 3), ("adresa", 7))
