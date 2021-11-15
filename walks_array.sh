#!/bin/bash

for nwalks in 5 10 20 30 40 50
do
    for walklen in 50 75 100 125 150
    do
        sbatch --job-name random_walks_N${nwalks}_L${walklen} \
	submit_walks.sh \
        $nwalks \
	$walklen
	 
    done
done
