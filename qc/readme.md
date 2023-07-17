# RDClust: Clustering of rare diseases on knowledge graphs quality check

## Workflow:

1.	``` bash random_graph_walks.sh ```
runs src/scripts/submit_random_graph_walks.sh and python src/model/random_sequence.py
-o 100x random_walk.txt

2.	``` bash random_graph_embeddings.sh ```
runs src/scripts/submit_random_embeddings.sh and python /data/binderjl/test/src/model/generate_random_embeddings.py
	-o random_ontograph_embed_{i}.model
     random_ontograph_embed_{i}.model.syn1neg.npy
     random_ontograph_embed_{i}.model.wv.vectors.npy

3.	``` bash random_graph_clusters.sh ```
runs src/scripts/submit_random_clusters.sh and python src/model/cluster_embeddings.py
-o random_ontograph_embed_{i}_KMEANS_KOPT*.pkl
