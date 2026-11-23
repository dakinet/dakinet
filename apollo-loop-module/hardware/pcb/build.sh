#!/bin/bash
# Ceo tok: raspored -> Freerouting -> uvoz vodova + GND povrsine -> DRC
# Radi na Linux-u (KiCad 7, python3.12, xvfb) i na Windows-u / Git Bash (KiCad 10):
#   PY=".../KiCad/10.0/bin/python.exe" JAVA=".../jre17/bin/java.exe" FREEROUTING_JAR=".../freerouting-1.9.0.jar" ./build.sh
# Freerouting 1.9.0 traži Javu 17+.
set -e
cd "$(dirname "$0")"
PY=${PY:-python3.12}
JAVA=${JAVA:-java}
FR=${FREEROUTING_JAR:-/tmp/claude-0/fr/fr.jar}
CLI=${KICAD_CLI:-kicad-cli}
"$PY" make_pcb.py
rm -f apollo_module.ses
XV=""; command -v xvfb-run >/dev/null 2>&1 && XV="xvfb-run -a"
$XV "$JAVA" -jar "$FR" -de apollo_module.dsn -do apollo_module.ses -mp 100 -mt 1 > logs/freerouting.log 2>&1
"$PY" finish_pcb.py
"$CLI" pcb drc --severity-all --refill-zones -o drc.rpt apollo_module.kicad_pcb
grep -E 'Found|violations|unconnected|Unconnected' drc.rpt
