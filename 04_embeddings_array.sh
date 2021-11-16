#!/bin/bash

for vector_size in 16 32 64 128 256 512
do
    for context_window in {6..20..2}
    do
    
        sbatch --job-name vector_embeddings_D${vector_size}_K${context_window} \
	submit_embeddings.sh \
        $vector_size \
	$context_window
	 
    done
done
