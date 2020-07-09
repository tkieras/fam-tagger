import networkx as nx
import matplotlib.pyplot as plt
from family_resemblance_tagger.common import database



def jaccard(A, B):
    A = set(A.keys())
    B = set(B.keys())
    num = len(A.intersection(B))
    denom = len(A.union(B))
    return num/denom

def weighted_jaccard(A, B):
    A_keys = set(A.keys())
    B_keys = set(B.keys())
    key_int = A_keys.intersection(B_keys)
    key_union = A_keys.union(B_keys)
    num = sum([A[k] + B[k] for k in key_int])
    denom = sum([A.get(k, 0) + B.get(k, 0) for k in key_union])
    return num/denom

def similarity(A, B):
    return weighted_jaccard(A, B)


def init_base_network(wg):
    G = nx.Graph()

    for i in wg.keys():
        for j in wg.keys():
            if i != j:
                G.add_edge(wg[i]["checksum"], wg[j]["checksum"], 
                    weight=similarity(wg[i]["keywords"], wg[j]["keywords"]))

    return G

def init_subgraph(G, threshold):
    def threshold_fn(u, v):
        w = G[u][v]["weight"]
        if w > threshold:
            return True
        else:
            return False

    SG = nx.subgraph_view(G, filter_edge=threshold_fn)
    return SG

def x_subgraph(G, threshold):
    SG = nx.Graph()

    n = len(G.nodes)
    for u in G.nodes:
        for v in G.nodes:
            if u == v:
                continue
            w = G[u][v]["weight"]
            if w > threshold:
                SG.add_edge(u, v, weight=w)

    return SG


# def init_tag_net(wg):
#     G = nx.Graph()

#     n = len(wg)

#     for i in range(n):
#         for j in range(len(wg[i]["keywords"])):
#             G.add_edge(wg[i]["filepath"], wg[i]["keywords"][j])
#         for j in range(n):
#             if(i != j):
#                 G.add_edge(wg[i]["filepath"], wg[j]["filepath"], 
#                     weight=similarity(wg[i]["keywords"], wg[j]["keywords"]))

#     return G

def draw_network(G):
    pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(G, pos, edge_color="black", width=1, lindewiths=1,\
        node_size=100, node_color='green', alpha=0.3)
    #labels = {node:node for node in G.nodes()})

   # nx.draw_networkx_edge_labels(G, pos, edge_labels={(edge[0], edge[1]): round(edge[2]["weight"], 2)
    #    for edge in G.edges(data=True)}, font_color="red")
    plt.axis('off')
    plt.show()

def plot_similarities(G):
    y_vals = []
    weights = nx.get_edge_attributes(G, "weight")
    for edge in G.edges:
        w = weights[edge]
        y_vals.append(w)

    x_vals = list(range(1, len(y_vals)+1))

    y_vals = sorted(y_vals, reverse=True)
    plt.figure()
    plt.scatter(x_vals, y_vals, marker="o", s=10, alpha=0.3, color="blue")
    plt.title("Pairwise Node Similarity Distribution")
    plt.ylabel("Similarity")
    plt.xlabel("Edge Index")
    plt.grid()
    plt.show()


def find_communities(G):
    #return nx.algorithms.community.greedy_modularity_communities(G)
    #return nx.algorithms.community.k_clique_communities(G, k=3)
    return nx.algorithms.community.label_propagation_communities(G)


def report_communities(G, SG, comm):
    pass

def detect_communities(data, sim_thresh=0.1):
    G = init_base_network(data)
    #plot_similarities(G)
    SG = init_subgraph(G, sim_thresh)
    comm = list(find_communities(SG))
    return comm

def main():
    data = database.load_data()
       
    print(detect_communities(data))
    
    


if __name__=="__main__":
    main()