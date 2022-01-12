#!/usr/bin/env python3

import sys
from pathlib import Path
from collections import Counter
import pickle
import pandas as pd
import csv
import obonet
import networkx as nx
import mygene

from goatools.anno.gaf_reader import GafReader
from goatools.base import download_ncbi_associations
from goatools.anno.genetogo_reader import Gene2GoReader


def process_pharos_data(pharos_data,small_molecule_set,gene2go,gene_ontology):
    """
    Construct graph from pharos data
    """
    pharos_graph = nx.MultiGraph()

    pharos_uniprot = set([i.get('UniProt') for i in pharos_data])
    mg = mygene.MyGeneInfo()
    mg_uniprot = mg.querymany(list(pharos_uniprot), scopes='uniprot', fields='entrezgene', species='human',returnall=True)
    entrez_counts = Counter([i.get('query') for i in mg_uniprot['out'] if i.get('entrezgene')])
    uniprot2entrez = {}
    
    for query in mg_uniprot['out']:
        if query.get('entrezgene'):
            if  query['query'] in uniprot2entrez:
                uniprot2entrez[query['query']].append(query['entrezgene'])
            else:
                uniprot2entrez[query['query']] = [query['entrezgene']]

    print("looping through pharos data\n")
    ec = 0
    for row in pharos_data:
        edge = []
        uniprot = row.get('UniProt')
        chembl = row.get('Ligand ChEMBL ID')
        pubchem = row.get('Ligand PubChem ID')
        
        #Do we have a gene id for this target?
        
        if uniprot in uniprot2entrez:
            for gene in uniprot2entrez[uniprot]:
                #print([uniprot,gene])
                pharos_graph.add_node(int(gene),key='gene')
                edge.append(int(gene))
                gene_annotation = gene2go.get(int(gene))

                if gene_annotation is not None:
                    go_leafs = get_leafs(gene_ontology,[i['GO_ID'] for i in gene_annotation])

                    for annot in gene_annotation:
                        if annot['GO_ID'] in go_leafs:
                            pharos_graph.add_node(annot['GO_ID'],label='GO')
                            rel_types = annot.get('Qualfier')
                            if rel_types:
                                for rel in rel_types:
                                    pharos_graph.add_edge(int(gene),annot['GO_ID'],key=rel)
                            else:
                                pharos_graph.add_edge(int(gene),annot['GO_ID'],key="associated_with")
                
                #Use ChEMBL first if possible, unless pathway commons ChEBI only mapped to PubChem or Pharos only gave PubChem
                if chembl:
                    if pubchem and (('PUBCHEM:' + pubchem) in small_molecule_set):
                        pharos_graph.add_node(('PUBCHEM:' + pubchem),key='SmallMolecule')
                        edge.append(('PUBCHEM:' + pubchem))
                    else:
                        pharos_graph.add_node(('CHEMBL:' + chembl),key='SmallMolecule')
                        edge.append(('CHEMBL:' + chembl))
                elif pubchem:
                    pharos_graph.add_node(('PUBCHEM:' + pubchem),key='SmallMolecule')
                    edge.append(('PUBCHEM:' + pubchem))
                else:
                    continue

                if len(edge) == 2:
                    ec += 1
                    pharos_graph.add_edge(edge[0],edge[1],key="chemical-affects")
    print("Total edges added {0}".format(ec))
    print("Total unique edges in graph {0}".format(pharos_graph.number_of_edges()))
    return pharos_graph

def get_sif_genes(sif_data):
    ptc_genes = []
    for i in sif_data:
        if 'CHEBI' not in i[0]:
            ptc_genes.append(i[0])
        if 'CHEBI' not in i[2]:
            ptc_genes.append(i[2])
    return set(ptc_genes)

def process_pathway_commons_sif(sif_data,gene2go,gene_ontology,chebi2chembl,chebi2pubchem):
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
                    gene = int(symbol2entrez[sif[i]])
                    edge.append(gene)
                    if not gene in ptc_graph:

                        ptc_graph.add_node(gene,label='gene')
                    
                        gene_annotation = gene2go.get(gene)
                        if gene_annotation is not None:

                            go_leafs = get_leafs(gene_ontology,[i['GO_ID'] for i in gene_annotation])

                            for annot in gene_annotation:
                                if annot['GO_ID'] in go_leafs:
                                    ptc_graph.add_node(annot['GO_ID'],label='GO')
                                    rel_types = annot.get('Qualfier')
                                    if rel_types:
                                        for rel in rel_types:
                                            ptc_graph.add_edge(gene,annot['GO_ID'],key=rel)
                                    else:
                                        ptc_graph.add_edge(gene,annot['GO_ID'],key="associated_with")
            else:
                if sif[i].strip('CHEBI:') in chebi2chembl:
                    chembl_id = 'CHEMBL:' + chebi2chembl[sif[i].strip('CHEBI:')]
                    ptc_graph.add_node(chembl_id,label='SmallMolecule')
                    edge.append(chembl_id)
                elif sif[i].strip('CHEBI:') in chebi2pubchem:
                    pubchem_id = 'PUBCHEM:' + chebi2pubchem[sif[i].strip('CHEBI:')]
                    ptc_graph.add_node(pubchem_id,label='SmallMolecule')
                    edge.append(pubchem_id)
                else:
                    ptc_graph.add_node(sif[i],label='SmallMolecule')
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
            gene2go[assoc.DB_ID].append({'GO_ID':assoc.GO_ID,'Qualifier':assoc.Qualifier})
        else:
            gene2go[assoc.DB_ID] = [{'GO_ID':assoc.GO_ID,'Qualifier':assoc.Qualifier}]

    return gene2go


def get_leafs(ont,nodeset):
    
    annot_subgraph = ont.subgraph(nodeset)
    annot_leafs = [n for n in annot_subgraph.nodes() if annot_subgraph.in_degree(n)==0]

    return annot_leafs


def construct_disease_subgraph(gard_gene_df, gard_phen_df,gene2go,gene_ontology,phenotype_ontology):
    
    disease_gene_phen_subgraph = nx.MultiGraph()
    for dis in set(gard_gene_df.GARD_ID):
        genes = gard_gene_df[gard_gene_df.GARD_ID == dis]
        phens = gard_phen_df[gard_phen_df.GARD_ID == dis]
        
        disease_gene_phen_subgraph.add_node(dis,label='disease')
        
        for ind, row in genes.iterrows():
            
            if (row['Gene_ID'] is not None) & (pd.isna(row['Gene_ID']) == False):

                gene = int(row['Gene_ID'])
                
                disease_gene_phen_subgraph.add_node(gene,label='gene')

                disease_gene_phen_subgraph.add_edge(dis,gene,key="associated_with")
                
                gene_annotation = gene2go.get(gene)
                if gene_annotation is not None:

                    go_leafs = get_leafs(gene_ontology,[i['GO_ID'] for i in gene_annotation])

                    for annot in gene_annotation:
                        if annot['GO_ID'] in go_leafs:
                            disease_gene_phen_subgraph.add_node(annot['GO_ID'],label='GO')
                            rel_types = annot.get('Qualfier')
                            if rel_types:
                                for rel in rel_types:
                                    disease_gene_phen_subgraph.add_edge(gene,annot['GO_ID'],key=rel)
                            else:
                                disease_gene_phen_subgraph.add_edge(gene,annot['GO_ID'],key="associated_with")

        phen_leafs = get_leafs(phenotype_ontology,list(phens.HPO_ID))
        for hpo in phen_leafs:
            disease_gene_phen_subgraph.add_node(hpo,label='HPO')
            disease_gene_phen_subgraph.add_edge(dis,hpo,key="presents")
    
    return disease_gene_phen_subgraph


def main():
    project_dir = Path(__file__).resolve().parents[2]

    gene_ontology = obonet.read_obo(project_dir / sys.argv[1])#.to_undirected()
    phenotype_ontology  = obonet.read_obo(project_dir / sys.argv[2])#.to_undirected()
    
    hp_remove = nx.ancestors(phenotype_ontology,"HP:0000005")
    phenotype_ontology.remove_node("HP:0000005")
    phenotype_ontology.remove_nodes_from(hp_remove)

    nx.set_node_attributes(gene_ontology,'GO','label')
    nx.set_node_attributes(phenotype_ontology,'HPO','label')

    gene2go = get_goa(project_dir / 'data/raw/gene2go')

    #CHEBI - ChEMBL mapping from UNICHEM
    chebi2chembl={}
    with open(project_dir / 'data/raw/src1src7.txt','r') as chembl_chebi_file:
        chembl_chebi_file.readline()
        for line in chembl_chebi_file.readlines():
            data = line.strip().split('\t')
            chebi2chembl[data[1]] = data[0]
    
    #CHEBI - PubChem mapping from UNICHEM
    chebi2pubchem={}
    with open(project_dir / 'data/raw/src7src22.txt','r') as chebi_pubchem_file:
        chebi_pubchem_file.readline()
        for line in chebi_pubchem_file.readlines():
            data = line.strip().split('\t')
            chebi2pubchem[data[0]] = data[1]
    

    gard_gene_df = pd.read_csv(project_dir / 'data/raw/gard2gene.csv')
    
    gard_phen_df = pd.read_csv(project_dir / 'data/raw/gard2hpo.csv')
    gard_phen_df.drop(gard_phen_df[gard_phen_df['HPO_ID'].isin(hp_remove)].index, inplace = True)

    #Pathway commons chemical and gene/protein interaction data https://www.pathwaycommons.org/archives/PC2/v12/
    with open(project_dir / 'data/raw/PathwayCommons12.All.hgnc.sif','r') as ptc_file:
        ptc_sif = [i.strip().split('\t') for i in ptc_file.readlines()]

    pharos_data = []
    with open(project_dir / 'data/raw/pharos_all_target_ligands.csv','r') as pharos_ligand_file:
        reader = csv.DictReader(pharos_ligand_file)
        for row in reader:
            pharos_data.append(row)
    
    ptc_graph = process_pathway_commons_sif(ptc_sif,gene2go,gene_ontology,chebi2chembl,chebi2pubchem)
    small_molecule_set =  [n for n in ptc_graph.nodes if ptc_graph.nodes[n].get('label') ==  'SmallMolecule']

    pharos_graph = process_pharos_data(pharos_data,small_molecule_set,gene2go,gene_ontology)

    disease_subgraph = construct_disease_subgraph(gard_gene_df, gard_phen_df,gene2go,gene_ontology,phenotype_ontology)
    disease_subgraph.remove_nodes_from(list(nx.isolates(disease_subgraph)))

    disease_ontograph = nx.compose_all([disease_subgraph,phenotype_ontology.to_undirected(),gene_ontology.to_undirected()])
    disease_ontograph.remove_nodes_from(list(nx.isolates(disease_ontograph)))

    disease_ontograph = nx.compose_all([disease_ontograph,ptc_graph,pharos_graph])

    with open(project_dir / 'data/processed/disease_ontograph.pkl', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(disease_ontograph, f, pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    main()
