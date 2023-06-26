#!/bin/bash

for i in 1..100
do
  sbatch src/scripts/submit_randomize_graph.sh ${i}
done
