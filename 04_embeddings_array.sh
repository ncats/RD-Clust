#!/bin/bash

for vector_size in  32
do
	for context_window in 6 8 10 12 14 16 18 20
	do
		for nwalks in 5 10 25 50 75 100 125 150 175 200 225 250
		do
    			for walklen in 25 50 75 100 125 150 175 200 225 250
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
