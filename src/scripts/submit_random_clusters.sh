#!/bin/bash
#
#SBATCH --mem=8g
#SBATCH --cpus-per-task=4
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mail-type=END

#graphfile #embedfile
python src/model/cluster_embeddings.py ${1} ${2}

