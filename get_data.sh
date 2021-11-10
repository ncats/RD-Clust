#!/bin/bash

python src/data/query_neo4j.py

wget -O data/gene2go.gz ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2go.gz 
gunzip data/gene2go.gz
