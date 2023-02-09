#!/bin/bash
#
#SBATCH --mem=128g
#SBATCH --cpus-per-task=56
#SBATCH --ntasks=1
#SBATCH --time=72:00:00
#SBATCH --mail-type=END

python src/analysis/semantic_similarity.py 
