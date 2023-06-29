#!/bin/bash
#
#SBATCH --mem=8g
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH --mail-type=END
    
    
#graph_file walk_file walks_per_disease walk_len 

python src/model/generate_walks.py ${1} ${2} ${3} ${4}

