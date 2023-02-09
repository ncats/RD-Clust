#!/bin/bash

for vector_size in 32
do
	for context_window in 6 8 10 12 14 16 18 20
	do

		for nwalks in 5 10 25 50 75 100 125 150 175 200 225 250
		do
    			for walklen in 25 50 75 100 125 150 175 200 225 250
    			do
	 			wfile="data/walks/walks_N${nwalks}_L${walklen}.txt"
				embedfile="data/embeddings/ontograph_embed_N${nwalks}_L${walklen}_D${vector_size}_K${context_window}.model"
				
				model_count=$(ls data/clusters/kmeans/ontograph_embed_N${nwalks}_L${walklen}_D${vector_size}_K${context_window}_KMEANS_KOPT*.pkl 2>/dev/null | wc -l )
				if [ $model_count == 0  ]; then
					
					sbatch src/scripts/submit_clusters.sh $embedfile
				
				fi
    			done
		done	
    	done
done
