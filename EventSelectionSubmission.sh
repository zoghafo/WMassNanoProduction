#!/bin/bash
#SBATCH --job-name=EventSelection
#SBATCH -p long
#SBATCH --account=t3
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=8gb
#SBATCH --time=23:00:00
#SBATCH --output=slurm_log/%x_%j.out
#SBATCH --error=slurm_log/%x_%j.err

set -x

start_time=$(date +%s)

source_dir="/scratch/zoghafoo"
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

echo "Going to copy"
echo "From "$source_dir"/"$DATASET"_SelectedEvents_$OUTPUTSUFFIX.root"
echo "To root://t3dcachedb03.psi.ch:1094//"$DESTDIR

echo "Analyze scratch"
cd /scratch
pwd
ls
xrdcp -f -N $source_dir/$DATASET"_SelectedEvents_$OUTPUTSUFFIX.root" root://t3dcachedb03.psi.ch:1094//$DESTDIR
xrdcp -f -N $source_dir/$DATASET"_TotalEvents_$OUTPUTSUFFIX.txt" root://t3dcachedb03.psi.ch:1094//$DESTDIR

rm $source_dir/$DATASET"_SelectedEvents_$OUTPUTSUFFIX.root"
rm $source_dir/$DATASET"_TotalEvents_$OUTPUTSUFFIX.txt"

end_time=$(date +%s)
elapsed=$((end_time - start_time))

printf "Job finished in %02d:%02d:%02d (hh:mm:ss)\n" $((elapsed/3600)) $(( (elapsed%3600)/60 )) $((elapsed%60))