#!/usr/bin/env python3
import sys
import pickle
from pathlib import Path
import random
import networkx as nx
from collections import Counter
#TODO: add bias parameters
def run_random_sequence(G, nodes, walk_len, num_walks):
    graph_nodes=list(G.nodes())
    graph_edges=[i for i in list(G.edges)]
    pairs = []

    for count, node in enumerate(nodes):

        if G.degree(node) == 0:
            continue
        for i in range(num_walks):
            random_nodes = random.sample(graph_nodes, walk_len)
            random_edges = random.sample(graph_edges, walk_len)
            random_types = [random.choice(list(G.get_edge_data(t[0], t[1]).keys())) for t in random_edges]
            walk_accumulate = [node]
            for j in range(walk_len):
                walk_accumulate.append(random_types[j])
                walk_accumulate.append(random_nodes[j])

            pairs.append(walk_accumulate)
    return pairs

def main():

    #TODO: command line argparser
    graph_file = sys.argv[1]
    walk_file = sys.argv[2]
    walks_per_disease = int(sys.argv[3])
    walk_len = int(sys.argv[4])

    project_dir = Path(__file__).resolve().parents[2]

    #TODO:checks on the graph
    with open(project_dir / graph_file, 'rb') as f:
        disease_ontograph = pickle.load(f)

    diseases = [n for n in disease_ontograph.nodes if disease_ontograph.nodes[n].get('label') ==  'disease']

    pairs = run_random_sequence(disease_ontograph,diseases,walk_len,walks_per_disease)

    #TODO: confirm walk_file
    with open(project_dir / walk_file, "a") as fp:
        for p in pairs:
            for sub_p in p:
                fp.write(str(sub_p)+" ")
            fp.write("\n")

if __name__=="__main__":
    main()
