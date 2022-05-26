import itertools
import copy
from turtle import distance
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
import imageio
import os

def createGraph(edgelist, nodelist):
    # create an empty graph
    g=nx.Graph()

    # add edges and edge atributes
    for i, elrow in edgelist.iterrows():
        g.add_edge(elrow[0], elrow[1], **elrow[2:].to_dict())


    # Add node attributes
    for i, nlrow in nodelist.iterrows():
        nx.set_node_attributes(g, {nlrow['id']:  nlrow[1:].to_dict()})

    return g

def plotGraph(g):
    # Define node positions data structure (dict) for plotting
    node_positions = {node[0]: (node[1]['X'], -node[1]['Y']) for node in g.nodes(data=True)}

    # Define data structure (list) of edge colors for plotting
    edge_colors = [e[2]['color'] for e in list(g.edges(data=True))]

    # plot graph
    plt.figure(figsize=(8,6))
    nx.draw(g, pos=node_positions, edge_color=edge_colors, node_size=10, node_color="black")
    plt.title("Test Graph", size=15)
    plt.show()

def findOddNodePairs(graph):
    # creates a list of all nodes of odd degree
    oddNodes = [v for v, d in g.degree() if d%2==1]
    oddNodePairs = list(itertools.combinations(oddNodes,2))
    return oddNodePairs

def ShortestPath(graph, OddPairs, name):
    distances={}
    for i in OddPairs:
        distances[i] = nx.dijkstra_path_length(graph,i[0],i[1],weight=name)
        print(distances[i])
    return distances

def completeGraph(shortPath, flip_weights=True):
    g=nx.Graph()
    for i, j in shortPath.items():
        w= - j if flip_weights else j
        g.add_edge(i[0], i[1], **{"distance": j, "weight": w})            

    return g

def augmentGraph(graph, minWeightPairs):
    augmentedGraph=nx.MultiGraph(graph.copy())
    for i in minWeightPairs:
        augmentedGraph.add_edge(i[0], i[1], **{'distance': nx.dijkstra_path_length(graph, i[0], i[1]), 'trail': 'augmented'})

    return augmentedGraph

def eulerianCircuit(graph, augGraph, starting_node=None):
    eulerCircuit=[]
    naiveCircuit=list(nx.eulerian_circuit(augGraph, source=starting_node))
    for i in naiveCircuit:
        edgeData=augGraph.get_edge_data(i[0],i[1])
        
        if edgeData[0]['trail'] != "augmented":
            edgeAtt=graph[i[0]][i[1]]
            eulerCircuit.append((i[0], i[1], edgeAtt))
        
        else:
            augPath = nx.shortest_path(graph, i[0], i[1], weight='distance')
            augPathPairs = list(zip(augPath[:-1], augPath[1:]))
            print(augPath)
            print(augPathPairs)
            for j in augPathPairs:
                edgeAtt=graph[j[0]][j[1]]
                eulerCircuit.append((j[0], j[1], edgeAtt))


    return eulerCircuit

def solutionEdgeList(circuit):
    cppEdges={}
    for i,j in enumerate(circuit):
        edge=frozenset([j[0],j[1]])
        if edge in cppEdges:
            cppEdges[edge][2]['sequence'] += ', ' + str(i)
            cppEdges[edge][2]['visits']+=1
        else:
            cppEdges[edge]=j
            cppEdges[edge][2]['sequence']=str(i)
            cppEdges[edge][2]['visits']=1 


    return list(cppEdges.values())

def plotSolution(solutionGraph):
    plt.figure(figsize=(14, 10))
    node_positions = {node[0]: (node[1]['X'], -node[1]['Y']) for node in g.nodes(data=True)}
    edge_colors = [e[2]['color'] for e in solutionGraph.edges(data=True)]
    nx.draw_networkx(solutionGraph, pos=node_positions, node_size=10, node_color='black', edge_color=edge_colors, with_labels=False, alpha=0.5)

    bbox = {'ec':[1,1,1,0], 'fc':[1,1,1,0]}  # hack to label edges over line (rather than breaking up line)
    edge_labels = nx.get_edge_attributes(solutionGraph, 'sequence')
    nx.draw_networkx_edge_labels(solutionGraph, pos=node_positions, edge_labels=edge_labels, bbox=bbox, font_size=6)

    plt.axis('off')
    plt.show()

def makePNGs(eulerCircuit, g):
    visit_colors = {1:'black', 2:'red'}
    edge_cnter = {}
    g_i_edge_colors = []
    for i, e in enumerate(eulerCircuit, start=1):

        edge = frozenset([e[0], e[1]])
        if edge in edge_cnter:
            edge_cnter[edge] += 1
        else:
            edge_cnter[edge] = 1

        # Full graph (faded in background)
        nx.draw_networkx(g, pos=node_positions, node_size=6, node_color='gray', with_labels=False, alpha=0.07)

        # Edges walked as of iteration i
        euler_circuit_i = copy.deepcopy(eulerCircuit[0:i])
        for i in range(len(euler_circuit_i)):
            edge_i = frozenset([euler_circuit_i[i][0], euler_circuit_i[i][1]])
            euler_circuit_i[i][2]['visits_i'] = edge_cnter[edge_i]
        g_i = nx.Graph(euler_circuit_i)
        g_i_edge_colors = [visit_colors[e[2]['visits_i']] for e in g_i.edges(data=True)]

        nx.draw_networkx_nodes(g_i, pos=node_positions, node_size=6, alpha=0.6, node_color='lightgray', linewidths=0.1)
        nx.draw_networkx_edges(g_i, pos=node_positions, edge_color=g_i_edge_colors, alpha=0.8)

        plt.axis('off')
        plt.savefig('C:/Users/callu/Desktop/21COD290 - Thesis Project/Flying Compute/figures/img{}.png'.format(i), dpi=120, bbox_inches='tight')
        plt.close()

def makeGIF(imagePath, movieFilename, fps=5):
    # sorting filenames in order
    filenames = glob.glob(imagePath + 'img*.png')
    filenamesSortIndices = np.argsort([int(os.path.basename(filename).split('.')[0][3:]) for filename in filenames])
    filenames = [filenames[i] for i in filenamesSortIndices]

    # make movie
    with imageio.get_writer(movieFilename, mode='I', fps=fps) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)




#program start

# Grab edge list data
edgelist = pd.read_csv('edgelistSample.csv')

# Grab node list data
nodelist = pd.read_csv('nodelistSample.csv')

#generate a graph and determine the positions of each node in space
g=createGraph(edgelist,nodelist)
node_positions = {node[0]: (node[1]['X'], -node[1]['Y']) for node in g.nodes(data=True)}

#generate pairs of odd nodes and find the shortest path between each one
oddNodePairs=findOddNodePairs(g)
pairShortPath=ShortestPath(g,oddNodePairs,"distance")
#generate a complete graph of each odd node pairing
completeOdd=completeGraph(pairShortPath,flip_weights=True)

#take these odd pairs and augment the intial graph
oddMatching = nx.algorithms.max_weight_matching(completeOdd, True)
augGraph=augmentGraph(g,oddMatching)

#generate an eurlerian circuit starting at the node named start
eulerCircuit=eulerianCircuit(g, augGraph, "start")

#plot the eulerian circuit
edgelist= solutionEdgeList(eulerCircuit)
solutionGraph=nx.Graph(edgelist)
plotSolution(solutionGraph)

#makePNGs(eulerCircuit,solutionGraph)
#makeGIF('C:/Users/callu/Desktop/21COD290 - Thesis Project/Flying Compute/figures/', 'figures/cpp_route_animation.gif', fps=3)





