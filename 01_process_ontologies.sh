#!/bin/bash

for ont in hp go
do
    third_party/bin/robot reason --reasoner ELK --annotate-inferred-axioms true --input data/${ont}.owl --output data/${ont}-reasoned.owl
    third_party/bin/robot convert --check false --input data/${ont}-reasoned.owl --format obo --output data/${ont}-reasoned.obo
    rm data/${ont}-reasoned.owl
done 

python src/data/construct_graph.py data/go-reasoned.obo data/hp-reasoned.obo 
