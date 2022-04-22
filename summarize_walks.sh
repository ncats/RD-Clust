#!/bin/bash
#
#SBATCH --mem=32g
#SBATCH --cpus-per-task=16
#SBATCH --ntasks=1
#SBATCH --time=48:00:00
#SBATCH --mail-type=END

python src/analysis/summarize_walks.py data/walks/walks_N120_L25.txt 12 data/clusters/kmeans/ontograph_embed_N120_L25_D512_K12_KMEANS_KOPT37.pkl
