#!/bin/bash

for i in {1..100}
do	
	graph_file="data/random_graphs/random_ontograph_${i}.pkl"
	embedfile="data/embeddings/random_ontograph_embed_${i}.model"
	sbatch src/scripts/submit_random_clusters.sh $graph_file $embedfile

done
