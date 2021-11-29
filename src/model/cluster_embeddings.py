#!/usr/bin/env python3
import sys
import os
import pickle
from pathlib import Path
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from sklearn.utils.validation import _deprecate_positional_args
from gensim.models import Word2Vec
from sklearn import cluster,metrics
from sklearn.preprocessing import StandardScaler, Normalizer
from kneed import KneeLocator


def run_kmeans(disease_vectors):
    inertia_scores = []
    k_values = [i for i in range(2,200)]

    standard_vectors = StandardScaler().fit_transform(disease_vectors)
    normalized_vectors = Normalizer().fit_transform(standard_vectors)

    for k in k_values:
        model = cluster.KMeans(n_clusters=k)
        model.fit(normalized_vectors)
        inertia_scores.append(model.inertia_)
    
    # Find the knee point in the curve.
    elbows = []
    for sval in range(1,30):
        kl = KneeLocator(x=k_values, 
                        y=inertia_scores, 
                        curve='convex', 
                        direction='decreasing',
                        interp_method='polynomial', 
                        S=sval)
        elbows.append(kl.knee)
    
    #Save the best model options
    best_models = dict()
    for k_opt in set(elbows):
        model = cluster.KMeans(n_clusters=k_opt)
        model.fit(normalized_vectors)
        best_models[k_opt] = model

    return(best_models)

def main():
    
    graph_file = sys.argv[1]
    embeddings_file = sys.argv[2]    
    project_dir = Path(__file__).resolve().parents[2]
    #TODO:checks on the graph
    with open(project_dir / graph_file, 'rb') as f:
        disease_ontograph = pickle.load(f)
        #Remove unconnected components
    components = [i for i in nx.connected_components(disease_ontograph)]
    disease_ontograph = disease_ontograph.subgraph(components[0]).copy()

    diseases = [n for n in disease_ontograph.nodes if disease_ontograph.nodes[n].get('label') ==  'disease']
    
    model = Word2Vec.load(str(project_dir / embeddings_file))
    disease_vectors = model.wv[diseases]
    
    k_means_best = run_kmeans(disease_vectors)
    for k_opt in k_means_best.keys():
        model_file = os.path.basename(embeddings_file).split('.')[0] + "_KMEANS_KOPT{0}.pkl".format(k_opt)
        with open(project_dir / 'data/clusters/kmeans/{0}'.format(model_file), 'wb') as kmf:
            pickle.dump(k_means_best[k_opt], kmf, pickle.HIGHEST_PROTOCOL)
    
if __name__=="__main__":
    main()