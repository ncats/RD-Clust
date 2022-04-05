import sys
import pickle
from functools import reduce
from pathlib import Path
import networkx as nx
import pandas as pd
import numpy as np
from joblib import Parallel, delayed



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

def permute_annotation_counts(diseases,annotation_counts,cluster_model,P):
    """
    Generate permutation of annotation counts per cluster and compare to observered
    """
    count_matrix = annotation_counts.pivot_table('Count', 'Cluster', 'Annotation',aggfunc='sum').fillna(0)
    perm_results = np.zeros(count_matrix.shape)
    
    annotation_counts_perm = annotation_counts.copy()
    cluster_labels_perm = cluster_model.labels_
    
    for i in range(P):
        np.random.shuffle(cluster_labels_perm)
        cluster_map_perm = {dis:cluster_labels_perm[i] for i,dis in enumerate(diseases)}
        annotation_counts_perm['Cluster'] = [cluster_map_perm.get(i) for i in annotation_counts_perm.Disease]
        count_matrix_perm = annotation_counts_perm.pivot_table('Count', 'Cluster', 'Annotation',aggfunc='sum').fillna(0)
        perm_results += np.greater_equal(count_matrix_perm.loc[count_matrix.index],count_matrix)*1
    
    return perm_results

def calculate_perm_pvalue(perm_sets,annotation_counts,tot_perm):
    
    perm_results = reduce(lambda x, y: x.add(y, fill_value=0), perm_sets)

    annotation_counts_by_cluster = annotation_counts.groupby(['Cluster','Annotation']).agg({'Count':'sum'}).reset_index()

    perm_results_condensed = annotation_counts_by_cluster.merge(perm_results.reset_index().melt(id_vars='Cluster').sort_values(['Cluster','Annotation']))
    perm_results_condensed['perm_p'] = np.fmax(np.ones(perm_results_condensed.shape[0]),perm_results_condensed['value'].values)/tot_perm

    return perm_results_condensed

def main():
    project_dir = Path(__file__).resolve().parents[2]
    model_file = sys.argv[1]
    walk_annot_file = sys.argv[2]
    P = int(sys.argv[3]) #sets of perms

    p = 100 #perms per set
    tot_perm = P*p

    #TODO:move these into parser
    with open(project_dir / "data/processed/disease_ontograph.pkl", 'rb') as f:
        disease_ontograph = pickle.load(f)

    with open(project_dir / model_file, 'rb') as f:
        cluster_model = pickle.load(f)

    #Remove unconnected components
    components = [i for i in nx.connected_components(disease_ontograph)]
    disease_ontograph = disease_ontograph.subgraph(components[0]).copy()

    diseases_in_graph = [n for n in disease_ontograph.nodes if disease_ontograph.nodes[n].get('label') ==  'disease']
    cluster_map = {d:cluster_model.labels_[i] for i,d in enumerate(diseases_in_graph)}  

    walk_annotations = pd.read_table(project_dir / walk_annot_file,index_col=None)
    walk_annotation_counts = walk_annotations[['Cluster','Disease','Annotation','Count']]

    gard_gene_data = pd.read_csv(project_dir / "data/raw/gard2gene.csv")
    gard_gene_data = gard_gene_data[gard_gene_data.Gene_ID.isnull()==False]
    gard_gene_data.Gene_ID = gard_gene_data.Gene_ID.astype('int')
    gard_gene_data['Cluster'] = [cluster_map.get(i) for i in gard_gene_data.GARD_ID]
    gard_gene_data.dropna(subset=['Cluster'])

    gene_annotation_counts = gard_gene_data[['Cluster','GARD_ID','Gene_Symbol']].copy()
    gene_annotation_counts['Count'] = 1
    gene_annotation_counts.columns = ['Cluster','Disease','Annotation','Count']

    gene_perm_sets = Parallel(n_jobs=-1)(delayed(permute_annotation_counts)(diseases_in_graph,gene_annotation_counts,cluster_model,p) for i in range(P))
    walk_perm_sets = Parallel(n_jobs=-1)(delayed(permute_annotation_counts)(diseases_in_graph,walk_annotation_counts,cluster_model,p) for i in range(P))
    
    gene_perm_results = calculate_perm_pvalue(gene_perm_sets,gene_annotation_counts,tot_perm)
    walk_perm_results = calculate_perm_pvalue(walk_perm_sets,walk_annotation_counts,tot_perm)

    gene_perm_results.to_csv(project_dir / 'data/processed/gene_annotation_enrichment.csv',index=False)
    walk_perm_results.to_csv(project_dir / 'data/processed/walk_annotation_enrichment.csv',index=False)

if __name__=="__main__":
    main()
