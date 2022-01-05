#!/usr/bin/env python3

import sys
from pathlib import Path
from collections import Counter
import pickle
import pandas as pd
import obonet
import networkx as nx
import mygene

from goatools.anno.gaf_reader import GafReader
from goatools.base import download_ncbi_associations
from goatools.anno.genetogo_reader import Gene2GoReader


def get_sif_genes(sif_data):
    ptc_genes = []
    for i in sif_data:
        if 'CHEBI' not in i[0]:
            ptc_genes.append(i[0])
        if 'CHEBI' not in i[2]:
            ptc_genes.append(i[2])
    return set(ptc_genes)

def process_pathway_commons_sif(sif_data):
    """
    Process simple interaction format data as edge list
    """
    
    ptc_genes = get_sif_genes(sif_data)

    mg = mygene.MyGeneInfo()
    mg_hgnc = mg.querymany(list(ptc_genes), scopes='symbol,alias', fields='entrezgene', species='human',returnall=True)

    entrez_counts = Counter([i.get('query') for i in mg_hgnc['out'] if i.get('entrezgene')])

    symbol2entrez = {}
    for gene in entrez_counts.keys():
        
        gene_results = [result for result in mg_hgnc['out'] if (result.get('query') == gene) and (result.get('entrezgene'))]

        if len(gene_results)==1:
            symbol2entrez[gene_results[0]['query']]=gene_results[0]['entrezgene']
        elif len(gene_results)>1:
            scores = [result['_score'] for result in gene_results]
            #Take the firs in the case of ties
            best_result = gene_results[scores.index(max(scores))]
            symbol2entrez[best_result['query']]=best_result['entrezgene']
    
    ptc_graph = nx.MultiGraph()
    
    for sif in sif_data:
        edge = []
        for i in [0,2]:
            if 'CHEBI' not in sif[i]:
                if sif[i] in symbol2entrez:
                    ptc_graph.add_node(int(symbol2entrez[sif[i]]),label='gene')
                    edge.append(int(symbol2entrez[sif[i]]))
                    
            else:
                ptc_graph.add_node(sif[i],label='chebi')
                edge.append(sif[i])
                                
        if len(edge)==2:
            ptc_graph.add_edge(edge[0],edge[1],key=sif[1])

    return ptc_graph

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
            disease_gene_phen_subgraph.add_edge(dis,hpo,key="presents")
    
    return disease_gene_phen_subgraph

def main():
    project_dir = Path(__file__).resolve().parents[2]

    gene_ontology = obonet.read_obo(project_dir / sys.argv[1]).to_undirected()
    phenotype_ontology  = obonet.read_obo(project_dir / sys.argv[2]).to_undirected()

    nx.set_node_attributes(gene_ontology,'GO','label')
    nx.set_node_attributes(phenotype_ontology,'HPO','label')

    gene2go = get_goa(project_dir / 'data/raw/gene2go')

    gard_gene_df = pd.read_csv(project_dir / 'data/raw/gard2gene.csv')
    gard_phen_df = pd.read_csv(project_dir / 'data/raw/gard2hpo.csv')

    disease_subgraph = construct_disease_subgraph(gard_gene_df, gard_phen_df,gene2go)
    disease_subgraph.remove_nodes_from(list(nx.isolates(disease_subgraph)))
    

    disease_ontograph = nx.compose_all([disease_subgraph,phenotype_ontology,gene_ontology])
    disease_ontograph.remove_nodes_from(list(nx.isolates(disease_ontograph)))

    #Pathway commons chemical and gene/protein interaction data https://www.pathwaycommons.org/archives/PC2/v12/
    with open(project_dir / 'data/raw/PathwayCommons12.All.hgnc.sif','r') as ptc_file:
        ptc_sif = [i.strip().split('\t') for i in ptc_file.readlines()]

    ptc_graph = process_pathway_commons_sif(ptc_sif)
    disease_ontograph = nx.compose_all([disease_ontograph,ptc_graph])

    print(disease_ontograph.number_of_nodes())

    with open(project_dir / 'data/processed/disease_ontograph.pkl', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(disease_ontograph, f, pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    main()
