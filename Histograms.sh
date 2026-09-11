#!/bin/bash

# Source bashrc to load sbw command
source ~/.bashrc

kin_filters=("pt" "mass" "rapidity")
axes=("raw" "quantile" "IP")

vars="PFCands_Ht"
ratio="DYMinBias"
slurm_flag="--slurm"
nthreads="32"

for kin_filter in "${kin_filters[@]}"; do
    for axis in "${axes[@]}"; do
        # echo "Running: kin-filter=$kin_filter, axis=$axis"
        
        sbw PlottingSubmission.sh \
            --mode histograms \
            --vars "$vars" \
            --kin-filter "$kin_filter" \
            --ratio "$ratio" \
            --axis "$axis" \
            "$slurm_flag" \
            --nthreads "$nthreads"
        
        # echo "Completed: kin-filter=$kin_filter, axis=$axis"
        # echo "---"
    done
done

# echo "All combinations finished!"