#!/bin/bash

for i in {1..100}
do
  echo $i
  #sbatch --job-name random_graph_${i} src/scripts/submit_randomize_graph.sh ${i}
done
