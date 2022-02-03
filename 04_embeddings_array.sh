#!/bin/bash

for vector_size in 256 # 8 14 16 18 20 24 32 64 128 256 360 512
do
	for context_window in 14 # 8 10 12 14 16
	do
		for nwalks in 30 # 5 10 20 30 40 50 60 70 80
		do
    			for walklen in 175 # 25 50 75 100 125 150 175 200
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
		#for wfile in data/walks/*
        	#do

            		#sbatch --job-name vector_embeddings_D${vector_size}_K${context_window} \
	    		#submit_embeddings.sh $wfile $vector_size $context_window
	    
        	#done
    	done
done
