#!/bin/bash

for ddir in raw processed walks embeddings clusters
do
    mkdir -p data/$ddir
done

for cdir in kmeans meanshift affinity dbscan optics agglom
do
    mkdir -p data/clusters/$cdir
done