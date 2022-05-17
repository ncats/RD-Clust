#!/bin/bash
#
#SBATCH --cpus-per-task=56
#SBATCH --mem=128g
#SBATCH --ntasks=1
#SBATCH --time=96:00:00
#SBATCH --mail-type=END

python src/analysis/cluster_enrichment.py data/clusters/kmeans/ontograph_embed_N250_L250_D32_K20_KMEANS_KOPT35.pkl data/processed/cluster_walk_annotations.txt 56
