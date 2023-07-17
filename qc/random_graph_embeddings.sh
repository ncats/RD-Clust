#!/bin/bash

for i in {1..100}
do
    
    walk_file="data/walks/random_graph_walks_${i}.txt"
    embedfile="data/embeddings/random_ontograph_embed_${i}.model"

    sbatch --job-name random_vector_embeddings_${i} src/scripts/submit_random_embeddings.sh $walk_file 32 12 $embedfile
				   
done
