#!/bin/bash

for vector_size in 256  # 8 14 16 18 20 24 32 64 128 256 360 #512
do
	for context_window in 14 #  8 10 12 14 16
	do

		for nwalks in 30 #5 10 20 30 40 50 60 70 80
		do
    			for walklen in 175 #25 50 75 100 125 150 175 200
    			do
	 			wfile="data/walks/walks_N${nwalks}_L${walklen}.txt"
				embedfile="data/embeddings/ontograph_embed_N${nwalks}_L${walklen}_D${vector_size}_K${context_window}.model"
				
				model_count=$(ls data/clusters/kmeans/ontograph_embed_N${nwalks}_L${walklen}_D${vector_size}_K${context_window}_KMEANS_KOPT*.pkl 2>/dev/null | wc -l )
				if [ $model_count == 0  ]; then
					
					sbatch submit_clusters.sh $embedfile
				
				fi
    			done
		done	
    	done
done
