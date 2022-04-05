import sys
import os
import pickle
import glob
from collections import Counter
from pathlib import Path
import networkx as nx
import pandas as pd
import numpy as np
from sklearn import cluster,metrics
from joblib import Parallel, delayed
import gensim

def flatten(t):
    return [item for sublist in t for item in sublist]


def get_windows(disease,walks,context_size):
    """All windows for a given disease in a set of random walks"""
    d_win = []
    for walk in walks:
        if disease in walk:
            walk_split = walk.split()   
            disease_index = [ i for i in range(len(walk_split)) if walk_split[i] == disease ]
            
            for i in disease_index:    
                d_win.append(walk_split[max(0,i - context_size):min(len(walk_split),i+context_size+1)])
    
    return {disease:d_win}


def main():
    project_dir = Path(__file__).resolve().parents[2]
    walk_file = sys.argv[1]
    context_size = int(sys.argv[2])
    m_file = sys.argv[3]

    #TODO:move these into parser
    with open(project_dir / "data/processed/disease_ontograph.pkl", 'rb') as f:
        disease_ontograph = pickle.load(f)
    #Remove unconnected components
    components = [i for i in nx.connected_components(disease_ontograph)]
    disease_ontograph = disease_ontograph.subgraph(components[0]).copy()

    diseases_in_graph = [n for n in disease_ontograph.nodes if disease_ontograph.nodes[n].get('label') ==  'disease']

    with open(project_dir / walk_file,'r') as wfile:
        walks = wfile.readlines()    

    with open(project_dir / m_file, 'rb') as f:
        cluster_model = pickle.load(f)

    cluster_map = {d:cluster_model.labels_[i] for i,d in enumerate(diseases_in_graph)}

    diseases_inwalks = list(set([w.split()[0] for w in walks]))

    disease_windows = Parallel(n_jobs=-1)(delayed(get_windows)(disease,walks,context_size) for disease in diseases_inwalks)
    disease_windows_combined = {dis: w_list for w_set in disease_windows for dis, w_list in w_set.items()}

    cluster_walk_annotations=[]
    node_strings = {str(i):i if disease_ontograph.nodes[i].get('label') == 'gene' else str(i) for i in disease_ontograph.nodes if 'GARD' not in str(i)}
    for d in diseases_inwalks:
        dis_w = flatten(disease_windows_combined[d])
        clust  = cluster_map.get(d)

        if clust is None:
            continue

        #Removal of edge types should be done earlier to for efficieincey
        dis_clust_annot = [node_strings[i] for i in dis_w if i in node_strings]
        annot_counts = Counter(dis_clust_annot)
        cluster_walk_annotations.extend([[str(clust),d,disease_ontograph.nodes[a[0]].get('label'),str(a[0]),str(a[1])] for a in annot_counts.items()])

    with open(project_dir / 'data/processed/cluster_walk_annotations.txt','w') as annot_file:
        annot_file.write('Cluster\tDisease\tAnnotation_Type\tAnnotation\tCount\n')
        for i in cluster_walk_annotations:
            annot_file.write("\t".join(i) + '\n')
            #annot_file.writelines(["\t".join(str(i)) for i in cluster_walk_annotations])
    

if __name__=="__main__":
    main()
