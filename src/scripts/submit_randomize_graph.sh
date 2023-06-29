#!/bin/bash
#
#SBATCH --mem=16g
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --time=10-00:00:00
#SBATCH --mail-type=END

python src/data/randomize_graph.py data/processed/disease_ontograph.pkl ${1}
