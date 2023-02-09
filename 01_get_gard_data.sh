#!/bin/bash

export $(cat config.env | xargs)

#GARD2.0 Data Lake data from Palantir
curl -X GET -o "data/raw/disease_genes_palantir.csv" -H "Authorization: Bearer ${PALANTIR_KEY}" \
"https://nidap.nih.gov/foundry-data-proxy/api/dataproxy/datasets/\
${GENE_DATA_RID}/\
branches/master/csv?includeColumnNames=true"

curl -X GET -o "data/raw/non_root_disease_genes_palantir.csv" -H "Authorization: Bearer ${PALANTIR_KEY}" \
"https://nidap.nih.gov/foundry-data-proxy/api/dataproxy/datasets/\
${NON_ROOT_GENE_DATA_RID}/\
branches/master/csv?includeColumnNames=true"

curl -X GET -o "data/raw/disease_phenotypes_palantir.csv" -H "Authorization: Bearer ${PALANTIR_KEY}" \
"https://nidap.nih.gov/foundry-data-proxy/api/dataproxy/datasets/\
${PHENOTYPE_DATA_RID}/\
branches/master/csv?includeColumnNames=true"
