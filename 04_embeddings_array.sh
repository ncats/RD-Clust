#!/bin/bash

for vector_size in 2 4 8 16 32 64 128 256
do
    for context_window in 8 10 12 14
    do
        for wfile in data/walks/*
        do

            sbatch --job-name vector_embeddings_D${vector_size}_K${context_window} \
	        submit_embeddings.sh $wfile $vector_size $context_window

        done
    done
done
