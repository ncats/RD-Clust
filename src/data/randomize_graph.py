import sys
import networkx as nx
import random
import pickle
from pathlib import Path

#import pickle5 as p

def random_reference_multigraph(G, niter=1, connectivity=True):
    """
    Source copied from: https://networkx.org/documentation/stable/_modules/networkx/algorithms/smallworld.html#random_reference
    """
    if len(G) < 4:
        raise nx.NetworkXError("Graph has fewer than four nodes.")
    if len(G.edges) < 2:
        raise nx.NetworkXError("Graph has fewer that 2 edges")

    from networkx.utils import cumulative_distribution, discrete_sequence

    local_conn = nx.connectivity.local_edge_connectivity

    G = G.copy()
    keys, degrees = zip(*G.degree())  # keys, degree
    cdf = cumulative_distribution(degrees)  # cdf of degree
    nnodes = len(G)
    nedges = nx.number_of_edges(G)
    niter = niter * nedges
    ntries = int(nnodes * nedges / (nnodes * (nnodes - 1) / 2))
    swapcount = 0

    for i in range(niter):
       if i % 1000 ==0:
           print(f"Completed {i} iterations which is {i/niter * 100} percent")
        n = 0
        while n < ntries:
            # pick two random edges without creating edge list
            # choose source node indices from discrete distribution
            (ai, ci) = discrete_sequence(2, cdistribution=cdf, seed=random)
            if ai == ci:
                continue  # same source, skip
            a = keys[ai]  # convert index to label
            c = keys[ci]
            # choose target uniformly from neighbors
            b = random.choice(list(G.neighbors(a)))
            d = random.choice(list(G.neighbors(c)))
            if b in [a, c, d] or d in [a, b, c]:
                continue  # all vertices should be different

            G.add_edge(a, d)
            G.add_edge(c, b)
            G.remove_edge(a, b)
            G.remove_edge(c, d)

            # Check if the graph is still connected
            if connectivity and local_conn(G, a, b) == 0:
                # Not connected, revert the swap
                G.remove_edge(a, d)
                G.remove_edge(c, b)
                G.add_edge(a, b)
                G.add_edge(c, d)
            else:
                swapcount += 1
                break
        n += 1
    return G


def main():
    project_dir = Path(__file__).resolve().parents[2]
    graph_file = sys.argv[1]
    iteration = sys.argv[2]

    #with open(graph_file, 'rb') as f:
    #     original_graph = p.load(f)
    original_graph =nx.barabasi_albert_graph(100,5)
    random_graph = random_reference_multigraph(original_graph, niter=1)
    nx.write_edgelist(original_graph, project_dir / "data/random_graphs/original_graph.edgelist")
    nx.write_edgelist(random_graph, project_dir / "data/random_graphs/random_graph.edgelist")

    #with open( project_dir / f"data/random_graphs/random_ontograph_{iteration}.pkl", 'wb') as f:
    #    # Pickle the 'data' dictionary using the highest protocol available.
    #    pickle.dump(random_graph, f, pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    main()
