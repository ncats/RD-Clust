import sys
import os
import pickle
import glob
from pathlib import Path
import networkx as nx
import pandas as pd
import numpy as np
from sklearn import cluster,metrics
from sklearn.preprocessing import StandardScaler, Normalizer
from gensim.models import Word2Vec
from joblib import Parallel, delayed

def scatter_crit(X,labels):
    u = np.mean(X,axis=0)
    for k in set(labels):
        Nk = sum(labels == k)
        uk = np.mean(X[labels == k],axis=0)
        if k == 0:
            Sw = np.cov(X[labels == k],rowvar=False)*(Nk-1)
            Sb = Nk*np.outer(uk-u,uk-u)
        else:
            Sw += np.cov(X[labels == k],rowvar=False)*(Nk-1)
            Sb += Nk*np.outer(uk-u,uk-u)
        
    return np.trace(np.matmul(np.linalg.inv(Sw),Sb)) 

def summarize_model(m_file,diseases,project_dir): 
        m_pars = os.path.splitext(m_file)[0].split("_")
        N = m_pars[2][1:]
        L = m_pars[3][1:]
        D = m_pars[4][1:]
        K_dim = m_pars[5][1:]
        MODEL = m_pars[6]
        K_kmean = m_pars[7][4:]
                                    
        embedding_file = project_dir / "data/embeddings/ontograph_embed_N{0}_L{1}_D{2}_K{3}.model".format(N,L,D,K_dim)
        #print(embedding_file)
        model = Word2Vec.load(str(embedding_file))
        disease_vectors = model.wv[diseases]
        standard_vectors = StandardScaler().fit_transform(disease_vectors)
        normalized_vectors = Normalizer().fit_transform(standard_vectors)
                                                            
                                                                
        with open(m_file, 'rb') as f:
            cluster_model = pickle.load(f)
                                                                                    
        mdata = {}
        mdata['N_WALKS'] = int(N)
        mdata['L_WALKS'] = int(L)
        mdata['D_EMBED'] = int(D)
        mdata['K_DIM']   = int(K_dim)
        mdata['Model']   = MODEL
        mdata['K_clust'] = int(K_kmean)
                                                                                                                        
        mdata['silhouette_euclidean'] = metrics.silhouette_score(normalized_vectors, cluster_model.labels_, metric='euclidean')
        mdata['davies_bouldin'] = metrics.davies_bouldin_score(normalized_vectors, cluster_model.labels_)
        mdata['calinski_harabasz'] = metrics.calinski_harabasz_score(normalized_vectors, cluster_model.labels_)
        mdata['scattering_criteria'] = scatter_crit(normalized_vectors,cluster_model.labels_)
                                                                                                                                    
        return mdata

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
    
    model_evals = Parallel(n_jobs=-1)(delayed(summarize_model)(m_file,diseases,project_dir) for m_file in model_files)
   
    model_eval_df = pd.DataFrame(model_evals)
    model_eval_df.to_csv(project_dir / "data/processed/kmeans_model_metrics.csv",index=False)

if __name__=="__main__":
    main()
