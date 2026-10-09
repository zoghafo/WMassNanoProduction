#!/bin/bash

# Source bashrc to load sbw command
source ~/.bashrc

kin_filters=("pt" "mass" "rapidity")
axes=("raw" "quantile" "IP")

vars="PFCands_Ht"
ratio="DYMinBias"
slurm_flag="--slurm"
nthreads="32"

n=${#kin_filters[@]}

# loop over every non-empty subset of kin_filters via bitmask (2^n - 1 subsets)
for (( mask=1; mask<(1<<n); mask++ )); do
    combo=()
    for (( i=0; i<n; i++ )); do
        if (( (mask >> i) & 1 )); then
            combo+=("${kin_filters[i]}")
        fi
    done
cd ...
    (( ${#combo[@]} > 2 )) && continue   # skip the 3-filter combination


    for axis in "${axes[@]}"; do
        echo "Running: kin-filter=${combo[*]}, axis=$axis"

        sbw PlottingSubmission.sh \
            --mode histograms \
            --vars "$vars" \
            --kin-filter "${combo[@]}" \
            --ratio "$ratio" \
            --axis "$axis" \
            "$slurm_flag" \
            --nthreads "$nthreads"
    done
done

# echo "All combinations finished!"