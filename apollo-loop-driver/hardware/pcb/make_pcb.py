"""Pravi KiCad 7 pločicu za Apollo XP95 laboratorijski drajver.

Pokretanje:  python3.12 make_pcb.py   (treba KiCad 7 i njegov pcbnew modul)
Izlaz:       apollo_loop_driver.kicad_pcb (raspored + mreže, bez vodova)
             apollo_loop_driver.dsn       (za Freerouting)
"""
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew

FP = '/usr/share/kicad/footprints/'
MM = pcbnew.FromMM

R0805 = ('Resistor_SMD', 'R_0805_2012Metric')
C0805 = ('Capacitor_SMD', 'C_0805_2012Metric')
C1206 = ('Capacitor_SMD', 'C_1206_3216Metric')
R2512 = ('Resistor_SMD', 'R_2512_6332Metric')
SOT23 = ('Package_TO_SOT_SMD', 'SOT-23')
SOIC8 = ('Package_SO', 'SOIC-8_3.9x4.9mm_P1.27mm')
TB2 = ('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal')
CP8 = ('Capacitor_THT', 'CP_Radial_D8.0mm_P3.50mm')

# ref: (biblioteka, x_mm, y_mm, rot, vrednost, {pin: mreža})
# Ploča: 130 x 95 mm, gornji levi ugao u (100, 100). Sve je na ploči, bez modula.
R0603 = ('Resistor_SMD', 'R_0603_1608Metric')
C0603 = ('Capacitor_SMD', 'C_0603_1608Metric')
CP10 = ('Capacitor_THT', 'CP_Radial_D10.0mm_P5.00mm')
P = {
    # ---- USB i galvanska izolacija (gornji levi ugao, posebna masa GND_USB)
    'J5':  (('Connector_USB', 'USB_B_OST_USB-B1HSxx_Horizontal'), 117, 112, 180, 'USB-B',
            {'1': 'VBUS_USB', '2': 'USB_DM_C', '3': 'USB_DP_C', '4': 'GND_USB', '5': 'GND_USB'}),
    'U8':  (('Package_SO', 'SOIC-16W_7.5x10.3mm_P1.27mm'), 130, 113, 0, 'ADuM3160',
            {'1': 'VBUS_USB', '2': 'GND_USB', '3': 'VDD1', '4': 'VDD1', '5': 'VDD1', '6': 'USB_DM_C',
             '7': 'USB_DP_C', '8': 'GND_USB', '9': 'GND', '10': 'DP_ISO', '11': 'DM_ISO', '12': 'VDD2',
             '13': 'VDD2', '14': 'VDD2', '15': 'GND', '16': '+5V'}),
    'C20': (C0805, 113, 118, 90, '10u', {'1': 'VBUS_USB', '2': 'GND_USB'}),
    'C21': (C0603, 116, 121, 0, '1u', {'1': 'VDD1', '2': 'GND_USB'}),
    'C23': (C0603, 128, 121, 0, '1u', {'1': 'VDD2', '2': 'GND'}),
    'C24': (C0603, 129, 106, 0, '100n', {'1': '+5V', '2': 'GND'}),
    'R21': (R0603, 133, 113, 0, '27', {'1': 'DP_ISO', '2': 'USB_DP'}),
    'R22': (R0603, 133, 116, 0, '27', {'1': 'DM_ISO', '2': 'USB_DM'}),
    # ---- ulaz 24 V, zaštita, 5 V
    'J1':  (TB2, 106, 140, 270, '24V IN', {'1': '+24V_IN', '2': 'GND'}),
    'F1':  (('Fuse', 'Fuse_1206_3216Metric'), 115, 139, 90, '3A', {'1': '+24V_IN', '2': 'VIN_F'}),
    'D3':  (('Diode_SMD', 'D_SMA'), 115, 133, 90, 'SS34', {'2': 'VIN_F', '1': '+24V'}),
    'C1':  (CP8, 121, 140, 90, '100u/50V', {'1': '+24V', '2': 'GND'}),
    'U2':  (('Converter_DCDC', 'Converter_DCDC_RECOM_R-78E-0.5_THT'), 108, 160, 0, 'R-78E5.0-0.5',
            {'1': '+24V', '2': 'GND', '3': '+5V'}),
    'C16': (C1206, 108, 158, 0, '4u7/50V', {'1': '+24V', '2': 'GND'}),
    'C10': (C1206, 115, 158, 0, '10u', {'1': '+5V', '2': 'GND'}),
    # ---- boost 24 -> 34 V na ploči (LM2587-ADJ)
    'U1':  (('Package_TO_SOT_SMD', 'TO-263-5_TabPin3'), 115, 167, 0, 'LM2587S-ADJ',
            {'1': 'COMP', '2': 'BFB', '3': 'GND', '4': 'SW', '5': '+24V'}),
    'L1':  (('Inductor_SMD', 'L_Bourns_SRR1260'), 140, 130, 90, '100uH SRR1280-101M', {'1': '+24V', '2': 'SW'}),
    'D1':  (('Diode_SMD', 'D_SMC'), 154, 124, 0, 'SS56', {'2': 'SW', '1': '+34V'}),
    'C31': (C1206, 141, 106, 90, '1u/50V', {'1': '+24V', '2': 'GND'}),
    'R30': (R0805, 140, 113, 90, '3k0', {'1': 'COMP', '2': 'CC'}),
    'C30': (C0805, 140, 118, 90, '680n', {'1': 'CC', '2': 'GND'}),
    'R31': (R0805, 146, 118, 0, '53k6', {'1': '+34V', '2': 'BFB'}),
    'R32': (R0805, 141, 122, 0, '2k', {'1': 'BFB', '2': 'GND'}),
    'C3':  (CP10, 158, 128, 0, '470u/50V lowESR', {'1': '+34V', '2': 'GND'}),
    'C32': (CP10, 172, 128, 0, '470u/50V lowESR', {'1': '+34V', '2': 'GND'}),
    'C5':  (C1206, 160, 121, 0, '1u/50V', {'1': '+34V', '2': 'GND'}),
    # ---- referenca i VSET
    'U3':  (SOT23, 153, 146, 0, 'REF3033', {'1': '+5V', '2': 'REF', '3': 'GND'}),
    'C17': (C0805, 153, 141, 0, '100n', {'1': '+5V', '2': 'GND'}),
    'R3':  (R0805, 159, 146, 0, '1k', {'1': 'REF', '2': 'VSET'}),
    'R4':  (R0805, 164, 150, 90, '15k', {'1': 'VSET', '2': 'GND'}),
    'C6':  (C0805, 167, 150, 90, '10n', {'1': 'VSET', '2': 'GND'}),
    'R5':  (R0805, 170, 150, 90, '3k24', {'1': 'VSET', '2': 'Q2D'}),
    'Q2':  (SOT23, 170, 156, 0, '2N7002', {'1': 'NIVO_G', '2': 'GND', '3': 'Q2D'}),
    'R19': (R0805, 164, 157, 0, '100', {'1': 'NIVO', '2': 'NIVO_G'}),
    'Q5':  (SOT23, 174, 150, 0, '2N7002', {'1': 'EN_N', '2': 'GND', '3': 'VSET'}),
    'R18': (R0805, 174, 156, 90, '100k', {'1': 'EN_N', '2': '+3V3'}),
    # ---- drajver petlje
    'U4':  (SOIC8, 183, 146, 0, 'OPA197', {'2': 'FB', '3': 'VSET', '4': 'GND', '6': 'U4OUT', '7': '+34V'}),
    'C13': (C0805, 183, 139, 0, '100n', {'1': '+34V', '2': 'GND'}),
    'R6':  (R0805, 190, 144, 0, '1k', {'1': 'U4OUT', '2': 'NB'}),
    'R8':  (R0805, 183, 153, 0, '91k', {'1': 'LOOP_DRV', '2': 'FB'}),
    'C7':  (C0805, 183, 156, 0, '100p', {'1': 'LOOP_DRV', '2': 'FB'}),
    'R9':  (R0805, 178, 153, 90, '10k', {'1': 'FB', '2': 'GND'}),
    'Q3':  (('Package_TO_SOT_THT', 'TO-220-3_Vertical'), 168, 121, 0, 'TIP122 + hladnjak',
            {'1': 'NB', '2': '+34V', '3': 'NE'}),
    'Q4':  (SOT23, 196, 120, 0, 'MMBT3904', {'1': 'NE', '2': 'LOOP_DRV', '3': 'NB'}),
    'R7':  (R2512, 204, 124, 90, '1R2 1W', {'1': 'NE', '2': 'LOOP_DRV'}),
    # ---- zaštita izlaza
    'F2':  (('Fuse', 'Fuse_2920_7451Metric'), 214, 118, 90, 'PTC 750mA/60V', {'1': 'LOOP_DRV', '2': 'LOOP_OUT'}),
    'D2':  (('Diode_SMD', 'D_SMB'), 214, 133, 90, 'SMBJ36A', {'1': 'LOOP_OUT', '2': 'GND'}),
    'R10': (R0805, 208, 138, 90, '100k', {'1': 'LOOP_OUT', '2': 'VLOOP'}),
    'R11': (R0805, 208, 144, 90, '10k', {'1': 'VLOOP', '2': 'GND'}),
    'J2':  (TB2, 224, 118, 90, 'LOOP OUT', {'1': 'LOOP_OUT', '2': 'ISENSE'}),
    # ---- merenje struje
    'R14': (R2512, 218, 160, 90, '1R 1W', {'1': 'ISENSE', '2': 'GND'}),
    'R15': (R0805, 211, 165, 0, '1k', {'1': 'ISENSE', '2': 'NA'}),
    'C8':  (C0805, 207, 169, 90, '1n', {'1': 'NA', '2': 'GND'}),
    'U5':  (SOIC8, 199, 169, 0, 'MCP6002', {'1': 'IAMP', '2': 'NM', '3': 'NA', '4': 'GND',
                                           '5': 'GND', '6': 'U5B', '7': 'U5B', '8': '+3V3'}),
    'C14': (C0805, 199, 162, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'R17': (R0805, 193, 175, 90, '10k', {'1': 'NM', '2': 'GND'}),
    'R16': (R0805, 199, 176, 0, '40k2', {'1': 'NM', '2': 'IAMP'}),
    'U6':  (('Package_TO_SOT_SMD', 'SOT-23-5'), 186, 174, 0, 'MCP6561',
            {'1': 'BIT', '2': 'GND', '3': 'IAMP', '4': 'PRAG_F', '5': '+3V3'}),
    'C15': (C0805, 186, 168, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'R20': (R0805, 180, 180, 0, '10k', {'1': 'PRAG', '2': 'PRAG_F'}),
    'C9':  (C0805, 186, 180, 90, '1u', {'1': 'PRAG_F', '2': 'GND'}),
    'J3':  (TB2, 224, 176, 90, 'LOOP IN', {'1': 'LOOP_IN', '2': 'ISENSE'}),
    'R12': (R0805, 214, 182, 0, '100k', {'1': 'LOOP_IN', '2': 'VRET'}),
    'R13': (R0805, 208, 186, 90, '10k', {'1': 'VRET', '2': 'GND'}),
    # ---- RP2040 (umesto Pico modula)
    'U9':  (('Package_DFN_QFN', 'QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm'), 140, 168, 0, 'RP2040',
            {'1': '+3V3', '10': '+3V3', '22': '+3V3', '33': '+3V3', '42': '+3V3', '49': '+3V3',
             '4': 'NIVO', '5': 'EN_N', '6': 'BIT', '7': 'OC_RST', '8': 'OC_FLAG', '19': 'GND', '20': 'XIN', '21': 'XOUT',
             '23': 'DVDD', '50': 'DVDD', '45': 'DVDD', '24': 'SWCLK', '25': 'SWDIO', '26': 'RUN',
             '27': 'PRAG', '37': 'LED', '38': 'IAMP', '39': 'VLOOP', '40': 'VRET',
             '43': '+3V3', '44': '+3V3', '46': 'USB_DM', '47': 'USB_DP', '48': '+3V3',
             '51': 'QSD3', '52': 'QSCLK', '53': 'QSD0', '54': 'QSD2', '55': 'QSD1', '56': 'QSS', '57': 'GND'}),
    'U10': (('Package_SO', 'SOIC-8_5.23x5.23mm_P1.27mm'), 124, 170, 0, 'W25Q16JVSS',
            {'1': 'QSS', '2': 'QSD1', '3': 'QSD2', '4': 'GND', '5': 'QSD0', '6': 'QSCLK', '7': 'QSD3', '8': '+3V3'}),
    'C53': (C0603, 124, 164, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'R23': (R0603, 118, 165, 90, '10k', {'1': 'QSS', '2': '+3V3'}),
    'R24': (R0603, 118, 175, 90, '1k', {'1': 'QSS', '2': 'BOOT'}),
    'SW1': (('Button_Switch_SMD', 'SW_Push_1P1T_XKB_TS-1187A'), 114, 184, 0, 'BOOTSEL', {'1': 'BOOT', '2': 'GND'}),
    'SW2': (('Button_Switch_SMD', 'SW_Push_1P1T_XKB_TS-1187A'), 124, 187, 0, 'RESET', {'1': 'RUN', '2': 'GND'}),
    'R25': (R0603, 133, 180, 0, '10k', {'1': 'RUN', '2': '+3V3'}),
    'Y1':  (('Crystal', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'), 140, 179, 0, '12MHz',
            {'1': 'XIN', '2': 'GND', '3': 'XO', '4': 'GND'}),
    'R26': (R0603, 145, 176, 0, '1k', {'1': 'XOUT', '2': 'XO'}),
    'C51': (C0603, 136, 183, 0, '33p', {'1': 'XIN', '2': 'GND'}),
    'C52': (C0603, 144, 183, 0, '33p', {'1': 'XO', '2': 'GND'}),
    'C40': (C0603, 134, 162, 90, '100n', {'1': '+3V3', '2': 'GND'}),
    'C41': (C0603, 146, 162, 90, '100n', {'1': '+3V3', '2': 'GND'}),
    'C42': (C0603, 147, 168, 90, '100n', {'1': '+3V3', '2': 'GND'}),
    'C43': (C0603, 133, 168, 90, '100n', {'1': '+3V3', '2': 'GND'}),
    'C44': (C0603, 140, 160, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'C45': (C0603, 134, 174, 90, '100n', {'1': '+3V3', '2': 'GND'}),
    'C46': (C0603, 146, 172, 90, '100n', {'1': 'DVDD', '2': 'GND'}),
    'C47': (C0603, 149, 165, 90, '1u', {'1': 'DVDD', '2': 'GND'}),
    'C48': (C0603, 149, 160, 90, '1u', {'1': '+3V3', '2': 'GND'}),
    'U11': (SOT23 if False else ('Package_TO_SOT_SMD', 'SOT-23-5'), 124, 152, 0, 'AP2112K-3.3',
            {'1': '+5V', '2': 'GND', '3': '+5V', '5': '+3V3'}),
    'C54': (C0805, 119, 150, 90, '1u', {'1': '+5V', '2': 'GND'}),
    'C55': (C0805, 129, 150, 90, '1u', {'1': '+3V3', '2': 'GND'}),
    'J6':  (('Connector_PinHeader_2.54mm', 'PinHeader_1x03_P2.54mm_Vertical'), 129, 152, 90, 'SWD',
            {'1': 'SWCLK', '2': 'GND', '3': 'SWDIO'}),
    'R27': (R0603, 160, 176, 0, '1k', {'1': 'LED', '2': 'LED_A'}),
    'D5':  (('LED_SMD', 'LED_0805_2012Metric'), 165, 176, 0, 'LED', {'2': 'LED_A', '1': 'GND'}),
    # ---- dodatni kondenzatori za razdvajanje i filtri
    'C22': (C0603, 0, 0, 0, '100n', {'1': 'VDD1', '2': 'GND_USB'}),
    'C25': (C0603, 0, 0, 0, '100n', {'1': 'VDD2', '2': 'GND'}),
    'C26': (C0603, 0, 0, 0, '1u', {'1': '+5V', '2': 'GND'}),
    'C49': (C0603, 0, 0, 0, '100n', {'1': 'DVDD', '2': 'GND'}),
    'C56': (C0603, 0, 0, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'C57': (C0603, 0, 0, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'C58': (C1206, 0, 0, 0, '1u/50V', {'1': '+34V', '2': 'GND'}),
    'C59': (C0603, 0, 0, 0, '1n', {'1': 'VLOOP', '2': 'GND'}),
    'C60': (C0603, 0, 0, 0, '1n', {'1': 'VRET', '2': 'GND'}),
    'C63': (C1206, 0, 0, 0, '10u/50V', {'1': '+34V', '2': 'GND'}),   # VF uz katodu D1
    # ---- hladnjak za Q3 (polozen TO-220, zavrtanj M3 kroz tab i hladnjak)
    'HS1': (('Heatsink', 'Heatsink_AAVID_TV5G_TO220_Horizontal'), 0, 0, 0, 'Aavid TV5G', {}),
    # ---- hardverska zaštita od kratkog spoja (> ~500 mA), sa zadrškom (latch)
    'U12': (('Package_TO_SOT_SMD', 'SOT-23-5'), 0, 0, 0, 'MCP6561',
            {'1': 'OCP', '2': 'GND', '3': 'OC_IN', '4': 'OC_REF', '5': '+3V3'}),
    'C61': (C0603, 0, 0, 0, '100n', {'1': '+3V3', '2': 'GND'}),
    'R33': (R0603, 0, 0, 0, '3k3', {'1': '+3V3', '2': 'OC_REF'}),
    'R34': (R0603, 0, 0, 0, '10k', {'1': 'OC_REF', '2': 'GND'}),
    'R35': (R0603, 0, 0, 0, '10k', {'1': 'IAMP', '2': 'OC_IN'}),
    'C62': (C0603, 0, 0, 0, '1n', {'1': 'OC_IN', '2': 'GND'}),
    'D6':  (('Diode_SMD', 'D_SOD-323'), 0, 0, 0, 'BAT54J', {'2': 'OCP', '1': 'OC_FB'}),
    'R36': (R0603, 0, 0, 0, '1k', {'1': 'OC_FB', '2': 'OC_IN'}),
    'Q6':  (SOT23, 0, 0, 0, '2N7002', {'1': 'OCP', '2': 'GND', '3': 'VSET'}),
    'Q7':  (SOT23, 0, 0, 0, '2N7002', {'1': 'OC_RST', '2': 'GND', '3': 'OC_IN'}),
    'R37': (R0603, 0, 0, 0, '100k', {'1': 'OC_RST', '2': 'GND'}),
}


# Konačne pozicije (x, y, rotacija) - nadjačavaju vrednosti iz P
POZ = {
    'J5': (115, 112, 180), 'U8': (130, 113, 0), 'C20': (121, 119, 90), 'C21': (124, 123, 0), 'C23': (136, 121, 0),
    'C24': (136.2, 103.3, 90), 'R21': (137.6, 112, 0), 'R22': (137.6, 115, 0),
    'J1': (106, 140, 270), 'F1': (115, 145, 90), 'D3': (115, 136, 90), 'C1': (140, 132, 0), 'U2': (126, 146.5, 0),
    'C16': (122, 152, 0), 'C10': (130, 152, 0),
    'U1': (164, 118, 0), 'L1': (146.9, 119, 0), 'D1': (153, 107.3, 90), 'C31': (157, 125.5, 0), 'R30': (159.5, 108.5, 0),
    'C30': (163, 108.5, 0), 'R31': (159.5, 111, 0), 'R32': (163, 111, 0), 'C3': (170, 106, 0), 'C32': (163, 131, 0),
    'C5': (159.5, 103, 0),
    'U3': (154, 141, 0), 'C17': (154, 146, 0), 'R3': (159, 141, 0), 'R4': (163, 144, 90), 'C6': (166, 144, 90),
    'R5': (169, 141, 90), 'Q2': (169, 147, 0), 'R19': (163, 149, 0), 'Q5': (174, 141, 0), 'R18': (174, 146.5, 90),
    'U4': (190, 134, 180), 'C13': (184.5, 135.8, 90), 'R6': (183, 131, 0), 'R8': (196, 133, 0), 'C7': (196, 136, 0),
    'R9': (199.5, 134.5, 90), 'Q3': (188, 127, 0), 'Q4': (205, 121, 0), 'R7': (205.5, 113, 90),
    'F2': (214, 115, 90), 'D2': (214, 129, 90), 'R10': (210, 139, 90), 'R11': (210, 145, 90), 'J2': (224, 118, 90),
    'R14': (218, 160, 90), 'R15': (211, 165, 0), 'C8': (207, 169, 90), 'U5': (199, 169, 0), 'C14': (199, 162, 0),
    'R17': (193, 175, 90), 'R16': (199, 176, 0), 'U6': (186, 174, 0), 'C15': (186, 168, 0), 'R20': (180, 180, 0),
    'C9': (186, 180, 90), 'J3': (224, 176, 90), 'R12': (214, 182, 0), 'R13': (208, 186, 90),
    'U9': (140, 172, 0), 'U10': (127.5, 167, 90), 'C53': (127.5, 161, 0), 'R23': (121.5, 164, 90), 'R24': (118, 179, 90),
    'SW1': (113.5, 188, 0), 'SW2': (125.5, 188, 0), 'R25': (133, 184, 0), 'Y1': (140, 183, 0), 'R26': (145, 180, 0),
    'C51': (136, 187, 0), 'C52': (144, 187, 0), 'C40': (134, 166, 90), 'C41': (146, 166, 90), 'C42': (147, 172, 90),
    'C43': (133, 172, 90), 'C44': (140, 164, 0), 'C45': (134, 178, 90), 'C46': (146, 176, 90), 'C47': (149, 169, 90),
    'C48': (149, 164, 90), 'U11': (139, 146.5, 0), 'C54': (135.5, 151, 90), 'C55': (142.5, 151, 90), 'J6': (152, 190, 90),
    'R27': (160, 181, 0), 'D5': (165, 181, 0),
    'C22': (118.5, 123.5, 0), 'C25': (136, 123.5, 0), 'C26': (134.2, 103.3, 90), 'C49': (149, 176, 90),
    'C56': (151.8, 172, 90), 'C57': (143.5, 164, 0), 'C58': (181, 135.8, 90), 'C59': (213.5, 145, 90),
    'C60': (211, 186, 90),
    'R33': (183, 147.0, 0), 'R34': (183, 150.0, 0), 'C61': (183, 153.0, 0), 'U12': (188.5, 150.0, 0),
    'R35': (194, 147.0, 0), 'C62': (194, 153.0, 0), 'R36': (198, 150.0, 0), 'D6': (198, 153.5, 0),
    'C63': (147.2, 102.6, 180), 'HS1': (190.54, 110.34, 0), 'Q7': (199, 146.5, 0), 'R37': (203.5, 147.0, 90), 'Q6': (178.5, 146, 0),
}
assert set(POZ) == set(P), set(P) ^ set(POZ)

# Klase vodova prema struji (1 oz bakar, porast ~10 °C, IPC-2152) i naponu (IPC-2221 B2)
KLASE = [
    # ime, mreže, širina um, razmak um
    ('boost', ['+24V_IN', 'VIN_F', '+24V', 'SW'], 1000, 600),         # do ~1,5 A vrh; = širina pina TO-263
    ('petlja', ['+34V', 'NE', 'LOOP_DRV', 'LOOP_OUT', 'ISENSE'], 600, 600),  # 0,5 A petlja (treba ~0,3 mm)
    ('napajanje', ['+5V', 'VBUS_USB', 'GND_USB'], 400, 200),          # < 150 mA
    ('hv', ['NB', 'U4OUT', 'LOOP_IN'], 300, 600),                      # signal do 34 V
    ('logika3v3', ['+3V3', 'DVDD'], 200, 150),                        # ulazi u QFN pinove 0,2 mm
]
SNAGA = KLASE[0][1] + KLASE[1][1]
HV_RAZMAK_UM = 600

# Funkcionalni blokovi: komponente po grupi (okvir i naziv na silk sloju)
BLOKOVI = [
    ('1 USB IZOLACIJA', ['J5', 'U8', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R21', 'R22']),
    ('2 ULAZ 24V I ZASTITA', ['J1', 'F1', 'D3']),
    ('3 BOOST 34V', ['U1', 'L1', 'D1', 'C1', 'C3', 'C32', 'C5', 'C63', 'C31', 'R30', 'C30', 'R31', 'R32']),
    ('4 NAPAJANJE 5V/3V3', ['U2', 'C16', 'C10', 'U11', 'C54', 'C55']),
    ('5 MCU RP2040', ['U9', 'U10', 'C53', 'R23', 'R24', 'SW1', 'SW2', 'R25', 'Y1', 'R26', 'C51', 'C52', 'C40', 'C41',
                      'C42', 'C43', 'C44', 'C45', 'C46', 'C47', 'C48', 'C49', 'C56', 'C57', 'J6', 'R27', 'D5']),
    ('6 REFERENCA I NIVO', ['U3', 'C17', 'R3', 'R4', 'C6', 'R5', 'Q2', 'R19', 'Q5', 'R18', 'Q6']),
    ('10 ZASTITA KS >500mA', ['U12', 'C61', 'R33', 'R34', 'R35', 'C62', 'D6', 'R36', 'Q7', 'R37']),
    ('7 DRAJVER PETLJE 34V', ['U4', 'C13', 'C58', 'R6', 'R8', 'C7', 'R9', 'Q3', 'HS1', 'Q4', 'R7']),
    ('8 IZLAZ I ZASTITA', ['F2', 'D2', 'R10', 'R11', 'C59', 'J2']),
    ('9 MERENJE STRUJE', ['R14', 'R15', 'C8', 'U5', 'C14', 'R17', 'R16', 'U6', 'C15', 'R20', 'C9', 'J3', 'R12', 'R13', 'C60']),
]


# Vodovi koje Freerouting sam ne nalazi: VLOOP od delitelja R10/R11 do ADC ulaza RP2040 (pin 39)
# ide donjim slojem preko cele ploče. (mreža, [(sloj, x1, y1, x2, y2, širina)], [via])
PREVODI = [
    ('VLOOP',
     [('F', 143.4375, 170.6, 144.2267, 170.6, 0.2), ('F', 144.2267, 170.6, 144.3959, 170.7692, 0.2),
      ('B', 144.3959, 170.7692, 163.6351, 170.7692, 0.2), ('B', 163.6351, 170.7692, 188.3331, 146.0712, 0.2),
      ('B', 188.3331, 146.0712, 208.8256, 146.0712, 0.2),
      ('F', 208.8256, 146.0712, 208.9843, 145.9125, 0.2), ('F', 208.9843, 145.9125, 210.0, 145.9125, 0.2),
      ('F', 210.0, 145.9125, 210.1375, 145.775, 0.2)],
     [(144.3959, 170.7692), (208.8256, 146.0712)]),
    # SWDIO od RP2040 (pin 25) do SWD konektora J6
    ('SWDIO',
     [('F', 141.4, 175.4375, 141.4, 176.104, 0.2), ('F', 141.4, 176.104, 141.8331, 176.5371, 0.2),
      ('F', 141.8331, 176.5371, 141.8331, 176.9054, 0.2), ('F', 141.8331, 176.9054, 144.1657, 179.238, 0.2),
      ('F', 144.1657, 179.238, 146.2373, 179.238, 0.2), ('F', 146.2373, 179.238, 155.9781, 188.9788, 0.2),
      ('F', 155.9781, 188.9788, 155.9781, 190.0, 0.2), ('F', 155.9781, 190.0, 157.08, 190.0, 0.2)],
     []),
    # +3V3 na IOVDD pin 22 RP2040: kratak vod ispod kućišta do pina 23 (desna strana)
    ('+3V3',
     [('F', 140.2, 175.4375, 140.2, 174.967, 0.2), ('F', 140.2, 174.967, 140.4334, 174.7336, 0.2),
      ('F', 140.4334, 174.7336, 140.8225, 174.7336, 0.2), ('F', 140.8225, 174.7336, 141.9774, 173.5787, 0.2),
      ('F', 141.9774, 173.5787, 141.9774, 173.0, 0.2), ('F', 141.9774, 173.0, 143.4375, 173.0, 0.2)],
     []),
]


def ucitaj(lib, ime):
    fp = pcbnew.FootprintLoad(FP + lib + '.pretty', ime)
    if fp is None:
        raise SystemExit('nema footprinta %s:%s' % (lib, ime))
    return fp


def main():
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
    nets = {}

    def net(ime):
        if ime not in nets:
            n = pcbnew.NETINFO_ITEM(b, ime)
            b.Add(n)
            nets[ime] = n
        return nets[ime]

    def postavi(ref, lib_ime, x, y, rot, val, pinovi):
        fp = ucitaj(*lib_ime)
        fp.SetReference(ref)
        fp.SetValue(val)
        b.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            m = pinovi.get(pad.GetNumber())
            if m:
                pad.SetNet(net(m))
        return fp

    fps = {}
    for ref, (li, _x, _y, _r, val, pins) in P.items():
        x, y, rot = POZ[ref]
        fps[ref] = postavi(ref, li, x, y, rot, val, pins)

    # Boost: SW čvor mora biti što kraći (LM2587 datasheet, "Layout guidelines").
    # Pad prigušnice bliži SW pinu postaje SW, a dioda se okreće anodom ka njemu.
    def pad(fp, n):
        return [p for p in fp.Pads() if p.GetNumber() == n][0]

    def dist(a, c):
        return ((a.GetPosition().x - c.GetPosition().x) ** 2 + (a.GetPosition().y - c.GetPosition().y) ** 2) ** 0.5
    sw_pin = pad(fps['U1'], '4')
    l1a, l1b = pad(fps['L1'], '1'), pad(fps['L1'], '2')
    if dist(l1a, sw_pin) < dist(l1b, sw_pin):
        l1a.SetNet(net('SW')); l1b.SetNet(net('+24V'))
    l_sw = l1a if l1a.GetNetname() == 'SW' else l1b
    d1 = fps['D1']
    if dist(pad(d1, '2'), l_sw) > dist(pad(d1, '1'), l_sw):
        d1.SetOrientationDegrees(d1.GetOrientationDegrees() + 180)

    for i, (x, y) in enumerate([(226, 104), (104, 191), (226, 191), (165, 191)]):
        postavi('H%d' % (i + 1), ('MountingHole', 'MountingHole_3.2mm_M3'), x, y, 0, 'M3', {})

    # ivica ploče 120 x 85
    x0, y0, x1, y1 = 100, 100, 230, 195
    for a, c in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        b.Add(s)

    # natpisi na silk sloju
    for txt, x, y, sz in [('APOLLO XP95 LOOP DRIVER v0.2 - SAMO LABORATORIJA', 195, 193, 1.1),
                          ('24V IN', 106, 148, 1.0), ('LOOP OUT', 219, 111, 1.0), ('LOOP IN', 219, 169, 1.0),
                          ('USB IZOLOVANO', 112, 125.5, 0.9), ('TIP122 + HLADNJAK TV5G, M3', 188.5, 102, 0.8)]:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(txt)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(MM(sz), MM(sz)))
        t.SetTextThickness(MM(sz * 0.15))
        b.Add(t)

    # okviri blokova
    fpd = {f.GetReference(): f for f in b.GetFootprints()}
    for ime, refs in BLOKOVI:
        xs0, ys0, xs1, ys1 = [], [], [], []
        for r in refs:
            c = fpd[r].GetBoundingBox(False, False)
            xs0.append(pcbnew.ToMM(c.GetLeft())); ys0.append(pcbnew.ToMM(c.GetTop()))
            xs1.append(pcbnew.ToMM(c.GetRight())); ys1.append(pcbnew.ToMM(c.GetBottom()))
        x0b, y0b, x1b, y1b = min(xs0) - 0.8, min(ys0) - 0.8, max(xs1) + 0.8, max(ys1) + 0.8
        x0b, y0b, x1b, y1b = max(x0b, 100.6), max(y0b, 100.6), min(x1b, 229.4), min(y1b, 194.4)
        r = pcbnew.PCB_SHAPE(b)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetStart(pcbnew.VECTOR2I(MM(x0b), MM(y0b)))
        r.SetEnd(pcbnew.VECTOR2I(MM(x1b), MM(y1b)))
        r.SetLayer(pcbnew.F_Fab)
        r.SetWidth(MM(0.15))
        b.Add(r)
        t = pcbnew.PCB_TEXT(b)
        t.SetText('BLOK ' + ime)
        t.SetLayer(pcbnew.F_Fab)
        t.SetTextSize(pcbnew.VECTOR2I(MM(0.9), MM(0.9)))
        t.SetTextThickness(MM(0.12))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        t.SetPosition(pcbnew.VECTOR2I(MM(x0b + 0.3), MM(y0b + 0.8)))
        b.Add(t)

    # izolaciona traka ispod ADuM3160: bez vodova, via i bakra
    ka = pcbnew.ZONE(b)
    ka.SetIsRuleArea(True)
    ka.SetDoNotAllowTracks(True)
    ka.SetDoNotAllowVias(True)
    ka.SetDoNotAllowCopperPour(True)
    ka.SetDoNotAllowPads(False)
    ka.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu)
    ka.SetLayerSet(ls)
    o = ka.Outline()
    o.NewOutline()
    for x, y in [(127.6, 100.5), (129.9, 100.5), (129.9, 129.4), (127.6, 129.4)]:
        o.Append(MM(x), MM(y))
    b.Add(ka)

    # donji sloj ispod tab-a LM2587 i centralnog pada RP2040 ostaje za termalne via (bez vodova)
    for ref, pol in (('U1', 5.2), ('U9', 1.9)):
        ep = max((p for p in fpd[ref].Pads() if p.GetNetname() == 'GND'), key=lambda p: p.GetSize().x * p.GetSize().y)
        cx, cy = pcbnew.ToMM(ep.GetPosition().x), pcbnew.ToMM(ep.GetPosition().y)
        kz = pcbnew.ZONE(b)
        kz.SetIsRuleArea(True)
        kz.SetDoNotAllowTracks(True)
        kz.SetDoNotAllowVias(False)
        kz.SetDoNotAllowCopperPour(False)
        kz.SetDoNotAllowPads(False)
        kz.SetDoNotAllowFootprints(False)
        kz.SetLayer(pcbnew.B_Cu)
        o = kz.Outline(); o.NewOutline()
        for x, y in [(cx - pol, cy - pol), (cx + pol, cy - pol), (cx + pol, cy + pol), (cx - pol, cy + pol)]:
            o.Append(MM(x), MM(y))
        b.Add(kz)

    # unapred zadati vodovi (zaključani): Freerouting ih zaobilazi
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

    ds.SetBoardThickness(MM(1.6))
    pcbnew.SaveBoard('apollo_loop_driver.kicad_pcb', b)
    pcbnew.ExportSpecctraDSN(b, 'apollo_loop_driver.dsn')

    # širi vodovi za mreže snage: posebna klasa u DSN fajlu
    t = open('apollo_loop_driver.dsn').read()
    t = postavi_klasu_snage(t)
    open('apollo_loop_driver.dsn', 'w').write(t)
    print('komponenti:', len(b.GetFootprints()), 'mreza:', len(nets))


def postavi_klasu_snage(dsn):
    import re
    m = re.search(r'\(class kicad_default(.*?)\(circuit', dsn, re.S)
    if not m:
        return dsn
    nets = m.group(1)
    sve = [n for _, mr, _, _ in KLASE for n in mr]
    for n in sve:
        nets = re.sub(r'(?<=\s)%s(?=[\s)])' % re.escape(n), '', nets)
    dsn = dsn[:m.start(1)] + nets + dsn[m.end(1):]
    klase = ''
    for ime, mr, w, c in KLASE:
        klase += ('(class %s %s\n      (circuit\n        (use_via Via[0-1]_600:300_um)\n      )\n'
                  '      (rule\n        (width %d)\n        (clearance %d)\n      )\n    )\n    ' % (ime, ' '.join(mr), w, c))
    i = dsn.index('(class kicad_default')
    return dsn[:i] + klase + dsn[i:]


if __name__ == '__main__':
    main()
