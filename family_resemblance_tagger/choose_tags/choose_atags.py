import networkx as nx 
from pprint import pprint
import math
from family_resemblance_tagger.common import database, config



def pull_working_group(data, comm):
    wg = {}

    for key in comm:
        wg[key] = data[key]

    return wg

def cost(count, weight):
    base_cost = math.ceil(1/count * 100)
    weight = math.ceil(1/weight / 10)
    return math.ceil(base_cost + config.dict["cost_alpha"] * weight)

def init_flow_problem(working_group, flow_demand):
    G = nx.DiGraph()

    n = len(working_group.keys())
    source = "Source"
    sink = "Sink"


    G.add_node(source, demand=(-(flow_demand*n)))
    
    if not config.dict["flow_constraint_full_coverage"]:
        G.add_node(sink, demand=(flow_demand*n))

    ptag_counts = {}
    ptag_weights = {}
   
    filepath_sink = []
    source_ptag = []

    for key, value in working_group.items():
        if not config.dict["flow_constraint_full_coverage"]:
            using_demand = 0
        else:
            using_demand = flow_demand
        G.add_node(key, demand=using_demand) ## force each filepath node to contribute something
        filepath_sink.append((key, sink))

        for index, ptag in enumerate(value["ptags"].keys()):
            ptag_counts[ptag] = ptag_counts.get(ptag, 0) + 1
            ptag_weights[ptag] = ptag_weights.get(ptag, 0) + value["ptags"][ptag]
            G.add_edge(ptag, key, capacity=1)
            source_ptag.append((source, ptag))

    G.add_edges_from(filepath_sink)

    for edge in source_ptag:
        G.add_edge(edge[0], edge[1], weight=cost(ptag_counts[edge[1]], ptag_weights[edge[1]]))
       # print("cost is {} for ptag: {}".format(cost(ptag_counts[edge[1]], ptag_weights[edge[1]]), edge[1]))
    
    
    return G


def solve_flow_problem(G):
    _, flow_results = nx.algorithms.network_simplex(G)
    
    return flow_results


def extract_atags(flow_results):
    atags = []
    for src, value in flow_results.items():
        for dst, flow in value.items():
            if src == "Source" and flow > 0:
                atags.append(dst)
    return sorted(atags)



def choose_atags(comm, data, flow_demand=1):
    wg = pull_working_group(data, comm)

    flow_problem = init_flow_problem(wg, flow_demand)
    flow_results = solve_flow_problem(flow_problem)
    atags = extract_atags(flow_results)
    return atags



def main():
    data = database.load_data()

    flow_problem = init_flow_problem(data, 2)
    flow_results = solve_flow_problem(flow_problem)
    atags = extract_atags(flow_results)
    print(atags)



if __name__=="__main__":
    main()