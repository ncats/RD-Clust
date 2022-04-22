#!/bin/bash
for efile in data/embeddings/*.model
do
    #echo $efile
    sbatch submit_clusters.sh $efile
	
done 

