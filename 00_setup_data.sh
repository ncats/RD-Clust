#!/bin/bash

for ddir in raw processed walks embeddings clusters
do
    mkdir -p data/$ddir
done