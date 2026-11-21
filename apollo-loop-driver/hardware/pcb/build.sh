#!/bin/bash
# Ceo tok: raspored -> Freerouting -> uvoz vodova + GND povrsine -> DRC -> izlazni fajlovi
set -e
cd "$(dirname "$0")"
FR=${FREEROUTING_JAR:-/tmp/claude-0/fr/fr.jar}
python3.12 make_pcb.py
rm -f apollo_loop_driver.ses
xvfb-run -a java -jar "$FR" -de apollo_loop_driver.dsn -do apollo_loop_driver.ses -mp 120 -mt 1 > freerouting.log 2>&1
python3.12 finish_pcb.py
python3.12 -c "import sys; sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew; b=pcbnew.LoadBoard('apollo_loop_driver.kicad_pcb'); pcbnew.WriteDRCReport(b,'drc.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep -E '^\*\* Found' drc.rpt
