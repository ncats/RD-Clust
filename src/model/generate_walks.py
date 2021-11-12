#!/usr/bin/env python3
import sys
import pickle
from pathlib import Path
import random
import networkx as nx

#TODO: add bias parameters
def run_random_walks(G, nodes, walk_len, num_walks):
    #print("now we start random walk")

    pairs = []
    for count, node in enumerate(nodes):

        if G.degree(node) == 0:
            continue
        for i in range(num_walks):
            curr_node = node
            walk_accumulate=[]
            for j in range(walk_len):
                next_node = random.choice(list(G.neighbors(curr_node)))

                edge_type = random.choice(list(G.get_edge_data(curr_node, next_node).keys()))

                if curr_node == node:
                    walk_accumulate.append(curr_node)
                walk_accumulate.append(edge_type)
                walk_accumulate.append(next_node)

                curr_node = next_node

            pairs.append(walk_accumulate)

    return(pairs)


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

    pairs = run_random_walks(disease_ontograph,diseases,walk_len,walks_per_disease)

    #TODO: confirm walk_file
    with open(project_dir / walk_file, "a") as fp:
        for p in pairs:
            for sub_p in p:
                fp.write(str(sub_p)+" ")
            fp.write("\n")

if __name__=="__main__":
    main()