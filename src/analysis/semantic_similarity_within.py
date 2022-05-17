import pickle
from pathlib import Path
from joblib import Parallel, delayed

import networkx as nx
import pandas as pd
from nxontology.imports import from_file


def semantic_sim_set(ontology,ont_map,metric,cluster,tups):
    # TODO:
    # Check if entities are in map
    # Check if mapped entities are in ontology
    # Check if metric is valid
    # Try and catch
    print(str(cluster)+'\n')
    sim = {}
    for entities in tups:
        sim[entities] = ontology.similarity(ont_map[entities[0]],ont_map[entities[1]], ic_metric=metric).lin

    return {cluster:sim}

def main():
    
    project_dir = Path(__file__).resolve().parents[2]
    
    with open(project_dir / "data/processed/disease_ontograph.pkl", 'rb') as f:
        disease_ontograph = pickle.load(f)
    #Remove unconnected components
    components = [i for i in nx.connected_components(disease_ontograph)]
    disease_ontograph = disease_ontograph.subgraph(components[0]).copy()

    diseases = [n for n in disease_ontograph.nodes if disease_ontograph.nodes[n].get('label') ==  'disease']
        
    gard_gene_raw = pd.read_csv(project_dir / 'data/raw/disease_genes_palantir.csv')
    gard_phen_raw =  pd.read_csv(project_dir / 'data/raw/disease_phenotypes_palantir.csv')

    gard_diseases = pd.concat([gard_gene_raw[['OrphaCode','curie','label']],gard_phen_raw[['OrphaCode','curie','label']]],axis=0).drop_duplicates().reset_index()

    ordo = from_file(project_dir / 'data/raw/ordo_orphanet.owl')
    gard2orpha = {i:'http://www.orpha.net/ORDO/Orphanet_{0}'.format(j) for i,j in zip(gard_diseases['curie'],gard_diseases['OrphaCode'])}


    with open(project_dir / 'data/clusters/kmeans/ontograph_embed_N250_L250_D32_K20_KMEANS_KOPT35.pkl', 'rb') as f:
        cluster_model = pickle.load(f)
                
    cluster_map = {dis:cluster_model.labels_[i] for i,dis in enumerate(diseases)}

    cluster_sets = {i:[] for i in set(cluster_model.labels_)}

    for i in cluster_map:
        cluster_sets[cluster_map[i]].append(i)

    cluster_tuples = {i:[] for i in set(cluster_model.labels_)}

    for cluster in cluster_sets:
        cluster_disease = cluster_sets[cluster]
        for i in range(len(cluster_disease)):
            for j in range(i+1,len(cluster_disease)):
                cluster_tuples[cluster].append((cluster_disease[i],cluster_disease[j]))

    print("starting parallel loop\n")

    within_cluster_sim = Parallel(n_jobs=-1)(delayed(semantic_sim_set)(ordo,gard2orpha,"intrinsic_ic_sanchez",cluster,tups) for cluster, tups in cluster_tuples.items())

    print("Finished parallel loop\n")

    with open(project_dir / 'data/processed/ordo_semantic_similarity_within_cluster_test.pkl', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(within_cluster_sim, f, pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    main()
