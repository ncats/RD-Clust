#!/bin/bash
#
#SBATCH --mem=4g
#SBATCH --cpus-per-task=4
#SBATCH --ntasks=1
#SBATCH --mail-type=END

python src/model/generate_embeddings.py \
data/walks \
${1} \
${2}

