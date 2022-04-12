#!/usr/bin/env python3

import sys
import pickle
from pathlib import Path
import pandas as pd
import mygene


def enrich_gene_ids(gard_gene_df):

    print(gard_gene_df.columns)
    gard_symbol_hgnc = gard_gene_df[
        (gard_gene_df['Gene_Symbol'].isnull() == False) & 
        (gard_gene_df['HGNC'].isnull() == False)
        ][['Gene_Symbol','HGNC']].drop_duplicates()

    #Some dictionaries for convenient mapping later
    sym2hgnc = {row['Gene_Symbol']:row['HGNC'] for i,row in gard_symbol_hgnc.iterrows()}
    hgnc2sym = {row['HGNC']:row['Gene_Symbol'] for i,row in gard_symbol_hgnc.iterrows()}

    #query mygene
    mg = mygene.MyGeneInfo()
    mg_hgnc = mg.querymany([i for i in gard_symbol_hgnc['HGNC']], scopes='hgnc', fields='entrezgene', species='human')
    hgnc2ncbi = {i.get('query') : i.get('entrezgene') for i in mg_hgnc if i.get('entrezgene') is not None}

    no_hgnc_hits = gard_symbol_hgnc[(gard_symbol_hgnc['HGNC'].isin(hgnc2ncbi.keys())==False)]
    mg_symbol = mg.querymany([i for i in no_hgnc_hits['Gene_Symbol']], scopes='symbol', fields='entrezgene', species='human')
    hgnc2ncbi.update({sym2hgnc.get(i.get('query')) : i.get('entrezgene') for i in mg_symbol if i.get('entrezgene') is not None})

    sym2ncbi = {hgnc2sym[i]:hgnc2ncbi[i] for i in hgnc2ncbi.keys()}
    sym_hits = sym2ncbi.keys()

    mg_symbol = mg.querymany(
        list(
            gard_gene_df[
                (gard_gene_df['Gene_Symbol'].isnull()==False) &
                (gard_gene_df['Gene_Symbol'].isin(sym_hits)==False)
                ]['Gene_Symbol']
            ),
            scopes='symbol', fields='entrezgene', species='human')

    sym2ncbi.update({i.get('query') : i.get('entrezgene') for i in mg_symbol if i.get('entrezgene') is not None})

    gard_gene_df['Gene_ID'] = [sym2ncbi.get(sym) for sym in gard_gene_df['Gene_Symbol']]

    return gard_gene_df


def main():
    
    project_dir = Path(__file__).resolve().parents[2]

    gard_gene_raw = pd.read_csv(project_dir / 'data/raw/disease_genes_palantir.csv')
    gard_phen_raw =  pd.read_csv(project_dir / 'data/raw/disease_phenotypes_palantir.csv')

    
    gard_gene_raw = gard_gene_raw[['curie','label','genes_association_type','genes_gene_symbol','genes_curie']]
    gard_gene_raw = gard_gene_raw[gard_gene_raw['genes_curie'].isnull()==False]
    gard_gene_raw['HGNC'] = gard_gene_raw.apply(lambda row:row.genes_curie.split(':')[1],axis=1)
    gard_gene_raw.drop('genes_curie',axis=1,inplace=True)
    gard_gene_raw.columns = ['GARD_ID','GARD_Disease','Disease_Gene_Association','Gene_Symbol','HGNC']

    gard_gene_df = enrich_gene_ids(gard_gene_raw)
    gard_gene_df.to_csv(project_dir / 'data/raw/gard2gene.csv',index=False)

    #GARD_ID,GARD_Disease,HPO_ID,HPO_Phenotype
    
    gard_phen_raw = gard_phen_raw[['curie','label','phenotypes_curie','phenotypes_label']]
    gard_phen_df = gard_phen_raw[gard_phen_raw['phenotypes_curie'].isnull()==False]
    gard_phen_df.columns = ['GARD_ID','GARD_Disease','HPO_ID','HPO_Phenotype']
    gard_phen_df.to_csv(project_dir / 'data/raw/gard2hpo.csv',index=False)

if __name__=="__main__":
    main()