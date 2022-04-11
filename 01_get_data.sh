#!/bin/bash

export $(cat config.env | xargs)

#GARD2.0 Data Lake data from Palantir
curl -X GET -o "data/raw/gard2gene_palantir.csv" -H "Authorization: Bearer ${PALANTIR_KEY}" \
"https://nidap.nih.gov/foundry-data-proxy/api/dataproxy/datasets/\
${GENE_DATA_RID}/\
branches/master/csv?includeColumnNames=true"

curl -X GET -o "data/raw/gard2hpo_palantir.csv" -H "Authorization: Bearer ${PALANTIR_KEY}" \
"https://nidap.nih.gov/foundry-data-proxy/api/dataproxy/datasets/\
${PHENOTYPE_DATA_RID}/\
branches/master/csv?includeColumnNames=true"

#Gene target - ligand/drug data from Pharos
python src/data/query_pharos.py

#ChEMBL - CHEBI mappings
wget -O data/raw/src1src7.txt.gz https://ftp.ebi.ac.uk/pub/databases/chembl/UniChem/data/wholeSourceMapping/src_id1/src1src7.txt.gz
gunzip data/raw/src1src7.txt.gz

#ChEBI - PubChem mappings
wget -O data/raw/src7src22.txt.gz https://ftp.ebi.ac.uk/pub/databases/chembl/UniChem/data/wholeSourceMapping/src_id7/src7src22.txt.gz
gunzip data/raw/src7src22.txt.gz

#GO Annotations from NCBI
wget -O data/raw/gene2go.gz ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2go.gz 
gunzip data/raw/gene2go.gz

wget -O data/raw/PathwayCommons12.All.hgnc.sif.gz https://www.pathwaycommons.org/archives/PC2/v12/PathwayCommons12.All.hgnc.sif.gz 
gunzip data/raw/PathwayCommons12.All.hgnc.sif.gz

#Obtain ontologies
for ont in hp go
do
    curl -L http://purl.obolibrary.org/obo/${ont}.owl > data/raw/${ont}.owl
done

