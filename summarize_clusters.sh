#!/bin/bash
#
#SBATCH --mem=32g
#SBATCH --cpus-per-task=8
#SBATCH --ntasks=1
#SBATCH --time=24:00:00

python src/analysis/summarize_clusters.py
