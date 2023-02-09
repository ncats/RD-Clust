#!/bin/bash
#
#SBATCH --mem=64g
#SBATCH --cpus-per-task=16
#SBATCH --ntasks=1
#SBATCH --time=48:00:00
#SBATCH --mail-type=END

python src/analysis/summarize_walks.py data/walks/walks_N250_L250.txt 20 data/clusters/kmeans/ontograph_embed_N250_L250_D32_K20_KMEANS_KOPT35.pkl
