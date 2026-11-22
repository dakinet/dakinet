#!/bin/bash
# Ceo tok: raspored -> Freerouting -> uvoz vodova + GND povrsine -> DRC
set -e
cd "$(dirname "$0")"
FR=${FREEROUTING_JAR:-/tmp/claude-0/fr/fr.jar}
python3.12 make_pcb.py
rm -f loopnet_1in.ses
xvfb-run -a java -jar "$FR" -de loopnet_1in.dsn -do loopnet_1in.ses -mp 100 -mt 1 > logs/freerouting.log 2>&1
python3.12 finish_pcb.py
python3.12 -c "import sys; sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew; b=pcbnew.LoadBoard('loopnet_1in.kicad_pcb'); pcbnew.WriteDRCReport(b,'drc.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep -E '^\*\* Found' drc.rpt
