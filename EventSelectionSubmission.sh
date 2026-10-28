#!/bin/bash
#SBATCH --job-name=EventSelection
#SBATCH -p long
#SBATCH --account=t3
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=8gb
#SBATCH --time=23:00:00
#SBATCH --output=slurm_log/%x_%j.out
#SBATCH --error=slurm_log/%x_%j.err

set -x

start_time=$(date +%s)

if ! voms-proxy-info --exists --valid 24:00; then
  echo "Grid proxy missing or valid for less than 24h, run voms-proxy-init --voms cms --valid 192:00"
  exit 1
fi

source_dir=/scratch/$USER/$SLURM_JOB_ID
DESTDIR=/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/selEvents_new
DATASET="$1"
OUTPUTSUFFIX="$2"
# MAXEVENTS="$3"
NTHREADS="$3"

mkdir -p "$source_dir"

echo "Before starting the python:"
echo "Dataset: "$DATASET
echo "Output suffix: "$OUTPUTSUFFIX
echo "Number of threads: "$NTHREADS
# echo "Max events: "$MAXEVENTS

python3 NanoAOD_EventSelection.py \
  --dataset "$DATASET" \
  --output-dir "$source_dir" \
  --output-suffix "$OUTPUTSUFFIX" \
  --nthreads "$NTHREADS"
  # --maxevents $MAXEVENTS
status=$?
if [ $status -ne 0 ]; then
  echo "Python script failed with exit code $status, not copying output"
  rm -rf "$source_dir"
  exit $status
fi

echo "Finished the python script"
echo "voms proxy info:"
voms-proxy-info --all
echo "Time left on proxy:"
voms-proxy-info --timeleft
echo "------------------"
echo "Going to copy"
echo "From "$source_dir"/"$DATASET"_SelectedEvents_$OUTPUTSUFFIX.root"
echo "To root://t3dcachedb03.psi.ch:1094//"$DESTDIR

echo "Analyze scratch"
ls -l "$source_dir"
cd /scratch
pwd
ls

if xrdcp -f -N "$source_dir/${DATASET}_SelectedEvents_${OUTPUTSUFFIX}.root" root://t3dcachedb03.psi.ch:1094//$DESTDIR && \
   xrdcp -f -N "$source_dir/${DATASET}_TotalEvents_${OUTPUTSUFFIX}.txt" root://t3dcachedb03.psi.ch:1094//$DESTDIR; then
  rm -rf "$source_dir"
else
  echo "Copy failed, output kept in $source_dir on $(hostname)"
  exit 1
fi


end_time=$(date +%s)
elapsed=$((end_time - start_time))

printf "Job finished in %02d:%02d:%02d (hh:mm:ss)\n" $((elapsed/3600)) $(( (elapsed%3600)/60 )) $((elapsed%60))