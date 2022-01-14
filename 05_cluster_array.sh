#!/bin/bash
for i in 2 4 8 16
do

	for efile in data/embeddings/*_D${i}_*.model
	do

   		sbatch submit_clusters.sh $efile
	
	done 
done

