#!/bin/bash

for ddir in raw processed walks embeddings clusters random_graphs
do
    mkdir -p data/$ddir
done

for cdir in kmeans
do
    mkdir -p data/clusters/$cdir
done
