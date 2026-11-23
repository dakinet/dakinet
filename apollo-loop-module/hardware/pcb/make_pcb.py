"""Pravi KiCad 7 pločicu za Apollo loop driver MODUL v0.1 (70 x 50 mm, 2 sloja) – samo laboratorija.

Kompaktna verzija apollo-loop-driver mastera za ugradnju: 24 V ulaz, boost 34 V (TPS55340), linearni
push-pull izlaz 24,2 / 31,2 V do 250 mA (OPA197 + MJD122 + MMBT5401 za aktivno spuštanje), merenje struje
(šant 1 Ω, MCP6002 x5,02), hardverska zaštita sa zadrškom (MCP6561), MCU AVR64DD28 sa kristalom 16 MHz:
interni komparator AC0 + DACREF prima odgovor uređaja (umesto spoljnog MCP6561), ADC meri IAMP/VLOOP/VRET,
USART0 ka matičnoj ploči, USART1 za dijagnostiku, UPDI + RESET na letvici (ažuriranje firmvera sa matične ploče).
TVS SMBJ28A na ulazu (TPS55340 VIN/EN apsolutni max 34 V).

Pokretanje:  python3.12 make_pcb.py   (KiCad 7 pcbnew)  -> apollo_module.kicad_pcb, apollo_module.dsn
Raspored pinova proveren po datasheet-ovima (vidi ../../README.md):
  TPS55340PWP (HTSSOP-14): 1,2 SW; 3 VIN; 4 EN; 5 SS; 6 SYNC; 7 AGND; 8 COMP; 9 FB; 10 FREQ; 11 NC; 12-14 PGND; PowerPAD
  TPS560430X3F (SOT-23-6): 1 CB; 2 GND; 3 FB (=VOUT kod fiksne 3,3 V); 4 EN; 5 VIN; 6 SW
  MJD122 (DPAK): 1 B, 2/tab C, 3 E;  MMBT5401 / MMBT3904 / 2N7002 (SOT-23): 1 B/G, 2 E/S, 3 C/D
  OPA197, MCP6002, MCP6561: isti raspored kao u apollo-loop-driver (proveren tamo)
  AVR64DD28 (SOIC-28): DS40002315A (prelim.), slika 2-1 i tabela 3-1 - proveren 23.11.2026, vidi komentar kod U7
"""
import os
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew

# KiCad 7 na Linuxu ili KiCad 9/10 na Windows-u (KICAD_FOOTPRINTS menja putanju)
FP = os.environ.get('KICAD_FOOTPRINTS') or next(
    (d for d in ('/usr/share/kicad/footprints/', r'C:/Program Files/KiCad/10.0/share/kicad/footprints/')
     if os.path.isdir(d)), '/usr/share/kicad/footprints/')
MM = pcbnew.FromMM
IME = 'apollo_module'

R0603 = ('Resistor_SMD', 'R_0603_1608Metric')
R0805 = ('Resistor_SMD', 'R_0805_2012Metric')
R2512 = ('Resistor_SMD', 'R_2512_6332Metric')
C0603 = ('Capacitor_SMD', 'C_0603_1608Metric')
C0402 = ('Capacitor_SMD', 'C_0402_1005Metric')   # blokada RP2040 (Hardware design with RP2040)
C0805 = ('Capacitor_SMD', 'C_0805_2012Metric')
C1210 = ('Capacitor_SMD', 'C_1210_3225Metric')
SOT23 = ('Package_TO_SOT_SMD', 'SOT-23')
SOT235 = ('Package_TO_SOT_SMD', 'SOT-23-5')
SOIC8 = ('Package_SO', 'SOIC-8_3.9x4.9mm_P1.27mm')
DSMA = ('Diode_SMD', 'D_SMA')
# KiCad 7 i KiCad 9/10 imaju različita imena ova dva footprinta (TI PWP0014A; varijanta maske NEPROVERENA za TPS55340)
_PSO = os.path.join(FP, 'Package_SO.pretty')
# bez bibliotečkih termalnih via (0,2 mm rupe – JLC 2 sloja traži >= 0,3 mm); 6 via 0,3/0,6 mm u PowerPAD-u su u PREVODI
HTSSOP14 = ('Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3.155x3.255mm'
            if os.path.exists(os.path.join(_PSO, 'Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3.155x3.255mm.kicad_mod'))
            else 'HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3x3.1mm')
SOIC8W = ('SOIC-8_5.3x5.3mm_P1.27mm' if os.path.exists(os.path.join(_PSO, 'SOIC-8_5.3x5.3mm_P1.27mm.kicad_mod'))
          else 'SOIC-8_5.23x5.23mm_P1.27mm')
TB2 = ('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal')

# ref: (biblioteka, vrednost, {pin: mreža})
P = {
    # ---- ulaz 24 V
    'F1': (('Fuse', 'Fuse_1206_3216Metric'), '3A', {'1': '+24V_IN', '2': 'VIN_F'}),
    'D1': (DSMA, 'SS34', {'2': 'VIN_F', '1': 'VIN'}),
    'D6': (('Diode_SMD', 'D_SMB'), 'SMBJ28A', {'1': 'VIN_F', '2': 'GND'}),   # TVS: K na VIN_F, A na GND
    'C1': (('Capacitor_SMD', 'CP_Elec_6.3x7.7'), '47u/50V', {'1': 'VIN', '2': 'GND'}),
    'C2': (C1210, '10u/50V', {'1': 'VIN', '2': 'GND'}),
    # ---- boost 34 V (TPS55340, ~580 kHz)
    'U1': (('Package_SO', HTSSOP14), 'TPS55340PWPR',
           {'1': 'SW', '2': 'SW', '3': 'VIN', '4': 'VIN', '5': 'SS', '6': 'GND', '7': 'GND', '8': 'COMP',
            '9': 'BFB', '10': 'FREQ', '11': 'GND', '12': 'GND', '13': 'GND', '14': 'GND', '15': 'GND'}),
    'L1': (('Inductor_SMD', 'L_Bourns_SRN6045TA'), '33uH SRN6045TA-330M', {'1': 'VIN', '2': 'SW'}),
    'D2': (DSMA, 'SS210', {'2': 'SW', '1': '+34V'}),
    'C3': (C1210, '10u/50V', {'1': '+34V', '2': 'GND'}),
    'C4': (C1210, '10u/50V', {'1': '+34V', '2': 'GND'}),
    'C5': (('Capacitor_SMD', 'CP_Elec_8x10'), '100u/50V', {'1': '+34V', '2': 'GND'}),
    'R1': (R0603, '270k', {'1': '+34V', '2': 'BFB'}),
    'R2': (R0603, '10k', {'1': 'BFB', '2': 'GND'}),
    'R3': (R0603, '82k', {'1': 'FREQ', '2': 'GND'}),
    'R4': (R0603, '2k2', {'1': 'COMP', '2': 'CC'}),
    'C6': (C0603, '100n', {'1': 'CC', '2': 'GND'}),
    'C7': (C0603, '100p', {'1': 'COMP', '2': 'GND'}),
    'C8': (C0603, '47n', {'1': 'SS', '2': 'GND'}),
    'C9': (C0603, '1u/50V', {'1': 'VIN', '2': 'GND'}),
    'C35': (C0603, '100n/50V', {'1': 'VIN', '2': 'GND'}),     # VF bypass uz VIN pin (TI layout primer)
    'C36': (C0603, '100n/50V', {'1': '+34V', '2': 'GND'}),    # VF kondenzator izlazne petlje D2 -> PGND
    # ---- 3,3 V buck (TPS560430X3F, fiksnih 3,3 V)
    'U2': (('Package_TO_SOT_SMD', 'SOT-23-6'), 'TPS560430X3FDBVR',
           {'1': 'CB', '2': 'GND', '3': '+3V3', '4': 'VIN', '5': 'VIN', '6': 'SW3'}),
    'C10': (C0603, '100n', {'1': 'CB', '2': 'SW3'}),
    'L2': (('Inductor_SMD', 'L_Bourns-SRN4018'), '15uH SRN4018-150M', {'1': 'SW3', '2': '+3V3'}),
    'C11': (C1210, '10u/50V', {'1': 'VIN', '2': 'GND'}),
    'C37': (C0603, '100n/50V', {'1': 'VIN', '2': 'GND'}),     # CIN VF direktno između VIN (5) i GND (2)
    'C12': (C0805, '22u/10V', {'1': '+3V3', '2': 'GND'}),     # TI tabela 1: COUT 22 uF za 3,3 V / 1,1 MHz
    'C13': (C0805, '10u', {'1': '+3V3', '2': 'GND'}),
    # ---- VSET: 3,3 V x 15k/16k = 3,094 V (impuls) ili x (15k||3k24)/... = 2,40 V (osnovni), Q3 gasi petlju
    'R5': (R0603, '1k', {'1': '+3V3', '2': 'VSET'}),
    'R6': (R0603, '15k', {'1': 'VSET', '2': 'GND'}),
    'C14': (C0603, '10n', {'1': 'VSET', '2': 'GND'}),
    'R7': (R0603, '3k24', {'1': 'VSET', '2': 'Q2D'}),
    'Q2': (SOT23, '2N7002', {'1': 'NIVO_G', '2': 'GND', '3': 'Q2D'}),
    'R8': (R0603, '100', {'1': 'NIVO', '2': 'NIVO_G'}),
    'Q3': (SOT23, '2N7002', {'1': 'EN_N', '2': 'GND', '3': 'VSET'}),
    'R9': (R0603, '100k', {'1': 'EN_N', '2': '+3V3'}),
    # ---- izlazni stepen: OPA197 (x10,1) + Darlington MJD122 (izvor) + MMBT5401 (ponor za silaznu ivicu)
    'U3': (SOIC8, 'OPA197', {'2': 'FB', '3': 'VSET', '4': 'GND', '6': 'U3OUT', '7': '+34V'}),
    'C15': (C0603, '100n/50V', {'1': '+34V', '2': 'GND'}),
    'R10': (R0603, '470', {'1': 'U3OUT', '2': 'NB'}),
    'R11': (R0805, '91k', {'1': 'LOOP_DRV', '2': 'FB'}),
    'C16': (C0603, '100p', {'1': 'LOOP_DRV', '2': 'FB'}),
    'R12': (R0603, '10k', {'1': 'FB', '2': 'GND'}),
    'Q1': (('Package_TO_SOT_SMD', 'TO-252-2'), 'MJD122', {'1': 'NB', '2': '+34V', '3': 'NE'}),
    'R13': (R2512, '2R0 1W', {'1': 'NE', '2': 'LOOP_DRV'}),
    'Q4': (SOT23, 'MMBT3904', {'1': 'NE', '2': 'LOOP_DRV', '3': 'NB'}),
    'Q5': (SOT23, 'MMBT5401', {'1': 'NB', '2': 'PE', '3': 'GND'}),
    'R14': (R0603, '10', {'1': 'PE', '2': 'LOOP_DRV'}),
    # ---- izlaz i zaštita
    'F2': (('Fuse', 'Fuse_2920_7451Metric'), 'PTC 750mA/60V', {'1': 'LOOP_DRV', '2': 'LOOP_OUT'}),
    'D3': (('Diode_SMD', 'D_SMB'), 'SMBJ36A', {'1': 'LOOP_OUT', '2': 'GND'}),
    'R15': (R0603, '100k', {'1': 'LOOP_OUT', '2': 'VLOOP'}),
    'R16': (R0603, '10k', {'1': 'VLOOP', '2': 'GND'}),
    'C17': (C0603, '1n', {'1': 'VLOOP', '2': 'GND'}),
    'R17': (R0603, '100k', {'1': 'LOOP_IN', '2': 'VRET'}),
    'R18': (R0603, '10k', {'1': 'VRET', '2': 'GND'}),
    'C18': (C0603, '1n', {'1': 'VRET', '2': 'GND'}),
    # ---- merenje struje
    'R19': (R2512, '1R 1W', {'1': 'ISENSE', '2': 'GND'}),
    'R20': (R0603, '1k', {'1': 'ISENSE', '2': 'NA'}),
    'C19': (C0603, '1n', {'1': 'NA', '2': 'GND'}),
    'U4': (SOIC8, 'MCP6002', {'1': 'IAMP', '2': 'NM', '3': 'NA', '4': 'GND', '5': 'GND', '6': 'U4B', '7': 'U4B', '8': '+3V3'}),
    'C20': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'R21': (R0603, '10k', {'1': 'NM', '2': 'GND'}),
    'R22': (R0603, '40k2', {'1': 'NM', '2': 'IAMP'}),
    # ---- zaštita od preopterećenja > ~285 mA sa zadrškom (kao kod mastera, prag 1,43 V)
    'U6': (SOT235, 'MCP6561T-E/OT', {'1': 'OCP', '2': 'GND', '3': 'OC_IN', '4': 'OC_REF', '5': '+3V3'}),
    'C23': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'R24': (R0603, '13k', {'1': '+3V3', '2': 'OC_REF'}),
    'R25': (R0603, '10k', {'1': 'OC_REF', '2': 'GND'}),
    'R26': (R0603, '10k', {'1': 'IAMP', '2': 'OC_IN'}),
    'C24': (C0603, '1n', {'1': 'OC_IN', '2': 'GND'}),
    'D4': (('Diode_SMD', 'D_SOD-323'), 'BAT54J', {'2': 'OCP', '1': 'OC_FB'}),
    'R27': (R0603, '1k', {'1': 'OC_FB', '2': 'OC_IN'}),
    'Q6': (SOT23, '2N7002', {'1': 'OCP', '2': 'GND', '3': 'VSET'}),
    'Q7': (SOT23, '2N7002', {'1': 'OC_RST', '2': 'GND', '3': 'OC_IN'}),
    'R28': (R0603, '100k', {'1': 'OC_RST', '2': 'GND'}),
    # ---- MCU AVR64DD28-I/SS (SSOP-28, isti raspored pinova kao SOIC-28), kristal 16 MHz. Pinovi po DS40002315A (prelim.), slika 2-1 + tabela 3-1:
    #  1 PA7 LED (alt: AC0 OUT za osciloskop) | 2 PC0 DBG_TX, 3 PC1 DBG_RX (USART1 default) | 6 VDDIO2 = 3V3
    #  7 PD1 OCP (ulaz) | 8 PD2 IAMP = AC0 AINP0 (prag DACREF) i ADC AIN2 | 10 PD4 VLOOP AIN4 | 11 PD5 VRET AIN5
    #  14, 20 VDD | 15, 21 GND | 18 PF6 RESET | 19 PF7 UPDI | 22/23 PA0/PA1 XTALHF1/2
    #  24 PA2 NIVO (TCA0 WO2 / TCB0 WO) | 25 PA3 EN_N | 26/27 PA4/PA5 TX/RX (USART0 ALT1) | 28 PA6 OC_RST
    #  slobodni (NC): 4 PC2, 5 PC3, 9 PD3, 12 PD6 (DAC OUT), 13 PD7 (VREFA), 16 PF0, 17 PF1
    'U7': (('Package_SO', 'SSOP-28_5.3x10.2mm_P0.65mm'), 'AVR64DD28-I/SS',
           {'1': 'LED', '2': 'DBG_TX', '3': 'DBG_RX', '6': '+3V3', '7': 'OCP', '8': 'IAMP', '10': 'VLOOP',
            '11': 'VRET', '14': '+3V3', '15': 'GND', '18': 'RESET', '19': 'UPDI', '20': '+3V3', '21': 'GND',
            '22': 'XIN', '23': 'XO', '24': 'NIVO', '25': 'EN_N', '26': 'TX', '27': 'RX', '28': 'OC_RST'}),
    'C25': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),       # VDD pin 14 (DS sl. 4-1, C1)
    'C28': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),       # VDD pin 20
    'C29': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),       # VDDIO2 pin 6 (DS sl. 4-2)
    'C32': (C0603, '1u', {'1': '+3V3', '2': 'GND'}),         # opcioni C3 iz sl. 4-1
    'Y1': (('Crystal', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'), '16MHz X322516MLB4SI',
           {'1': 'XIN', '2': 'GND', '3': 'XO', '4': 'GND'}),
    'C26': (C0603, '27p', {'1': 'XIN', '2': 'GND'}),         # za CL 20 pF: 2 x (20 - ~5 pF parazitno); proveriti
    'C27': (C0603, '27p', {'1': 'XO', '2': 'GND'}),
    'R29': (R0603, '10k', {'1': 'RESET', '2': '+3V3'}),      # interni pull-up postoji; spoljni zbog voda ka MB
    'C30': (C0603, '10n', {'1': 'RESET', '2': 'GND'}),
    'R35': (R0603, '1k', {'1': 'LED', '2': 'LED_A'}),
    'D5': (('LED_SMD', 'LED_0603_1608Metric'), 'LED', {'1': 'GND', '2': 'LED_A'}),
    # ---- J1: letvica 2x14 / 2,54 mm sa DONJE strane – modul se utiče u matičnu ploču (sve spoljne veze)
    #  pinovi (neparni red / parni red), s leva na desno, prate blokove iznad letvice:
    #  24V x2 (ulaz F1/D1) | GND x2 | 3V3,GND | TX,RX | RESET,UPDI | DBG_TX,DBG_RX | GND,GND |
    #  GND | ISENSE (ispod šanta R19) | LOOP_IN | LOOP_OUT (uz TVS D3) | GND
    'J1': (('Connector_PinHeader_2.54mm', 'PinHeader_2x14_P2.54mm_Vertical'), 'MATICNA 2x14',
           {'1': '+24V_IN', '2': '+24V_IN', '3': '+24V_IN', '4': '+24V_IN', '5': 'GND', '6': 'GND', '7': 'GND', '8': 'GND',
            '9': '+3V3', '10': 'GND', '11': 'TX', '12': 'RX', '13': 'RESET', '14': 'UPDI', '15': 'DBG_TX', '16': 'DBG_RX',
            '17': 'GND', '18': 'GND', '19': 'GND', '20': 'GND', '21': 'ISENSE', '22': 'ISENSE',
            '23': 'LOOP_IN', '24': 'LOOP_IN', '25': 'LOOP_OUT', '26': 'LOOP_OUT', '27': 'GND', '28': 'GND'}),
}

# delovi sa donje strane (B.Cu); ostali su gore
DOLE = {'J1'}

POZ = {
    # ulaz i boost (gore)
    'F1': (110, 141.2, 90), 'D1': (104.5, 141.75, 0), 'C1': (104, 133.5, 90), 'C2': (105.3, 103.35, 90),
    'U1': (109, 110.6, 270), 'L1': (110.5, 103.35, 0), 'D2': (113.6, 110.6, 90), 'C3': (112.1, 117.85, 180), 'C4': (116.8, 117.85, 180),
    'C5': (120.7, 110.2, 0), 'C9': (103.7, 108.3, 270), 'R1': (105.15, 112.7, 270), 'R2': (108.45, 116.35, 270), 'R3': (105.6, 115.6, 180),
    'R4': (102.3, 113.4, 180), 'C6': (102.25, 111.3, 0), 'C7': (102.8, 116.2, 270), 'C8': (101.1, 107.7, 180),
    # buck 3V3 (levo)
    'U2': (104, 124, 0), 'C10': (104, 121.45, 0), 'L2': (108.7, 123.3, 0), 'C11': (104, 129.05, 180), 'C12': (110.1, 118.95, 90),
    'C13': (113.3, 123.25, 0),
    # VSET
    'R5': (130.4, 125.15, 90), 'R6': (125.6, 121.45, 180), 'C14': (129.25, 121.9, 0), 'R7': (128.35, 124.75, 270), 'Q2': (126.7, 128.5, 0),
    'R8': (122.7, 127.55, 0), 'Q3': (125.1, 124.5, 0), 'R9': (121.85, 124.7, 90),
    # izlazni stepen
    'U3': (135.15, 117.4, 0), 'C15': (137, 113.25, 180), 'R10': (143.55, 116.75, 0), 'R11': (143.25, 114.5, 180), 'C16': (143.1, 118.8, 180),
    'R12': (140.25, 114.55, 90), 'Q1': (153.5, 106, 0), 'R13': (152.5, 112.8, 0), 'Q4': (147.5, 116.6, 0), 'Q5': (151.5, 117.1, 90),
    'R14': (156.3, 117.4, 90),
    # petlja
    'F2': (156.3, 125, 270), 'D3': (152, 136, 0), 'R15': (143.8, 129.8, 270), 'R16': (145.95, 132.6, 270), 'C17': (145.85, 129.05, 90),  'R17': (136.75, 142, 0), 'R18': (143.1, 132.6, 0), 'C18': (140.3, 134.8, 90),
    # merenje i zaštita
    'R19': (141, 132.95, 0), 'R20': (137, 129.6, 0), 'C19': (136.55, 128, 90), 'U4': (140.7, 127, 90), 'C20': (135.8, 124.7, 180),
    'R21': (139.25, 121.9, 180), 'R22': (144.8, 126.25, 270), 
    'U6': (125.45, 133.45, 180), 'C23': (122, 133.5, 90), 'R24': (128.4, 136.55, 180), 'R25': (128.45, 130.35, 0),
    'R26': (145.7, 133.25, 0), 'C24': (146.85, 130.45, 90), 'D4': (133.95, 133.5, 90), 'R27': (133.15, 136.5, 180), 'Q6': (133.45, 120.45, 90),
    'Q7': (124.1, 129.4, 0), 'R28': (124.05, 136.55, 0),
    # MCU AVR64DD28 (grubo – raspored u toku)
    
    
    
    
    'C36': (112.1, 115.35, 180),
    'C35': (105.4, 108.3, 270),
    'C37': (104, 126.55, 180),
    
    
    
    
    # letvica 2x14 (donja strana), simetrično na sredini donje ivice: pinovi x 113,49..146,51; neparni red y=140,6
    'J1': (113.49, 139.6, 90),
    # U7 rot 270: pinovi 1-14 gornji red (y 128,35; x 124,25 -> 107,75), 15-28 donji red (y 137,65; x 107,75 -> 124,25)
    'U7': (114, 130, 270),
    'Y1': (115.3, 138.3, 0), 'C26': (112.2, 138.3, 90), 'C27': (118.4, 138.3, 90),   # XIN 22 / XO 23 dole
    'C28': (110.3, 138.3, 90),                                                       # VDD 20 / GND 21
    'R29': (108.4, 138.3, 90), 'C30': (106.5, 138.3, 90),                             # RESET 18
    'R35': (120.5, 138.3, 90), 'D5': (122.5, 138.3, 90),                              # LED (pin 1 gore desno)
    'C25': (102.8, 130.2, 90),                                                       # VDD 14 / GND 15 levo
    'C29': (116.5, 122.2, 0), 'C32': (119.8, 122.2, 0),                              # VDDIO2 6 gore
    'D6': (106, 136, 0),                                                          # TVS uz levu ivicu
}

KLASE = [
    ('boost', ['+24V_IN', 'VIN_F', 'SW'], 800, 300),
    ('vin', ['VIN'], 600, 200),                 # VIN ide i do SOT-23-6 pinova buck-a (korak 0,95 mm)
    ('buck', ['SW3'], 500, 250),
    ('petlja', ['+34V', 'NE', 'LOOP_DRV', 'LOOP_OUT', 'ISENSE', 'LOOP_IN', 'PE'], 600, 300),
    ('hv', ['NB', 'U3OUT'], 300, 300),
    ('logika3v3', ['+3V3'], 250, 150),
]

BLOKOVI = [
    ('1 ULAZ 24V', ['F1', 'D1', 'D6']),
    ('2 BOOST 34V', ['C1', 'C2', 'U1', 'L1', 'D2', 'C3', 'C4', 'C5', 'R1', 'R2', 'R3', 'R4', 'C6', 'C7', 'C8', 'C9', 'C35', 'C36']),
    ('3 BUCK 3V3', ['U2', 'C10', 'L2', 'C11', 'C12', 'C13', 'C37']),
    ('4 VSET', ['R5', 'R6', 'C14', 'R7', 'Q2', 'R8', 'Q3', 'R9']),
    ('5 IZLAZ 24/31V', ['U3', 'C15', 'R10', 'R11', 'C16', 'R12', 'Q1', 'R13', 'Q4', 'Q5', 'R14']),
    ('6 PETLJA', ['F2', 'R15', 'R16', 'C17', 'R17', 'R18', 'C18']),
    ('7 MERENJE I ZASTITA', ['R19', 'R20', 'C19', 'U4', 'C20', 'R21', 'R22',
                             'U6', 'C23', 'R24', 'R25', 'R26', 'C24', 'D4', 'R27', 'Q6', 'Q7', 'R28']),
    ('8 MCU AVR64DD28', ['U7', 'C25', 'C28', 'C29', 'C32', 'Y1', 'C26', 'C27', 'R29', 'C30', 'R35', 'D5']),
    ('9 LETVICA 2x14 (DOLE)', ['J1', 'D3']),
]

# Ručno nacrtani strujni putevi prekidačkih napajanja (TI SLVSBD4E §10, SLVSE22B §11): najkraće i najšire moguće,
# zaključani; Freerouting ih zadržava i rutira samo ostatak.  (mreža, [(sloj, x1, y1, x2, y2, širina)], [via])
PREVODI = [
    ('SW', [('F', 110.3, 107.6, 110.3, 106.2, 0.4),
          ('F', 110.95, 107.6, 110.95, 106.2, 0.4),
          ('F', 110.3, 106.2, 112.6, 106.2, 0.8),
          ('F', 112.6, 106.2, 113.6, 106.2, 1.0),
          ('F', 113.6, 106.2, 113.6, 108, 1.2)],
     []),
    ('VIN', [('F', 106, 104.8, 108, 104.8, 1.0),
          ('F', 109, 107.6, 109, 105.5, 0.4),
          ('F', 109, 107.2, 109.65, 107.2, 0.35),
          ('F', 103.7, 107.5, 105.4, 107.5, 0.6),
          ('F', 105.4, 107.5, 106.3, 106.3, 0.5),
          ('F', 106.3, 106.3, 107.6, 105.6, 0.5),
          ('F', 105.3, 124, 105.3, 126.5, 0.6),
          ('F', 105.3, 126.5, 105.5, 128.5, 0.6)],
     []),
    ('+34V', [('F', 113.6, 113.5, 113.6, 117, 1.2),
          ('F', 114.2, 112, 116.2, 110.6, 1.0),
          ('F', 118.3, 111.2, 118.3, 117, 1.0)],
     []),
    ('GND', [('F', 109, 114, 110.95, 114, 0.35),
          ('F', 110.3, 114, 110.6, 117.8, 0.6),
          ('F', 102.4, 124, 101.4, 124, 0.5),
          ('F', 101.4, 124, 101.4, 128.5, 0.5),
          ('F', 101.4, 126.55, 103.2, 126.55, 0.5),
          ('F', 101.4, 128.5, 102.5, 128.5, 0.5)],
     [(109.4, 115), (110.6, 119.8), (101.4, 125.3), (107.4, 109.8), (109, 109.8), (110.6, 109.8), (107.4, 111.4), (109, 111.4), (110.6, 111.4), (143.96, 130.6), (154.15, 138.4)]),
    ('SW3', [('F', 105.4, 123.05, 107, 123.05, 0.6),
          ('F', 104.8, 121.6, 105.2, 122.9, 0.4)],
     []),
    ('CB', [('F', 103.2, 121.5, 103, 123, 0.4)],
     []),
    ('+24V_IN', [('F', 113.49, 139.6, 113.49, 142.14, 1.0),
          ('F', 113.49, 142.14, 116.03, 142.14, 1.0),
          ('F', 116.03, 139.6, 116.03, 142.14, 1.0),
          ('F', 110, 142.6, 113.49, 142.14, 1.0)],
     []),
    ('VIN_F', [('F', 110, 139.8, 106.6, 141.6, 1.0)],
     []),
    ('NE', [('F', 148.46, 108.28, 149.54, 111.5, 0.8),
          ('F', 146.9, 115.65, 149.3, 114.2, 0.3)],
     []),
    ('LOOP_DRV', [('F', 155.46, 114, 154.95, 114.9, 0.7),
          ('F', 154.95, 114.9, 154.95, 121, 0.7),
          ('F', 154.95, 116.57, 156.1, 116.57, 0.5)],
     []),
    ('LOOP_OUT', [('F', 149.85, 136, 144.4, 136, 0.8),
          ('F', 144.4, 136, 144.4, 139.6, 0.8)],
     []),
    ('ISENSE', [('F', 138.89, 139.6, 138.04, 134, 1.0),
          ('F', 136.2, 129.6, 137.8, 131.6, 0.25)],
     []),
]
X0, Y0, X1, Y1 = 100, 100, 160, 145

# Dobra praksa za prekidačka napajanja: donja GND površina ispod konvertera ostaje neprekinuta
# (povratna struja prekidačke petlje teče odmah ispod nje). Na B.Cu tu nisu dozvoljeni vodovi; via za masu jesu.
MASA_B = [
    ('boost', (103.0, 100.4, 118.5, 119.5)),   # U1, L1, D2, C3/C36, kompenzacija
    ('buck', (101.0, 120.5, 116.0, 131.0)),    # U2, L2, C10, C11, C37, C12/C13
]


def ucitaj(lib, ime):
    fp = pcbnew.FootprintLoad(FP + lib + '.pretty', ime)
    if fp is None:
        raise SystemExit('nema footprinta %s:%s' % (lib, ime))
    return fp


assert set(POZ) == set(P), set(P) ^ set(POZ)


def napravi():
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ns = ds.m_NetSettings
    nc = ns.m_DefaultNetClass if hasattr(ns, 'm_DefaultNetClass') else ns.GetDefaultNetclass()  # KiCad 7 / 9+
    nc.SetClearance(MM(0.15))
    nc.SetTrackWidth(MM(0.2))
    nc.SetViaDiameter(MM(0.6))
    nc.SetViaDrill(MM(0.3))
    ds.m_MinClearance = MM(0.15)
    ds.m_TrackMinWidth = MM(0.15)
    ds.m_CopperEdgeClearance = MM(0.3)       # JLCPCB: bakar do ivice >= 0,3 mm
    nets = {}

    def net(ime):
        if ime not in nets:
            n = pcbnew.NETINFO_ITEM(b, ime)
            b.Add(n)
            nets[ime] = n
        return nets[ime]

    for ref, (li, val, pins) in P.items():
        x, y, rot = POZ[ref]
        fp = ucitaj(*li)
        fp.SetReference(ref)
        fp.SetValue(val)
        b.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        if ref in DOLE:
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        for pad in fp.Pads():
            m = pins.get(pad.GetNumber())
            if m:
                pad.SetNet(net(m))
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        fp.Reference().SetTextThickness(MM(0.1))
        fp.Reference().SetVisible(False)            # premalo mesta: oznake su na F.Fab crtežu
    for a, c in [((X0, Y0), (X1, Y0)), ((X1, Y0), (X1, Y1)), ((X1, Y1), (X0, Y1)), ((X0, Y1), (X0, Y0))]:
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        b.Add(s)
    # natpisi na donjoj strani (gore nema mesta)
    for txt, x, y, sz in [('APOLLO LOOP DRIVER MODUL v0.1 - SAMO LAB', 135, 104, 1.0),
                          ('J1 2x14 (dole): 24V GND 3V3 TX RX RUN BOOT D+ D- SWD GND ISENSE LOOP_IN LOOP_OUT GND', 135, 107, 0.7)]:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(txt)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.B_SilkS)
        t.SetMirrored(True)
        t.SetTextSize(pcbnew.VECTOR2I(MM(sz), MM(sz)))
        t.SetTextThickness(MM(sz * 0.15))
        b.Add(t)
    fpd = {f.GetReference(): f for f in b.GetFootprints()}
    for ime, refs in BLOKOVI:
        xs0, ys0, xs1, ys1 = [], [], [], []
        for r in refs:
            c = fpd[r].GetBoundingBox(False, False)
            xs0.append(pcbnew.ToMM(c.GetLeft())); ys0.append(pcbnew.ToMM(c.GetTop()))
            xs1.append(pcbnew.ToMM(c.GetRight())); ys1.append(pcbnew.ToMM(c.GetBottom()))
        r = pcbnew.PCB_SHAPE(b)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetStart(pcbnew.VECTOR2I(MM(max(min(xs0) - 0.3, X0)), MM(max(min(ys0) - 0.3, Y0))))
        r.SetEnd(pcbnew.VECTOR2I(MM(min(max(xs1) + 0.3, X1)), MM(min(max(ys1) + 0.3, Y1))))
        r.SetLayer(pcbnew.F_Fab)
        r.SetWidth(MM(0.1))
        b.Add(r)
        t = pcbnew.PCB_TEXT(b)
        t.SetText(ime)
        t.SetLayer(pcbnew.F_Fab)
        t.SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        t.SetTextThickness(MM(0.1))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        t.SetPosition(pcbnew.VECTOR2I(MM(max(min(xs0), X0) + 0.2), MM(max(min(ys0), Y0) + 0.5)))
        b.Add(t)
    for ime, segs, vias in PREVODI:
        n = net(ime)
        for lay, x1, y1, x2, y2, w in segs:
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1))); t.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
            t.SetWidth(MM(w)); t.SetLayer(pcbnew.F_Cu if lay == 'F' else pcbnew.B_Cu)
            t.SetNet(n); t.SetLocked(True); b.Add(t)
        for x, y in vias:
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetDrill(MM(0.3)); v.SetWidth(MM(0.6))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(n); v.SetLocked(True); b.Add(v)
    # pojas 0,35 mm uz ivicu bez vodova i via (Freerouting ne poznaje razmak bakra do ivice)
    for (ax, ay, bx, by) in [(X0, Y0, X1, Y0 + 0.35), (X0, Y1 - 0.35, X1, Y1), (X0, Y0, X0 + 0.35, Y1), (X1 - 0.35, Y0, X1, Y1)]:
        kz = pcbnew.ZONE(b)
        kz.SetIsRuleArea(True); kz.SetDoNotAllowTracks(True); kz.SetDoNotAllowVias(True)
        (kz.SetDoNotAllowCopperPour if hasattr(kz, 'SetDoNotAllowCopperPour') else kz.SetDoNotAllowZoneFills)(False); kz.SetDoNotAllowPads(False); kz.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); kz.SetLayerSet(ls)
        o = kz.Outline(); o.NewOutline()
        for x, y in [(ax, ay), (bx, ay), (bx, by), (ax, by)]:
            o.Append(MM(x), MM(y))
        b.Add(kz)
    for ime, (ax, ay, bx, by) in MASA_B:
        kz = pcbnew.ZONE(b)
        kz.SetIsRuleArea(True); kz.SetDoNotAllowTracks(True); kz.SetDoNotAllowVias(False)
        (kz.SetDoNotAllowCopperPour if hasattr(kz, 'SetDoNotAllowCopperPour') else kz.SetDoNotAllowZoneFills)(False)
        kz.SetDoNotAllowPads(False); kz.SetDoNotAllowFootprints(False)
        kz.SetZoneName('masa ispod ' + ime)
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.B_Cu); kz.SetLayerSet(ls)
        o = kz.Outline(); o.NewOutline()
        for x, y in [(ax, ay), (bx, ay), (bx, by), (ax, by)]:
            o.Append(MM(x), MM(y))
        b.Add(kz)
    ds.SetBoardThickness(MM(1.6))
    return b, nets


def kutija(f):
    """Zauzeće na GORNJOJ strani u mm (x0, y0, x1, y1): courtyard; za delove sa donje strane samo THT padovi + 0,25 mm."""
    if f.IsFlipped():
        q = [pd.GetBoundingBox() for pd in f.Pads()]
        m = 0.25
        return (pcbnew.ToMM(min(b.GetLeft() for b in q)) - m, pcbnew.ToMM(min(b.GetTop() for b in q)) - m,
                pcbnew.ToMM(max(b.GetRight() for b in q)) + m, pcbnew.ToMM(max(b.GetBottom() for b in q)) + m)
    c = f.GetCourtyard(pcbnew.F_CrtYd)
    bb = c.BBox() if not c.IsEmpty() else f.GetBoundingBox(False, False)
    return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def preklapanja(b):
    """Parovi komponenti čiji se courtyard-i preklapaju, i komponente van ivice ploče."""
    out = []
    box = {}
    for f in b.GetFootprints():
        box[f.GetReference()] = kutija(f)
    refs = sorted(box)
    for i, a in enumerate(refs):
        ax0, ay0, ax1, ay1 = box[a]
        if ax0 < X0 - 0.01 or ay0 < Y0 - 0.01 or ax1 > X1 + 0.01 or ay1 > Y1 + 0.01:
            out.append((a, 'IVICA', box[a]))
        for c in refs[i + 1:]:
            bx0, by0, bx1, by1 = box[c]
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                out.append((a, c, round(min(ax1, bx1) - max(ax0, bx0), 2), round(min(ay1, by1) - max(ay0, by0), 2)))
    return out


def slika(b, ime='raspored.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.add_patch(plt.Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fill=False, lw=1.5))
    for f in b.GetFootprints():
        c = f.GetCourtyard(pcbnew.F_CrtYd)
        bb = c.BBox() if not c.IsEmpty() else f.GetBoundingBox(False, False)
        x0, y0 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())
        ax.add_patch(plt.Rectangle((x0, y0), pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight()), fill=False, ec='b', lw=0.6))
        for pd in f.Pads():
            q = pd.GetPosition(); sz = pd.GetBoundingBox()
            ax.add_patch(plt.Rectangle((pcbnew.ToMM(sz.GetLeft()), pcbnew.ToMM(sz.GetTop())), pcbnew.ToMM(sz.GetWidth()),
                                       pcbnew.ToMM(sz.GetHeight()), color='orange', alpha=0.6))
            ax.text(pcbnew.ToMM(q.x), pcbnew.ToMM(q.y), pd.GetNetname()[:6], fontsize=5, ha='center', va='center')
        p = f.GetPosition()
        ax.text(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y) - 0.6, f.GetReference(), fontsize=8, color='r', ha='center')
    ax.set_xlim(X0 - 1, X1 + 1); ax.set_ylim(Y1 + 1, Y0 - 1); ax.set_aspect('equal')
    fig.savefig(ime, dpi=110)


def postavi_klase(dsn):
    import re
    m = re.search(r'\(class kicad_default(.*?)\(circuit', dsn, re.S)
    if not m:
        return dsn
    nets = m.group(1)
    for _, mr, _, _ in KLASE:
        for n in mr:
            nets = re.sub(r'(?<=\s)%s(?=[\s)])' % re.escape(n), '', nets)
    dsn = dsn[:m.start(1)] + nets + dsn[m.end(1):]
    klase = ''
    for ime, mr, w, c in KLASE:
        klase += ('(class %s %s\n      (circuit\n        (use_via Via[0-1]_600:300_um)\n      )\n'
                  '      (rule\n        (width %d)\n        (clearance %d)\n      )\n    )\n    ' % (ime, ' '.join(mr), w, c))
    i = dsn.index('(class kicad_default')
    return dsn[:i] + klase + dsn[i:]


def main():
    b, nets = napravi()
    pr = preklapanja(b)
    for p in pr:
        print('PREKLAPANJE:', p)
    if '--slika' in sys.argv:
        slika(b)
    if '--samo-proveri' in sys.argv:
        return
    pcbnew.SaveBoard(IME + '.kicad_pcb', b)
    pcbnew.ExportSpecctraDSN(b, IME + '.dsn')
    t = postavi_klase(open(IME + '.dsn').read())
    open(IME + '.dsn', 'w').write(t)
    print('komponenti:', len(b.GetFootprints()), 'mreza:', len(nets))


if __name__ == '__main__':
    main()
