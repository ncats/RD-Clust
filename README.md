# RDClust: Clustering of rare diseases on knowledge graphs

Identifying sets of rare diseases with shared aspects of etiology and pathophysiology may enable drug repurposing and/or platform based therapeutic development. Toward that aim we utilize an integrative knowledge graph-based approach to constructing clusters of rare diseases. 

## Workflow:

The workflow is designed to executed within an HPC slurm cluster environment. If you just want to get a better sense of the approach, please see the various example notebooks provided. 

The steps to reproducing the workflow are outlined below:

- 0) Set up environment and directory: 
```
bash 00_setup_data.sh
conda env create -f rdclust.yml
conda activate rdclust
pip install -r requirements.txt
```
- 1) Get data: ```01_get_gard_data.sh``` and ```01_get_public_data.sh```
    - The GARD data aren't presently publicly accessible via API so we provide them in this repository
- 2) Pre-process the data: ```02_process_ontologies.sh```
- 3) Generate random walks: ```03_walks_array.sh```
- 4) Generate node embeddings: ```04_embeddings_array.sh```
- 5) Create clustering models: ```05_cluster_array.sh```
- 6) Post-hoc summaries 
    - Gene enrichment: ```06_calculate_enrichment.sh```
    - Clustering metrics: ```06_summarize_clusters.sh```
    - Walk annotation counts: ```06_summarize_walks.sh```
- 7) Detailed analysis and Visualization in the notebooks directory

