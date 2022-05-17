#!/bin/bash
#
#SBATCH --cpus-per-task=56
#SBATCH --mem=64g
#SBATCH --ntasks=1
#SBATCH --time=96:00:00
#SBATCH --mail-type=END

python src/analysis/hypergeometric_test.py data/processed/cluster_walk_annotations.txt
