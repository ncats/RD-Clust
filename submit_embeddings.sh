#!/bin/bash
#
#SBATCH --mem=4g
#SBATCH --cpus-per-task=4
#SBATCH --ntasks=1
#SBATHC --time=24:00:00
#SBATCH --mail-type=END

python src/model/generate_embeddings.py ${1} ${2} ${3}

