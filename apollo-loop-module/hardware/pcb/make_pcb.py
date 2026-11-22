"""Pravi KiCad 7 pločicu za Apollo loop driver MODUL v0.1 (60 x 45 mm, 2 sloja) – samo laboratorija.

Kompaktna verzija apollo-loop-driver mastera za ugradnju: 24 V ulaz, boost 34 V (TPS55340), linearni
push-pull izlaz 24,2 / 31,2 V do 250 mA (OPA197 + MJD122 + MMBT5401 za aktivno spuštanje), merenje struje
(šant 1 Ω, MCP6002 x5,02, komparator MCP6561), hardverska zaštita sa zadrškom, RP2040, UART 3,3 V na letvici.
GPIO raspored isti kao kod mastera (firmver apollo-loop-driver/firmware radi bez izmena pinova), plus UART0.

Pokretanje:  python3.12 make_pcb.py   (KiCad 7 pcbnew)  -> apollo_module.kicad_pcb, apollo_module.dsn
Raspored pinova proveren po datasheet-ovima (vidi ../../README.md):
  TPS55340PWP (HTSSOP-14): 1,2 SW; 3 VIN; 4 EN; 5 SS; 6 SYNC; 7 AGND; 8 COMP; 9 FB; 10 FREQ; 11 NC; 12-14 PGND; PowerPAD
  TPS560430X3F (SOT-23-6): 1 CB; 2 GND; 3 FB (=VOUT kod fiksne 3,3 V); 4 EN; 5 VIN; 6 SW
  MJD122 (DPAK): 1 B, 2/tab C, 3 E;  MMBT5401 / MMBT3904 / 2N7002 (SOT-23): 1 B/G, 2 E/S, 3 C/D
  OPA197, MCP6002, MCP6561, RP2040, W25Q16JV: isti raspored kao u apollo-loop-driver (proveren tamo)
"""
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew

FP = '/usr/share/kicad/footprints/'
MM = pcbnew.FromMM
IME = 'apollo_module'

R0603 = ('Resistor_SMD', 'R_0603_1608Metric')
R0805 = ('Resistor_SMD', 'R_0805_2012Metric')
R2512 = ('Resistor_SMD', 'R_2512_6332Metric')
C0603 = ('Capacitor_SMD', 'C_0603_1608Metric')
C0805 = ('Capacitor_SMD', 'C_0805_2012Metric')
C1210 = ('Capacitor_SMD', 'C_1210_3225Metric')
SOT23 = ('Package_TO_SOT_SMD', 'SOT-23')
SOT235 = ('Package_TO_SOT_SMD', 'SOT-23-5')
SOIC8 = ('Package_SO', 'SOIC-8_3.9x4.9mm_P1.27mm')
DSMA = ('Diode_SMD', 'D_SMA')
TB2 = ('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal')

# ref: (biblioteka, vrednost, {pin: mreža})
P = {
    # ---- ulaz 24 V
    'J1': (TB2, '24V IN', {'1': '+24V_IN', '2': 'GND'}),
    'F1': (('Fuse', 'Fuse_1206_3216Metric'), '3A', {'1': '+24V_IN', '2': 'VIN_F'}),
    'D1': (DSMA, 'SS34', {'2': 'VIN_F', '1': 'VIN'}),
    'C1': (('Capacitor_SMD', 'CP_Elec_6.3x7.7'), '47u/50V', {'1': 'VIN', '2': 'GND'}),
    'C2': (C1210, '10u/50V', {'1': 'VIN', '2': 'GND'}),
    # ---- boost 34 V (TPS55340, ~580 kHz)
    'U1': (('Package_SO', 'HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3x3.1mm'), 'TPS55340PWPR',
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
    'C9': (C0603, '1u', {'1': 'VIN', '2': 'GND'}),
    # ---- 3,3 V buck (TPS560430X3F, fiksnih 3,3 V)
    'U2': (('Package_TO_SOT_SMD', 'SOT-23-6'), 'TPS560430X3FDBVR',
           {'1': 'CB', '2': 'GND', '3': '+3V3', '4': 'VIN', '5': 'VIN', '6': 'SW3'}),
    'C10': (C0603, '100n', {'1': 'CB', '2': 'SW3'}),
    'L2': (('Inductor_SMD', 'L_Bourns-SRN4018'), '15uH SRN4018-150M', {'1': 'SW3', '2': '+3V3'}),
    'C11': (C1210, '10u/50V', {'1': 'VIN', '2': 'GND'}),
    'C12': (C0805, '10u', {'1': '+3V3', '2': 'GND'}),
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
    'J2': (TB2, 'LOOP OUT', {'1': 'LOOP_OUT', '2': 'ISENSE'}),
    'J3': (TB2, 'LOOP IN', {'1': 'LOOP_IN', '2': 'ISENSE'}),
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
    'U5': (SOT235, 'MCP6561', {'1': 'BIT', '2': 'GND', '3': 'IAMP', '4': 'PRAG_F', '5': '+3V3'}),
    'C21': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'R23': (R0603, '10k', {'1': 'PRAG', '2': 'PRAG_F'}),
    'C22': (C0603, '1u', {'1': 'PRAG_F', '2': 'GND'}),
    # ---- zaštita od preopterećenja > ~285 mA sa zadrškom (kao kod mastera, prag 1,43 V)
    'U6': (SOT235, 'MCP6561', {'1': 'OCP', '2': 'GND', '3': 'OC_IN', '4': 'OC_REF', '5': '+3V3'}),
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
    # ---- RP2040 (isti GPIO kao master; GP0/GP1 = UART0; OC_FLAG je sada OCP)
    'U7': (('Package_DFN_QFN', 'QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm'), 'RP2040',
           {'1': '+3V3', '10': '+3V3', '22': '+3V3', '33': '+3V3', '42': '+3V3', '49': '+3V3',
            '2': 'TX', '3': 'RX', '4': 'NIVO', '5': 'EN_N', '6': 'BIT', '7': 'OC_RST', '8': 'OCP',
            '19': 'GND', '20': 'XIN', '21': 'XOUT', '23': 'DVDD', '50': 'DVDD', '45': 'DVDD',
            '24': 'SWCLK', '25': 'SWDIO', '26': 'RUN', '27': 'PRAG', '37': 'LED', '38': 'IAMP', '39': 'VLOOP',
            '40': 'VRET', '43': '+3V3', '44': '+3V3', '46': 'USB_DM', '47': 'USB_DP', '48': '+3V3',
            '51': 'QSD3', '52': 'QSCLK', '53': 'QSD0', '54': 'QSD2', '55': 'QSD1', '56': 'QSS', '57': 'GND'}),
    'U8': (('Package_SO', 'SOIC-8_5.23x5.23mm_P1.27mm'), 'W25Q16JVSS',
           {'1': 'QSS', '2': 'QSD1', '3': 'QSD2', '4': 'GND', '5': 'QSD0', '6': 'QSCLK', '7': 'QSD3', '8': '+3V3'}),
    'C25': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'R29': (R0603, '10k', {'1': 'QSS', '2': '+3V3'}),
    'R30': (R0603, '1k', {'1': 'QSS', '2': 'BOOT'}),
    'R31': (R0603, '10k', {'1': 'RUN', '2': '+3V3'}),
    'Y1': (('Crystal', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'), '12MHz', {'1': 'XIN', '2': 'GND', '3': 'XO', '4': 'GND'}),
    'R32': (R0603, '1k', {'1': 'XOUT', '2': 'XO'}),
    'C26': (C0603, '33p', {'1': 'XIN', '2': 'GND'}),
    'C27': (C0603, '33p', {'1': 'XO', '2': 'GND'}),
    'C28': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'C29': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'C30': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'C31': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'C32': (C0603, '1u', {'1': '+3V3', '2': 'GND'}),
    'C33': (C0603, '100n', {'1': 'DVDD', '2': 'GND'}),
    'C34': (C0603, '1u', {'1': 'DVDD', '2': 'GND'}),
    'R33': (R0603, '27', {'1': 'USB_DP', '2': 'DP_H'}),
    'R34': (R0603, '27', {'1': 'USB_DM', '2': 'DM_H'}),
    'R35': (R0603, '1k', {'1': 'LED', '2': 'LED_A'}),
    'D5': (('LED_SMD', 'LED_0603_1608Metric'), 'LED', {'1': 'GND', '2': 'LED_A'}),
    # letvica za ugradnju: GND, 3V3, TX, RX, RUN, BOOT, USB D+, USB D- (za prvo programiranje MicroPython-a)
    'J4': (('Connector_PinHeader_2.54mm', 'PinHeader_1x08_P2.54mm_Vertical'), 'HOST',
           {'1': 'GND', '2': '+3V3', '3': 'TX', '4': 'RX', '5': 'RUN', '6': 'BOOT', '7': 'DP_H', '8': 'DM_H'}),
    'J5': (('Connector_PinHeader_1.27mm', 'PinHeader_1x03_P1.27mm_Vertical'), 'SWD',
           {'1': 'SWCLK', '2': 'GND', '3': 'SWDIO'}),
}

POZ = {
    # ulaz i boost (gore)
    'J1': (105.75, 105.0, 180), 'F1': (111.5, 102.3, 0), 'D1': (111.5, 106.3, 0), 'C1': (104.4, 113.6, 0), 'C2': (111.3, 110.8, 90),
    'U1': (118.6, 108.4, 0), 'L1': (126.1, 104.1, 0), 'D2': (133.6, 102.8, 0), 'C3': (133.3, 107.3, 0), 'C4': (133.3, 110.6, 0),
    'C5': (141.6, 105.6, 0), 'C9': (114.8, 113.4, 90), 'R1': (121.0, 114.0, 0), 'R2': (121.0, 115.6, 0), 'R3': (117.6, 115.6, 0),
    'R4': (117.6, 114.0, 0), 'C6': (124.6, 114.0, 0), 'C7': (124.6, 115.6, 0), 'C8': (124.6, 112.4, 0),
    # buck 3V3 (levo)
    'U2': (104.0, 120.6, 0), 'C10': (104.0, 123.6, 0), 'L2': (109.6, 121.2, 0), 'C11': (104.4, 126.6, 0), 'C12': (113.6, 119.6, 90),
    'C13': (115.8, 119.6, 90),
    # VSET
    'R5': (127.6, 118.0, 0), 'R6': (127.6, 119.6, 0), 'C14': (127.6, 121.2, 0), 'R7': (127.6, 122.8, 0), 'Q2': (131.6, 124.6, 0),
    'R8': (127.6, 124.4, 0), 'Q3': (131.6, 119.0, 0), 'R9': (131.6, 121.8, 0),
    # izlazni stepen
    'U3': (141.0, 117.4, 0), 'C15': (136.0, 114.4, 0), 'R10': (145.6, 121.6, 0), 'R11': (141.0, 121.6, 0), 'C16': (141.0, 123.2, 0),
    'R12': (137.0, 121.6, 0), 'Q1': (154.0, 106.0, 0), 'R13': (153.0, 112.8, 0), 'Q4': (148.0, 116.6, 0), 'Q5': (153.0, 117.4, 0),
    'R14': (156.8, 117.4, 90),
    # petlja
    'F2': (156.8, 125.0, 90), 'D3': (151.2, 124.8, 90), 'R15': (147.6, 125.6, 90), 'R16': (147.6, 129.6, 90), 'C17': (145.6, 129.6, 90),
    'J2': (146.25, 140.0, 0), 'J3': (154.25, 140.0, 0), 'R17': (157.6, 132.6, 90), 'R18': (155.6, 132.6, 90), 'C18': (153.6, 132.6, 90),
    # merenje i zaštita
    'R19': (141.0, 134.4, 0), 'R20': (137.0, 130.6, 0), 'C19': (137.0, 132.2, 0), 'U4': (140.6, 127.0, 0), 'C20': (136.0, 124.8, 0),
    'R21': (144.6, 131.0, 90), 'R22': (142.6, 131.0, 90), 'U5': (132.0, 131.0, 0), 'C21': (132.0, 128.4, 0), 'R23': (132.0, 133.6, 0),
    'C22': (132.0, 135.2, 0), 'U6': (126.6, 131.0, 0), 'C23': (126.6, 128.4, 0), 'R24': (126.6, 133.6, 0), 'R25': (126.6, 135.2, 0),
    'R26': (122.6, 128.4, 0), 'C24': (122.6, 126.8, 0), 'D4': (136.6, 135.8, 0), 'R27': (136.6, 137.6, 0), 'Q6': (136.0, 127.8, 0),
    'Q7': (132.4, 138.2, 0), 'R28': (128.4, 138.2, 0),
    # RP2040
    'U7': (116.0, 131.4, 0), 'U8': (105.2, 132.4, 90), 'C25': (105.2, 137.6, 0), 'R29': (109.6, 128.6, 90), 'R30': (109.6, 136.6, 90),
    'R31': (122.4, 135.6, 0), 'Y1': (116.0, 138.4, 0), 'R32': (120.4, 138.0, 90), 'C26': (112.6, 138.0, 90), 'C27': (119.0, 140.6, 0),
    'C28': (111.0, 131.4, 90), 'C29': (121.0, 131.4, 90), 'C30': (116.0, 126.2, 0), 'C31': (112.8, 126.2, 0), 'C32': (119.4, 126.2, 0),
    'C33': (121.0, 128.4, 90), 'C34': (111.0, 134.8, 90),
    'R33': (124.4, 138.6, 90), 'R34': (126.0, 138.6, 90), 'R35': (101.8, 140.0, 90), 'D5': (101.8, 137.0, 90),
    'J4': (104.0, 143.0, 90), 'J5': (126.6, 143.2, 90),
}

KLASE = [
    ('boost', ['+24V_IN', 'VIN_F', 'VIN', 'SW'], 800, 300),
    ('petlja', ['+34V', 'NE', 'LOOP_DRV', 'LOOP_OUT', 'ISENSE', 'LOOP_IN', 'PE'], 600, 300),
    ('hv', ['NB', 'U3OUT', 'SW3'], 300, 300),
    ('logika3v3', ['+3V3', 'DVDD'], 300, 150),
]

BLOKOVI = [
    ('1 ULAZ 24V', ['J1', 'F1', 'D1', 'C1', 'C2']),
    ('2 BOOST 34V', ['U1', 'L1', 'D2', 'C3', 'C4', 'C5', 'R1', 'R2', 'R3', 'R4', 'C6', 'C7', 'C8', 'C9']),
    ('3 BUCK 3V3', ['U2', 'C10', 'L2', 'C11', 'C12', 'C13']),
    ('4 VSET', ['R5', 'R6', 'C14', 'R7', 'Q2', 'R8', 'Q3', 'R9']),
    ('5 IZLAZ 24/31V', ['U3', 'C15', 'R10', 'R11', 'C16', 'R12', 'Q1', 'R13', 'Q4', 'Q5', 'R14']),
    ('6 PETLJA', ['F2', 'D3', 'R15', 'R16', 'C17', 'J2', 'J3', 'R17', 'R18', 'C18']),
    ('7 MERENJE I ZASTITA', ['R19', 'R20', 'C19', 'U4', 'C20', 'R21', 'R22', 'U5', 'C21', 'R23', 'C22',
                             'U6', 'C23', 'R24', 'R25', 'R26', 'C24', 'D4', 'R27', 'Q6', 'Q7', 'R28']),
    ('8 RP2040', ['U7', 'U8', 'C25', 'R29', 'R30', 'R31', 'Y1', 'R32', 'C26', 'C27', 'C28', 'C29', 'C30',
                  'C31', 'C32', 'C33', 'C34', 'R33', 'R34', 'R35', 'D5', 'J4', 'J5']),
]

PREVODI = []

X0, Y0, X1, Y1 = 100, 100, 160, 145


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
    nc = ds.m_NetSettings.m_DefaultNetClass
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
    for txt, x, y, sz in [('APOLLO LOOP DRIVER MODUL v0.1 - SAMO LAB', 130, 104, 1.0),
                          ('J4: GND 3V3 TX RX RUN BOOT D+ D-', 130, 107, 0.8)]:
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
        kz.SetDoNotAllowCopperPour(False); kz.SetDoNotAllowPads(False); kz.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); kz.SetLayerSet(ls)
        o = kz.Outline(); o.NewOutline()
        for x, y in [(ax, ay), (bx, ay), (bx, by), (ax, by)]:
            o.Append(MM(x), MM(y))
        b.Add(kz)
    ds.SetBoardThickness(MM(1.6))
    return b, nets


def preklapanja(b):
    """Parovi komponenti čiji se courtyard-i preklapaju, i komponente van ivice ploče."""
    out = []
    box = {}
    for f in b.GetFootprints():
        c = f.GetCourtyard(pcbnew.F_CrtYd)
        bb = c.BBox() if not c.IsEmpty() else f.GetBoundingBox(False, False)
        box[f.GetReference()] = (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                                 pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))
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
