#!/bin/bash
#
#SBATCH --mem=8g
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mail-type=END

python src/data/randomize_graph.py data/processed/disease_ontograph.pkl ${1}