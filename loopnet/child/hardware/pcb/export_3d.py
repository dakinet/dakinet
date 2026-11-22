"""3D izvoz pločice (VRML sa modelima) za pregled: python3.12 export_3d.py [izlaz.wrl]
Treba paket kicad-packages3d. Za dva otiska KiCad 7 nema model, pa se uzima najbliži:
  U2 VQFN-20 3x3: nema modela (zamenski UQFN izvoz preskače) -> izostavljen; 3D stranica crta telo 3 x 3 x 0,9 mm
  SW1 TS-1187A: nema modela -> izostavljen; 3D stranica ga crta kao kvadar 5,1 x 5,1 mm"""
import os
import sys
sys.path.append('/usr/lib/python3/dist-packages')
D = '/usr/share/kicad/3dmodels'
for v in ('KICAD6_3DMODEL_DIR', 'KICAD7_3DMODEL_DIR'):
    os.environ[v] = D
import pcbnew

ZAMENE = {
}
izlaz = sys.argv[1] if len(sys.argv) > 1 else 'loopnet_1in.wrl'
b = pcbnew.LoadBoard(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loopnet_1in.kicad_pcb'))
for f in b.GetFootprints():
    if f.GetReference() in ('SW1', 'U2'):
        f.Models().clear()
    for m in f.Models():
        if f.GetReference() in ZAMENE:
            m.m_Filename = ZAMENE[f.GetReference()]
        else:
            m.m_Filename = m.m_Filename.replace('${KICAD6_3DMODEL_DIR}', D).replace('${KICAD7_3DMODEL_DIR}', D)
        if not os.path.exists(m.m_Filename):
            print('NEMA MODELA:', f.GetReference(), m.m_Filename)
# ishodište u gornjem levom uglu ploče (100, 100); jedinica 1 mm
exp = pcbnew.EXPORTER_VRML(b)
poruke = pcbnew.wxString()
ok = exp.ExportVRML_File(b.GetProject(), poruke, izlaz, 1.0, False, False, '', 100.0, 100.0)
print('izvoz:', ok, izlaz, os.path.getsize(izlaz) if os.path.exists(izlaz) else 0, str(poruke)[:300])
