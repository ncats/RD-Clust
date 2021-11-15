#!/bin/bash

for ont in hp go
do
    third_party/bin/robot reason --reasoner ELK --annotate-inferred-axioms true \
    --input data/raw/${ont}.owl --output data/processed/${ont}-reasoned.owl

    third_party/bin/robot convert --check false \
    --input data/processed/${ont}-reasoned.owl --format obo --output data/processed/${ont}-reasoned.obo
done 

python src/data/construct_graph.py data/go-reasoned.obo data/hp-reasoned.obo 
