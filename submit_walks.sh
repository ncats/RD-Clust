#!/bin/bash
#
#SBATCH --mem=4g
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1

python src/model/generate_walks.py \
data/disease_ontograph.pkl \
data/walks/walks_N${1}_L${2}.txt \
${1} \
${2}

