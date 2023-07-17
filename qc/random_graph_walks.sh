#!/bin/bash

for i in {1..100}
do
    
    graph_file="/home/binderjl/RD-Clust/data/processed/disease_ontograph.pkl"
    walk_file="data/walks/random_graph_walks_${i}.txt"

    sbatch --job-name random_graph_walks_${i} \
        src/scripts/submit_random_graph_walks.sh \
        ${graph_file} \
        ${walk_file} \
        250 \
        250 
        
done
        
