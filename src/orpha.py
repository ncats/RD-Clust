from neo4j import GraphDatabase
import sys

uri = "bolt://disease.ncats.io:80"
driver = GraphDatabase.driver(uri, auth=("neo4j", ""))

def run_query(tx, orpha):
    label = ''
    xrefs = set()
    genes = set()
    for row in tx.run("match p=(d)-[:PAYLOAD]->(o:S_ORDO_ORPHANET)-[:R_exactMatch|:R_equivalentClass]-(:S_MONDO)-[:R_exactMatch|:R_equivalentClass]-(m)<-[:PAYLOAD]-(z) \
    where d.notation='ORPHA:%d' and not m:TRANSIENT \
    optional match (o)-[e:R_rel{name:'disease_associated_with_gene'}]->()<-[:PAYLOAD]-(g) \
    where e.DisorderGeneAssociationType in ['Disease-causing germline mutation(s) in',\
    'Disease-causing germline mutation(s) (gain of function) in',\
    'Disease-causing germline mutation(s) (loss of function) in'] \
    RETURN d as orpha, z, g.symbol as gene" % orpha):
        label = row['orpha']['label']
        z = row['z']
        g = row['gene']
        if g != None:
            genes.add(g)
        if 'notation' in z:
            xrefs.add(z['notation'])
        elif 'gard_id' in z:
            xrefs.add(z['gard_id'])
        elif 'id' in z:
            xrefs.add(z['id'])
        
    print('%d\t%s\t%s\t%s' % (orpha, label,
                              ','.join(list(genes)), ','.join(list(xrefs))))
        
        
with driver.session() as session, open('Orphanet IDs_CNH_CuratedList.txt') as f:
    f.readline()
    print('Orpha\tLabel\tGenes\tXrefs')
    for line in f.readlines():
        orpha = int(line.strip())
        run_query(session, orpha)
    session.close()
