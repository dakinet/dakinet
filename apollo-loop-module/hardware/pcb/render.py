"""Crta gotovu ploču (pad-ovi, vodovi F/B, via) u PNG za brzi pregled: python3.12 render.py [ulaz] [izlaz.png]"""
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ul = sys.argv[1] if len(sys.argv) > 1 else 'apollo_module.kicad_pcb'
iz = sys.argv[2] if len(sys.argv) > 2 else 'pregled.png'
b = pcbnew.LoadBoard(ul)
T = pcbnew.ToMM
fig, ax = plt.subplots(figsize=(14, 10))
for t in b.GetTracks():
    if t.GetClass() == 'PCB_TRACK':
        c = 'red' if t.GetLayer() == pcbnew.F_Cu else 'blue'
        ax.plot([T(t.GetStart().x), T(t.GetEnd().x)], [T(t.GetStart().y), T(t.GetEnd().y)], color=c,
                lw=T(t.GetWidth()) * 28, alpha=0.55, solid_capstyle='round')
for f in b.GetFootprints():
    for pd in f.Pads():
        bb = pd.GetBoundingBox()
        ax.add_patch(plt.Rectangle((T(bb.GetLeft()), T(bb.GetTop())), T(bb.GetWidth()), T(bb.GetHeight()),
                                   color='goldenrod', alpha=0.7))
        q = pd.GetPosition()
        ax.text(T(q.x), T(q.y), pd.GetNetname()[:7], fontsize=5, ha='center', va='center')
    p = f.GetPosition()
    ax.text(T(p.x), T(p.y) - 0.5, f.GetReference(), fontsize=8, color='k', ha='center', weight='bold')
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        try:
            d = t.GetWidth(pcbnew.F_Cu)          # KiCad 9/10: širina via po sloju
        except TypeError:
            d = t.GetWidth()                     # KiCad 7
        ax.add_patch(plt.Circle((T(t.GetPosition().x), T(t.GetPosition().y)), T(d) / 2, color='green', alpha=0.8))
bb = b.GetBoardEdgesBoundingBox()
ax.add_patch(plt.Rectangle((T(bb.GetLeft()), T(bb.GetTop())), T(bb.GetWidth()), T(bb.GetHeight()), fill=False, lw=1.5))
ax.set_xlim(T(bb.GetLeft()) - 1, T(bb.GetRight()) + 1); ax.set_ylim(T(bb.GetBottom()) + 1, T(bb.GetTop()) - 1)
ax.set_aspect('equal'); ax.set_title('crveno = F.Cu, plavo = B.Cu, zeleno = via')
fig.savefig(iz, dpi=100, bbox_inches='tight')
