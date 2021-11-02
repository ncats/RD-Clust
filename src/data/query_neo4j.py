import sys
import pickle
from pathlib import Path
import pandas as pd
from neo4j import GraphDatabase
import mygene


def get_gene_data(session):

    gard_gene_query = \
    """
    MATCH p=(d:DATA)-[:PAYLOAD]->(:S_GARD)-[:R_exactMatch|:R_equivalentClass]-(m:S_MONDO) WHERE d.is_rare = TRUE
    OPTIONAL MATCH q=(m)-[:R_exactMatch|:R_equivalentClass]-(:S_ORDO_ORPHANET)-[e:R_rel{name:'disease_associated_with_gene'}]->(:S_ORDO_ORPHANET)<-[:PAYLOAD]-(o:DATA)
    RETURN DISTINCT d.gard_id as `GARD_ID`,d.name as `GARD_Disease`,e.DisorderGeneAssociationType as `Disease_Gene_Association`,
    o.symbol as `Gene_Symbol`,o.label as `Gene_Name`, o.hasDbXref as `Gene_Refs`
    ORDER BY d.gard_id
    """

    gard_gene_res = session.run(gard_gene_query)
    #Convert to dict
    gard_gene_data = [dict(record) for record in gard_gene_res]

    #Extract the external db references
    for gd in gard_gene_data:
        if gd['Gene_Refs'] is not None:
            for ref_id in gd['Gene_Refs']:
                ref = ref_id.split(':')
                gd[ref[0]] = ref[1]
    
    gard_gene_df = enrich_gene_ids(pd.DataFrame(gard_gene_data))

    return gard_gene_df

def get_phen_data(session):
    gard_phen_query = \
    """
    MATCH r=(d:DATA)-[:PAYLOAD]->(n:S_GARD)-[:R_hasPhenotype]->(p:S_HP)<-[:PAYLOAD]-(z)
    WHERE d.is_rare=true
    RETURN DISTINCT d.gard_id as `GARD_ID`, d.name as `GARD_Disease`,z.id as `HPO_ID`, z.label as `HPO_Phenotype`
    ORDER BY d.gard_id
    """

    gard_phen_res = session.run(gard_phen_query)
    gard_phen_data = [dict(record) for record in gard_phen_res]
    gard_phen_df = pd.DataFrame(gard_phen_data)

    return gard_phen_df


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
    uri = "bolt://disease.ncats.io:80"
    driver = GraphDatabase.driver(uri, auth=("neo4j", ""))
    session = driver.session()
    
    project_dir = Path(__file__).resolve().parents[2]

    gard_gene_df = get_gene_data(session)
    gard_phen_df = get_phen_data(session)

    gard_gene_df.to_csv(project_dir / 'data/gard2gene.csv',index=False)
    gard_phen_df.to_csv(project_dir / 'data/gard2hpo.csv',index=False)

if __name__=="__main__":
    main()