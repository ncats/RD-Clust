#!/bin/bash

for vector_size in  8 14 16 18 20 24 32 64 128 256 360 512
do
	for context_window in 10 12 14
	do
		for nwalks in 80 100 120
		do
    			for walklen in 25 50 75 100
    			do
	 			wfile="data/walks/walks_N${nwalks}_L${walklen}.txt"
				embedfile="data/embeddings/ontograph_embed_N${nwalks}_L${walklen}_D${vector_size}_K${context_window}.model"
				if [ ! -f "$embedfile" ]; then
					sbatch --job-name vector_embeddings_D${vector_size}_K${context_window} \
                        		submit_embeddings.sh $wfile $vector_size $context_window
				    #echo $embedfile
                fi		
    			done
		done	
    	done
done
