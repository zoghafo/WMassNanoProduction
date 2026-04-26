#!/bin/bash

set -e
set -x

TRIGGER=$1
NEVENTS=$2
SKIP=$3

echo "Trigger: $TRIGGER"
echo "NEvents: $NEVENTS"
echo "SkipEvents: $SKIP"

# cd /home/z/zoghafoo/
source /cvmfs/cms.cern.ch/cmsset_default.sh
# cmssw-cc7
# cd CMSSW_10_6_26/src
eval `scramv1 runtime -sh`
cmsenv
# cd Configuration/WMassNanoProduction/configs

cmsRun NanoV9DataPostVFP_cfg.py $TRIGGER $NEVENTS $SKIP

echo "Job finished successfully."