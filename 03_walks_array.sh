#!/bin/bash

for nwalks in 5 10 20 30 40 50 60 70 80
do
    for walklen in 25 50 75 100 125 150 175 200
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
