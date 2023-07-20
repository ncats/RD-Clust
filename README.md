# RDClust: Clustering of rare diseases on knowledge graphs

Identifying sets of rare diseases with shared aspects of etiology and pathophysiology may enable drug repurposing and/or platform-based therapeutic development. Toward that aim, we utilize an integrative knowledge graph-based approach to constructing clusters of rare diseases. 

## Workflow:

Note: The workflow is designed and executed within an HPC slurm cluster environment. 
For more information, please see the various example notebooks provided. 

The steps to reproducing the workflow are outlined below:

- 0) Set up environment and directory: 
```
bash 00_setup_data.sh
conda env create -f rdclust.yml
conda activate rdclust
pip install -r requirements.txt
```
- 1) Get data: ```01_get_public_data.sh```
###### Note - The GARD data is currently NOT publicly accessible via API; therefore, we provide the necessary datasets in this repository (RD-Clust/data/raw/). When an API is publicly available, the workflow and ```01_get_gard_data.sh``` will be updated.
- 2) Pre-process the data: ```02_process_ontologies.sh```
- 3) Generate random walks: ```03_walks_array.sh```
- 4) Generate node embeddings: ```04_embeddings_array.sh```
- 5) Create clustering models: ```05_cluster_array.sh```
- 6) Post-hoc summaries 
    - Gene enrichment: ```06_calculate_enrichment.sh```
    - Clustering metrics: ```06_summarize_clusters.sh```
    - Walk annotation counts: ```06_summarize_walks.sh```
    - Semantic similarity: ```06_calculate_semantic_similarity.sh```
- 7) Detailed analysis and Visualization in the notebooks directory
 
     ______________
     
* For quality check, we randomized graphs to assess how well disease nodes cluster when their relationships are not based on real knowledge. See QC directory for quality control pipeline *
