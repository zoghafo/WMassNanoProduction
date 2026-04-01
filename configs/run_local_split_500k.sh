#!/bin/bash

set -euo pipefail

TRIGGER="${1:-SingleMuon}"
EVENTS_PER_JOB=100000
N_SPLITS=5

for ((i=0; i<N_SPLITS; i++)); do
    SKIP=$((i * EVENTS_PER_JOB))
    echo "Running split $((i+1))/${N_SPLITS}: trigger=${TRIGGER}, events=${EVENTS_PER_JOB}, skip=${SKIP}"
    cmsRun configs/NanoV9DataPostVFP_cfg.py "${TRIGGER}" "${EVENTS_PER_JOB}" "${SKIP}"
done

echo "All splits finished."
