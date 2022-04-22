#!/bin/bash
#
#SBATCH --mem=16g
#SBATCH --cpus-per-task=4
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mail-type=END

for ont in hp go
do
    third_party/bin/robot reason --reasoner ELK --annotate-inferred-axioms true --input data/raw/${ont}.owl --output data/processed/${ont}-reasoned.owl
    third_party/bin/robot convert --check false --input data/processed/${ont}-reasoned.owl --format obo --output data/processed/${ont}-reasoned.obo
done 

python src/data/construct_graph.py data/processed/go-reasoned.obo data/processed/hp-reasoned.obo 
