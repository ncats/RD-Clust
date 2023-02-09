import sys
import pickle
from pathlib import Path
import pandas as pd
from neo4j import GraphDatabase

def get_gene_disease_pubs(session):
    gard_gd_query = \
"""
MATCH r=(d:Disease)-[:MENTIONED_IN]->(a:Article)<-[:ANNOTATION_FOR]-(p:PubtatorAnnotation{infons_type:'Gene'}) 
RETURN r LIMIT 100
"""

    gard_gd_res = session.run(gard_gd_query)
    #Convert to dict
    gard_gd_data = [dict(record) for record in gard_gd_res]
    
    gard_gd_df = pd.DataFrame(gard_gd_data)

    return  gard_gd_df


def main():
    uri = "bolt+s://rdip2.ncats.io/:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", ""))
    session = driver.session()
    
    project_dir = Path(__file__).resolve().parents[2]

    gard_gd_df = get_gene_disease_pubs(session)

    gard_gd_df.to_csv(project_dir / 'data/raw/gard-gene-pubs.csv',index=False)

if __name__=="__main__":
    main()