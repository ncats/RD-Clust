import sys
import os
import pickle
import glob
import scipy.stats as stats

import networkx as nx
import pandas as pd
import numpy as np


from sklearn import cluster,metrics
from nxontology.imports import from_file
from joblib import Parallel, delayed


def main():
    
    project_dir = Path(__file__).resolve().parents[2]
    model_files = glob.glob(str(project_dir / "data/clusters/kmeans/*.pkl"))
    #print(model_files[0])
    with open(project_dir / "data/processed/disease_ontograph.pkl", 'rb') as f:
        disease_ontograph = pickle.load(f)
    #Remove unconnected components
    components = [i for i in nx.connected_components(disease_ontograph)]
    disease_ontograph = disease_ontograph.subgraph(components[0]).copy()

    diseases = [n for n in disease_ontograph.nodes if disease_ontograph.nodes[n].get('label') ==  'disease']
    
    disease_cluster_data = pd.read_csv(project_dir / "data/processed/disease_cluster_information.csv")
    gard_mondo = pd.read_csv(project_dir / "data/raw/gard2mondo.csv")
    gard2mondo = {row[1]['GARD_ID']:row[1]['MONDO_ID'] for row in gard_mondo.iterrows()}

    N = 80
    L = 25
    D = 512 
    K_dim = 10
    m_file = project_dir / "data/clusters/kmeans/ontograph_embed_N{0}_L{1}_D{2}_K{3}_KMEANS_KOPT37.pkl".format(N,L,D,K_dim)

    mondo = from_file('http://purl.obolibrary.org/obo/mondo.obo')
    mondo_dz = [gard2mondo[i] for i in diseases if gard2mondo[i] in mondo.graph]

    model_evals = Parallel(n_jobs=-1)(delayed(summarize_model)(m_file,diseases,project_dir) for m_file in model_files)
   
    model_eval_df = pd.DataFrame(model_evals)
    model_eval_df.to_csv(project_dir / "data/processed/kmeans_model_metrics.csv",index=False)

if __name__=="__main__":
    main()