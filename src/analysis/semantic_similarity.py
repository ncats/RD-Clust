import pickle
from pathlib import Path
from joblib import Parallel, delayed

import networkx as nx
import pandas as pd
from nxontology.imports import from_file


def semantic_sim(ontology,entities,ont_map,metric='intrinsic_ic_sanchez'):
    # TODO:
    # Check if entities are in map
    # Check if mapped entities are in ontology
    # Check if metric is valid
    # Try and catch
    sim = ontology.similarity(ont_map[entities[0]],ont_map[entities[1]], ic_metric=metric).lin

    return {entities:sim}

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
    
    tuple_list = []
    for i in range(10):#range(len(gard2orpha)):
        for j in range(i+1,10):#range(i+1,len(gard2orpha)):
            tuple_list.append((gard_diseases['curie'][i],gard_diseases['curie'][j]))

    ordo_sim = Parallel(n_jobs=-1)(delayed(semantic_sim)(ordo,entities,gard2orpha,"intrinsic_ic_sanchez") for entities in tuple_list)
    ordo_sim_dict = {dis: sim for dis_sim in ordo_sim for dis, sim in dis_sim.items()}
    with open(project_dir / 'data/processed/ordo_semantic_similarity.pkl', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(ordo_sim_dict, f, pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    main()