#!/bin/bash
#
#SBATCH --cpus-per-task=56
#SBATCH --ntasks=1
#SBATCH --time=96:00:00
#SBATCH --mail-type=END

python src/analysis/cluster_enrichment.py data/clusters/kmeans/ontograph_embed_N80_L25_D512_K10_KMEANS_KOPT37.pkl data/processed/cluster_walk_annotations.txt 56
