#!/bin/bash

for nwalks in 10 20
do
    for walklen in 50 100
    do
        sbatch --job-name random_walks_N${nwalks}_L${walklen} \
        submit_walks.sh \
        $nwalks \
        $walklen
    done
done