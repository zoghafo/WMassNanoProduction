#!/bin/bash
#SBATCH --job-name=Plotting
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

DIRECTORY=/t3home/zoghafoo/WMassNanoProduction
source_dir="/scratch/zoghafoo"
PNFS_DESTDIR=/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/selEvents

mkdir -p "$source_dir"
mkdir -p "$source_dir/tmp"

cd $DIRECTORY
pwd
echo "Plotting..."

# python3 NanoAOD_Plotting.py --mode compare --nthreads 32 --slurm True

# python3 NanoAOD_Plotting.py --mode quantile-ptscan --nthreads 32 --slurm True --quantile-bins 0 0.02 0.04 0.06 0.08 0.1 0.12 0.14 0.16 0.18 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.6 0.7 0.8 0.9 1

python3 NanoAOD_Plotting.py "$@"

# python3 NanoAOD_Plotting.py --mode ptscan-quantilebinning --quantile-bins 0 0.02 0.04 0.06 0.08 0.1 0.12 0.14 0.16 0.18 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.6 0.7 0.8 0.9 1 --zoomxmax 100 --vars PFCands_Ht --pt-cuts 1 2 --nthreads 32 --slurm True

# python3 NanoAOD_Plotting.py --mode ptscan-quantilebinning --quantile-bins 0 0.02 0.04 0.06 0.08 0.1 0.12 0.14 0.16 0.18 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.6 0.7 0.8 0.9 1 --zoomxmax 70 --vars PFCands_Ht --pt-cuts 1 --quantile-reference Data --nthreads 32

# python3 NanoAOD_Plotting.py --mode ptscan-quantilebinning --quantile-bins 0 0.02 0.04 0.06 0.08 0.1 0.12 0.14 0.16 0.18 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.6 0.7 0.8 0.9 1 --zoomxmax 70 --vars PFCands_Ht --pt-cuts 1 --quantile-reference MC --nthreads 32

echo "Saving the plots in "$DIRECTORY

echo "Analyze scratch:"
cd $source_dir
pwd
ls
xrdcp -f -N $source_dir/*.txt root://t3dcachedb03.psi.ch:1094//$PNFS_DESTDIR/

rm -r $source_dir

end_time=$(date +%s)
elapsed=$((end_time - start_time))

printf "Job finished in %02d:%02d:%02d (hh:mm:ss)\n" $((elapsed/3600)) $(( (elapsed%3600)/60 )) $((elapsed%60))