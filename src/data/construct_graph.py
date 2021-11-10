import sys
from pathlib import Path
import pickle
import pandas as pd
import obonet
import networkx as nx

from goatools.anno.gaf_reader import GafReader
from goatools.base import download_ncbi_associations
from goatools.anno.genetogo_reader import Gene2GoReader

def get_goa(goa_file):

    # Read NCBI's gene2go. Store annotations in a list of namedtuples
    objanno = Gene2GoReader(goa_file, taxids=[9606])

    gene2go = {}
    for assoc in objanno.associations:
        if assoc.DB_ID in gene2go:
            if assoc.NS in gene2go[assoc.DB_ID]:
                gene2go[assoc.DB_ID][assoc.NS].append({'GO_ID':assoc.GO_ID,'Qualifier':assoc.Qualifier})
            else:
                gene2go[assoc.DB_ID][assoc.NS] = [{'GO_ID':assoc.GO_ID,'Qualifier':assoc.Qualifier}]
        else:
            gene2go[assoc.DB_ID] = {assoc.NS:[{'GO_ID':assoc.GO_ID,'Qualifier':assoc.Qualifier}]}

    return gene2go


def construct_disease_subgraph(gard_gene_df, gard_phen_df,gene2go):
    
    disease_gene_phen_subgraph = nx.MultiGraph()
    for dis in set(gard_gene_df.GARD_ID):
        genes = gard_gene_df[gard_gene_df.GARD_ID == dis]
        phens = gard_phen_df[gard_phen_df.GARD_ID == dis]
        
        disease_gene_phen_subgraph.add_node(dis,label='disease')
        
        for ind, row in genes.iterrows():
            
            if (row['Gene_ID'] is not None) & (pd.isna(row['Gene_ID']) == False):

                gene = int(row['Gene_ID'])
                
                disease_gene_phen_subgraph.add_node(gene,label='gene')

                disease_gene_phen_subgraph.add_edge(dis,gene,key="causes")
                
                gene_annotation = gene2go.get(gene)
                if gene_annotation is not None:
                    for go_class in gene_annotation.keys():
                        for annot in gene_annotation.get(go_class):
                            
                            disease_gene_phen_subgraph.add_node(annot['GO_ID'],label='GO')
                            
                            disease_gene_phen_subgraph.add_edge(gene,annot['GO_ID'],key="associated_with")
        
        for hpo in phens.HPO_ID:
            disease_gene_phen_subgraph.add_node(hpo,label='HPO')
            disease_gene_phen_subgraph.add_edge('GARD:{}'.format(dis),hpo,key="presents")
    
    return disease_gene_phen_subgraph

def main():
    project_dir = Path(__file__).resolve().parents[2]

    gene_ontology = obonet.read_obo(project_dir /sys.argv[1]).to_undirected()
    phenotype_ontology  = obonet.read_obo(project_dir /sys.argv[2]).to_undirected()

    nx.set_node_attributes(gene_ontology,'GO','label')
    nx.set_node_attributes(phenotype_ontology,'HPO','label')

    gene2go = get_goa(project_dir / 'data/gene2go')

    gard_gene_df = pd.read_csv(project_dir / 'data/gard2gene.csv')
    gard_phen_df = pd.read_csv(project_dir / 'data/gard2hpo.csv')

    disease_subgraph = construct_disease_subgraph(gard_gene_df, gard_phen_df,gene2go)
    disease_subgraph.remove_nodes_from(list(nx.isolates(disease_subgraph)))
    
    

    disease_ontograph = nx.compose_all([disease_subgraph,phenotype_ontology,gene_ontology])
    disease_ontograph.remove_nodes_from(list(nx.isolates(disease_ontograph)))

    with open(project_dir / 'data/disease_ontograph.pkl', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(disease_ontograph, f, pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    main()