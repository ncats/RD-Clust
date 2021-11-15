#!/bin/bash

for nwalks in {10..50..5}
do
    for walklen in {50..200..10}
    do
        sbatch --job-name random_walks_N${nwalks}_L${walklen} \
	submit_walks.sh \
        $nwalks \
	$walklen
	 
    done
done
