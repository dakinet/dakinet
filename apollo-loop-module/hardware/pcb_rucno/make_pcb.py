"""Pravi KiCad 7 pločicu za Apollo loop driver MODUL v0.1 (76 x 54 mm, 2 sloja) – samo laboratorija.

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
    'U5': (SOT235, 'MCP6561T-E/OT', {'1': 'BIT', '2': 'GND', '3': 'IAMP', '4': 'PRAG_F', '5': '+3V3'}),
    'C21': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'R23': (R0603, '10k', {'1': 'PRAG', '2': 'PRAG_F'}),
    'C22': (C0603, '1u', {'1': 'PRAG_F', '2': 'GND'}),
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
    # ---- RP2040 (isti GPIO kao master; GP0/GP1 = UART0; OC_FLAG je sada OCP)
    'U7': (('Package_DFN_QFN', 'QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm'), 'RP2040',
           {'1': '+3V3', '10': '+3V3', '22': '+3V3', '33': '+3V3', '42': '+3V3', '49': '+3V3',
            '2': 'TX', '3': 'RX', '4': 'NIVO', '5': 'EN_N', '6': 'BIT', '7': 'OC_RST', '8': 'OCP',
            '19': 'GND', '20': 'XIN', '21': 'XOUT', '23': 'DVDD', '50': 'DVDD', '45': 'DVDD',
            '24': 'SWCLK', '25': 'SWDIO', '26': 'RUN', '27': 'PRAG', '37': 'LED', '38': 'IAMP', '39': 'VLOOP',
            '40': 'VRET', '43': '+3V3', '44': '+3V3', '46': 'USB_DM', '47': 'USB_DP', '48': '+3V3',
            '51': 'QSD3', '52': 'QSCLK', '53': 'QSD0', '54': 'QSD2', '55': 'QSD1', '56': 'QSS', '57': 'GND'}),
    'U8': (('Package_SO', SOIC8W), 'W25Q16JVSS',
           {'1': 'QSS', '2': 'QSD1', '3': 'QSD2', '4': 'GND', '5': 'QSD0', '6': 'QSCLK', '7': 'QSD3', '8': '+3V3'}),
    'C25': (C0603, '100n', {'1': '+3V3', '2': 'GND'}),
    'R29': (R0603, '10k', {'1': 'QSS', '2': '+3V3'}),
    'R30': (R0603, '1k', {'1': 'QSS', '2': 'BOOT'}),
    'R31': (R0603, '10k', {'1': 'RUN', '2': '+3V3'}),
    'Y1': (('Crystal', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'), '12MHz ABM8-272-T3', {'1': 'XIN', '2': 'GND', '3': 'XO', '4': 'GND'}),
    'R32': (R0603, '1k', {'1': 'XOUT', '2': 'XO'}),
    'C26': (C0603, '15p', {'1': 'XIN', '2': 'GND'}),
    'C27': (C0603, '15p', {'1': 'XO', '2': 'GND'}),
    'C28': (C0402, '100n', {'1': '+3V3', '2': 'GND'}),       # IOVDD pin 10
    'C29': (C0402, '100n', {'1': '+3V3', '2': 'GND'}),       # IOVDD pin 33
    'C30': (C0402, '100n', {'1': '+3V3', '2': 'GND'}),       # USB_VDD 48 + IOVDD 49
    'C31': (C0402, '100n', {'1': '+3V3', '2': 'GND'}),       # IOVDD pin 1
    'C32': (C0402, '1u', {'1': '+3V3', '2': 'GND'}),         # VREG_VIN pin 44 (datasheet 2.10)
    'C38': (C0402, '100n', {'1': '+3V3', '2': 'GND'}),       # IOVDD pin 42
    'C39': (C0402, '100n', {'1': '+3V3', '2': 'GND'}),       # ADC_AVDD pin 43
    'C40': (C0402, '100n', {'1': '+3V3', '2': 'GND'}),       # IOVDD pin 22
    'C33': (C0402, '100n', {'1': 'DVDD', '2': 'GND'}),       # DVDD pin 50
    'C41': (C0402, '100n', {'1': 'DVDD', '2': 'GND'}),       # DVDD pin 23
    'C34': (C0402, '1u', {'1': 'DVDD', '2': 'GND'}),         # VREG_VOUT pin 45, tik uz pin
    'R33': (R0603, '27', {'1': 'USB_DP', '2': 'DP_H'}),
    'R34': (R0603, '27', {'1': 'USB_DM', '2': 'DM_H'}),
    'R35': (R0603, '1k', {'1': 'LED', '2': 'LED_A'}),
    'D5': (('LED_SMD', 'LED_0603_1608Metric'), 'LED', {'1': 'GND', '2': 'LED_A'}),
    # ---- J1: letvica 2x14 / 2,54 mm sa DONJE strane – modul se utiče u matičnu ploču (sve spoljne veze)
    #  pinovi (neparni red / parni red), s leva na desno, prate blokove iznad letvice:
    #  24V x2 (ulaz F1/D1) | GND x2 | 3V3,GND | TX,RX | RUN,BOOT | D+,D- | SWCLK,SWDIO (MCU) |
    #  GND | ISENSE (ispod šanta R19) | LOOP_IN | LOOP_OUT (uz TVS D3) | GND
    'J1': (('Connector_PinHeader_2.54mm', 'PinHeader_2x14_P2.54mm_Vertical'), 'MATICNA 2x14',
           {'1': '+24V_IN', '2': '+24V_IN', '3': '+24V_IN', '4': '+24V_IN', '5': 'GND', '6': 'GND', '7': 'GND', '8': 'GND',
            '9': '+3V3', '10': 'GND', '11': 'TX', '12': 'RX', '13': 'RUN', '14': 'BOOT', '15': 'DP_H', '16': 'DM_H',
            '17': 'SWCLK', '18': 'SWDIO', '19': 'GND', '20': 'GND', '21': 'ISENSE', '22': 'ISENSE',
            '23': 'LOOP_IN', '24': 'LOOP_IN', '25': 'LOOP_OUT', '26': 'LOOP_OUT', '27': 'GND', '28': 'GND'}),
}

# delovi sa donje strane (B.Cu); ostali su gore
DOLE = {'J1'}

POZ = {
    # ulaz i boost (gore)
    'F1': (118, 151.2, 90), 'D1': (112.5, 151.75, 0), 'C1': (105.2, 104, 180), 'C2': (117.3, 103.35, 90),
    'U1': (121, 110.6, 270), 'L1': (122.5, 103.35, 0), 'D2': (125.6, 110.6, 90), 'C3': (124.1, 117.85, 180), 'C4': (128.8, 117.85, 180),
    'C5': (132.7, 110.2, 0), 'C9': (115.7, 108.3, 270), 'R1': (118.3, 117.8, 180), 'R2': (118.3, 116.2, 0), 'R3': (120.6, 116.6, 270),
    'R4': (115.2, 116.2, 0), 'C6': (115.2, 119.4, 0), 'C7': (115.2, 117.8, 0), 'C8': (117.4, 111.35, 90),
    # buck 3V3 (levo)
    'U2': (104, 124, 0), 'C10': (104, 121.45, 0), 'L2': (108.7, 123.3, 0), 'C11': (104, 129.05, 180), 'C12': (112.55, 123.3, 90),
    'C13': (114.65, 123.3, 90),
    # VSET
    'R5': (128.55, 124.8, 0), 'R6': (128.55, 126.4, 0), 'C14': (131.6, 124.2, 0), 'R7': (131.6, 125.8, 0), 'Q2': (135.6, 127.6, 0),
    'R8': (131.6, 127.4, 0), 'Q3': (137.15, 122, 0), 'R9': (135.6, 124.8, 0),
    # izlazni stepen
    'U3': (151, 117.4, 0), 'C15': (145.7, 115.45, 0), 'R10': (155.6, 121.6, 0), 'R11': (151, 121.6, 0), 'C16': (151, 123.4, 0),
    'R12': (147, 121.6, 0), 'Q1': (164, 106, 0), 'R13': (163, 112.8, 0), 'Q4': (158, 116.6, 0), 'Q5': (163, 117.4, 0),
    'R14': (166.8, 117.4, 90),
    # petlja
    'F2': (166.8, 125, 270), 'D3': (160, 146, 0), 'R15': (157.6, 125.6, 90), 'R16': (157.6, 129.6, 90), 'C17': (155.7, 127.9, 90),  'R17': (168.8, 131.6, 90), 'R18': (168.8, 134.8, 90), 'C18': (168.8, 138, 90),
    # merenje i zaštita
    'R19': (149, 142.95, 0), 'R20': (145, 139.6, 0), 'C19': (140.6, 138.55, 0), 'U4': (146.1, 132, 0), 'C20': (140.3, 128.2, 0),
    'R21': (150.65, 136, 90), 'R22': (150.65, 139.05, 90), 'U5': (136.9, 136, 0), 'C21': (137, 133.4, 0), 'R23': (137, 138.6, 0),
    'C22': (137, 140.2, 0), 'U6': (131.6, 136, 0), 'C23': (131.6, 133.4, 0), 'R24': (131.6, 138.6, 0), 'R25': (133.25, 140.2, 0),
    'R26': (127.95, 135.1, 0), 'C24': (127.6, 131.1, 0), 'D4': (140.45, 140.45, 0), 'R27': (141.2, 142.6, 0), 'Q6': (140.44, 132.25, 90),
    'Q7': (142.6, 146.7, 0), 'R28': (133.4, 143, 0),
    # RP2040
    'U7': (117, 137, 90), 'U8': (108, 142.75, 90), 'C25': (106.1, 136.5, 90), 'R29': (103.6, 145.2, 270), 'R30': (103.6, 148.6, 270),
    'R31': (126.35, 141.75, 0), 'Y1': (124.8, 138.8, 0), 'R32': (124.4, 135.95, 0), 'C26': (123.7, 142.3, 270), 'C27': (127.8, 138.8, 270),
    'C28': (118.7, 142.25, 270), 'C29': (118, 131.85, 90), 'C30': (111.4, 136.6, 180), 'C31': (113.4, 142.25, 270), 'C32': (111.95, 131.85, 90),
    'C33': (122, 142.1, 270), 'C34': (111.3, 134.7, 180),
    'R33': (105.5, 131.6, 0), 'R34': (108.6, 131.6, 0), 'R35': (101.9, 141.85, 90), 'D5': (103.45, 142, 90),
    'C36': (124.1, 115.35, 180),
    'C35': (117.4, 108.3, 270),
    'C37': (104, 126.55, 180),
    'C38': (114.4, 131.85, 90),
    'C39': (113.2, 131.85, 90),
    'C40': (119.2, 131.85, 90),
    'C41': (120.8, 142.15, 270),
    # letvica 2x14 (donja strana), simetrično na sredini donje ivice: pinovi x 113,49..146,51; neparni red y=140,6
    'J1': (121.49, 149.6, 90),
}

KLASE = [
    ('boost', ['+24V_IN', 'VIN_F', 'SW'], 800, 300),
    ('vin', ['VIN'], 600, 200),                 # VIN ide i do SOT-23-6 pinova buck-a (korak 0,95 mm)
    ('buck', ['SW3'], 500, 250),
    ('petlja', ['+34V', 'NE', 'LOOP_DRV', 'LOOP_OUT', 'ISENSE', 'LOOP_IN', 'PE'], 600, 300),
    ('hv', ['NB', 'U3OUT'], 300, 300),
    ('logika3v3', ['+3V3'], 250, 150),          # RP2040 QFN korak 0,4 mm
    ('jezgro', ['DVDD'], 200, 150),             # 1,1 V jezgro RP2040, <= 40 mA – 0,2 mm dovoljno, mora oko tela čipa
]

BLOKOVI = [
    ('1 ULAZ 24V', ['F1', 'D1']),
    ('2 BOOST 34V', ['C1', 'C2', 'U1', 'L1', 'D2', 'C3', 'C4', 'C5', 'R1', 'R2', 'R3', 'R4', 'C6', 'C7', 'C8', 'C9', 'C35', 'C36']),
    ('3 BUCK 3V3', ['U2', 'C10', 'L2', 'C11', 'C12', 'C13', 'C37']),
    ('4 VSET', ['R5', 'R6', 'C14', 'R7', 'Q2', 'R8', 'Q3', 'R9']),
    ('5 IZLAZ 24/31V', ['U3', 'C15', 'R10', 'R11', 'C16', 'R12', 'Q1', 'R13', 'Q4', 'Q5', 'R14']),
    ('6 PETLJA', ['F2', 'R15', 'R16', 'C17', 'R17', 'R18', 'C18']),
    ('7 MERENJE I ZASTITA', ['R19', 'R20', 'C19', 'U4', 'C20', 'R21', 'R22', 'U5', 'C21', 'R23', 'C22',
                             'U6', 'C23', 'R24', 'R25', 'R26', 'C24', 'D4', 'R27', 'Q6', 'Q7', 'R28']),
    ('8 RP2040', ['U7', 'U8', 'C25', 'R29', 'R30', 'R31', 'Y1', 'R32', 'C26', 'C27', 'C28', 'C29', 'C30',
                  'C31', 'C32', 'C33', 'C34', 'C38', 'C39', 'C40', 'C41', 'R33', 'R34', 'R35', 'D5']),
    ('9 LETVICA 2x14 (DOLE)', ['J1', 'D3']),
]

# Ručno nacrtani strujni putevi prekidačkih napajanja (TI SLVSBD4E §10, SLVSE22B §11): najkraće i najšire moguće,
# zaključani; Freerouting ih zadržava i rutira samo ostatak.  (mreža, [(sloj, x1, y1, x2, y2, širina)], [via])
PREVODI = [
    # boost SW čvor: SW pinovi 1,2 (gore desno na U1) -> L1 pad 2 -> anoda D2; petlja što manja (SW max 40 V!)
    ('SW', [('F', 122.3, 107.6, 122.3, 106.2, 0.4), ('F', 122.95, 107.6, 122.95, 106.2, 0.4),
            ('F', 122.3, 106.2, 124.6, 106.2, 0.8), ('F', 124.6, 106.2, 125.6, 106.2, 1.0),
            ('F', 125.6, 106.2, 125.6, 108, 1.2)], []),
    # VIN: C2 -> L1 pad 1 -> U1 VIN (3) i EN (4); C9/C35 uz VIN pin; ulaz od D1
    ('VIN', [('F', 118, 104.8, 120, 104.8, 1.0), ('F', 121, 107.6, 121, 105.5, 0.4),
             ('F', 121, 107.2, 121.65, 107.2, 0.35), ('F', 115.7, 107.5, 117.4, 107.5, 0.6),
             ('F', 117.4, 107.5, 118.3, 106.3, 0.5), ('F', 118.3, 106.3, 119.6, 105.6, 0.5),
             ('F', 109.2, 104, 115.7, 107.5, 0.8),   # C1 (47u, gore levo) -> C9/C35 -> L1
             # buck VIN: pinovi 4,5 -> C37 (100n) -> C11 (10u)
             ('F', 105.3, 124, 105.3, 126.5, 0.6), ('F', 105.3, 126.5, 105.5, 128.5, 0.6)], []),
    # +34V: katoda D2 -> C36 -> C3; katoda -> C5 -> C4
    ('+34V', [('F', 125.6, 113.5, 125.6, 117, 1.2), ('F', 126.2, 112, 128.2, 110.6, 1.0),
              ('F', 130.3, 111.2, 130.3, 117, 1.0)], []),
    # PGND: pinovi 11-14 -> masa C36 i C3 (zatvara izlaznu petlju), via na donju masu
    ('GND', [('F', 121, 114, 122.95, 114, 0.35), ('F', 122.3, 114, 122.6, 117.8, 0.6),
             # buck GND pin 2 -> C37 i C11 (oko FB pina sa leve strane)
             ('F', 102.4, 124, 101.4, 124, 0.5), ('F', 101.4, 124, 101.4, 128.5, 0.5),
             ('F', 101.4, 126.55, 103.2, 126.55, 0.5), ('F', 101.4, 128.5, 102.5, 128.5, 0.5)],
     [(121.4, 115), (122.6, 119.8), (101.4, 125.3),
      # termalne via u PowerPAD-u U1 (TI: thermal vias do donje mase)
      (119.4, 109.8), (121, 109.8), (122.6, 109.8), (119.4, 111.4), (121, 111.4), (122.6, 111.4),
      # masa šanta R19 i TVS D3 direktno na donju GND površinu
      (148.96, 136.6), (162.15, 148.4)]),
    # ulaz: F1 -> D1 (24 V dolazi sa letvice J1 dole)
    # buck: SW pin 6 -> L2, C10 (CB) na SW i na CB pin 1
    ('SW3', [('F', 105.4, 123.05, 107, 123.05, 0.6), ('F', 104.8, 121.6, 105.2, 122.9, 0.4)], []),
    ('CB', [('F', 103.2, 121.5, 103, 123, 0.4)], []),
    # ---- ulaz (dobra praksa: zaštita odmah na konektoru): 24V pinovi 1-4 -> F1 -> D1 (obrnuti polaritet)
    ('+24V_IN', [('F', 121.49, 149.6, 121.49, 152.14, 1.0), ('F', 121.49, 152.14, 124.03, 152.14, 1.0),
                 ('F', 124.03, 149.6, 124.03, 152.14, 1.0), ('F', 118, 152.6, 121.49, 152.14, 1.0)], []),
    ('VIN_F', [('F', 118, 149.8, 114.6, 151.6, 1.0)], []),
    # ---- izlazni stepen: emiter Q1 -> R13 (široko); Q4 meri pad na R13 posebnim (Kelvin) vodom sa pada
    ('NE', [('F', 158.96, 108.28, 160.04, 111.5, 0.8), ('F', 157.4, 115.65, 159.8, 114.2, 0.3)], []),
    # ---- petlja: R13 -> PTC F2 -> TVS D3 (uz konektor) -> LOOP_OUT pinovi 25/26
    ('LOOP_DRV', [('F', 165.96, 114, 165.45, 114.9, 0.7), ('F', 165.45, 114.9, 165.45, 121, 0.7),
                  ('F', 165.45, 116.57, 166.6, 116.57, 0.5)], []),
    ('LOOP_OUT', [('F', 157.85, 146, 152.4, 146, 0.8),
                  ('F', 152.4, 146, 152.4, 149.6, 0.8)], []),
    # ---- merenje: ISENSE pinovi 21/22 -> šant R19; R20 uzima napon direktno sa pada šanta (Kelvin)
    ('ISENSE', [('F', 146.89, 149.6, 146.04, 144, 1.0), ('F', 144.2, 139.6, 145.8, 141.6, 0.25)], []),
]
X0, Y0, X1, Y1 = 100, 100, 176, 154

# Dobra praksa za prekidačka napajanja: donja GND površina ispod konvertera ostaje neprekinuta
# (povratna struja prekidačke petlje teče odmah ispod nje). Na B.Cu tu nisu dozvoljeni vodovi; via za masu jesu.
MASA_B = [
    ('boost', (120.8, 100.4, 130.5, 119.5)),   # SW petlja: U1 desno od VIN pinova, L1, D2, C3/C36 (analogna leva polovina slobodna)
    ('buck', (101.0, 120.5, 116.0, 131.0)),    # U2, L2, C10, C11, C37, C12/C13
]


try:                                   # ručno nacrtani vodovi (pcb_rucno)
    from rucni_vodovi import RUCNI
    PREVODI = PREVODI + RUCNI
except ImportError:
    pass


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
    for txt, x, y, sz in [('APOLLO LOOP DRIVER MODUL v0.1 - SAMO LAB', 138, 104, 1.0),
                          ('J1 2x14 (dole): 24V GND 3V3 TX RX RUN BOOT D+ D- SWD GND ISENSE LOOP_IN LOOP_OUT GND', 138, 107, 0.7)]:
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
    # ispod tela QFN-a (RP2040) između pinova i PowerPAD-a: bez vodova i via na F.Cu – 4 trake oko PowerPAD-a
    for ref in ('U7',):
        ux, uy = POZ[ref][:2]
        a, e = 3.0, 1.65            # unutrašnji kraj pinova, ivica PowerPAD-a (mm od centra)
        for ime_t, (x0, y0, x1, y1) in (('gore', (-a, -a, a, -e)), ('dole', (-a, e, a, a)),
                                        ('levo', (-a, -e, -e, e)), ('desno', (e, -e, a, e))):
            kz = pcbnew.ZONE(b)
            kz.SetIsRuleArea(True); kz.SetDoNotAllowTracks(True); kz.SetDoNotAllowVias(True)
            (kz.SetDoNotAllowCopperPour if hasattr(kz, 'SetDoNotAllowCopperPour') else kz.SetDoNotAllowZoneFills)(False)
            kz.SetDoNotAllowPads(False); kz.SetDoNotAllowFootprints(False)
            kz.SetZoneName('ispod tela %s %s' % (ref, ime_t))
            ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); kz.SetLayerSet(ls)
            o = kz.Outline(); o.NewOutline()
            for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
                o.Append(MM(ux + x), MM(uy + y))
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
