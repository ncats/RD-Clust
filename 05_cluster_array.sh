#!/bin/bash

for efile in data/embeddings/*
do

    sbatch submit_clusters.sh $efile

done

