#!/bin/bash

k=${1:-1}   # max number of kin filters per combination, from the command line (default 1)

# Source bashrc to load sbw command
source ~/.bashrc

kin_filters=("pt" "mass" "rapidity" "Ht")
# axes=("raw" "quantile" "IP")
axes="raw"

# vars=("PFCands_Ht" "PFCands_InvariantMass" "nPFCands" "PFCands_Pt2sum" "PFCands_P2sum")
# ratio="DYMinBias"
vars=("DiMuon_Mass" "DiMuon_Pt")
ratio="DataMC"
slurm_flag="--slurm"
nthreads="32"

n=${#kin_filters[@]}

# loop over every subset of kin_filters via bitmask (2^n subsets, mask=0 = no filter)
for (( mask=0; mask<(1<<n); mask++ )); do
    combo=()
    for (( i=0; i<n; i++ )); do
        if (( (mask >> i) & 1 )); then
            combo+=("${kin_filters[i]}")
        fi
    done
    (( ${#combo[@]} > k )) && continue   # skip the k-filter combination

    # only pass --kin-filter when there is at least one filter
    kf_args=()
    (( ${#combo[@]} > 0 )) && kf_args=(--kin-filter "${combo[@]}")

    for axis in "${axes[@]}"; do
        echo "Running: kin-filter=${combo[*]}, axis=$axis"

        sbw PlottingSubmission.sh \
            --mode histograms \
            --vars "${vars[@]}" \
            "${kf_args[@]}" \
            --ratio "$ratio" \
            --axis "$axis" \
            --output-suffix _LogY \
            "$slurm_flag" \
            --nthreads "$nthreads"
    done
done

# echo "All combinations finished!"