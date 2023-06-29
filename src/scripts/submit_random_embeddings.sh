#!/bin/bash
#
#SBATCH --mem=8g
#SBATCH --cpus-per-task=4
#SBATCH --ntasks=1
#SBATCH --time=36:00:00
#SBATCH --mail-type=END

python src/model/generate_random_embeddings.py ${1} ${2} ${3} ${4}

