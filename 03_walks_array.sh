#!/bin/bash

for nwalks in 80 100 120
do
    for walklen in 25 50 75 100
    do
        wfile="data/walks/walks_N${nwalks}_L${walklen}.txt"
        if [ ! -f "$wfile" ]; then
            echo $wfile
            sbatch --job-name random_walks_N${nwalks}_L${walklen} \
                submit_walks.sh \
                $nwalks \
                $walklen
        fi 
    done
done
