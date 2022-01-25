#!/bin/bash
for efile in data/embeddings/*.model
do

	sbatch submit_clusters.sh $efile
	
done 

