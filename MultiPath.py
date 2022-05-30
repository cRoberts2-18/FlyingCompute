import itertools
import copy
from multiprocessing import connection
from posixpath import supports_unicode_filenames
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



def pathCompute(teams,nodepath,edgepath):
    # Grab edge list data
    edgelist = pd.read_csv(edgepath)

    # Grab node list data
    nodelist = pd.read_csv(nodepath)

    g=createGraph(edgelist,nodelist)

    teamLocations={}
    teamEdgeList={}

    for i in range(1,teams+1):
        teamLocations[i]="start"
        teamEdgeList[i]=[]

    complete=False
    freeMove=False

    connections={}
    edges=[]
    nodes=[]
    for i, row in edgelist.iterrows():
        edges.append([row[0],row[1],0])

    for i, row in nodelist.iterrows():
        nodes.append([row[0],(row[1],row[2])])

    for i in range(len(nodes)):
        templist=[]
        for j in range(len(edges)):
            if edges[j][0]==nodes[i][0]:
                templist.append(edges[j][1])
            elif edges[j][1]==nodes[i][0]:
                templist.append(edges[j][0])
        connections[nodes[i][0]]=templist


    while complete==False:
        
        complete=True
        for i in range(len(edges)):
            if edges[i][2]==0:
                complete=False
        if complete==False:
            for i in range(1,teams+1):
                location=teamLocations[i]
                freeMove=False
                for j in range(len(edges)):
                        if edges[j][0]==location or edges[j][1]==location:
                            if edges[j][2]==0:
                                freeMove=True
                if freeMove==True:
                    for j in range(len(edges)):
                        if edges[j][2]==0:
                            if edges[j][0]==location:
                                teamLocations[i]=edges[j][1]
                                
                                teamEdgeList[i].append((edges[j][0],edges[j][1]))
                                edges[j][2]+=1
                                break
                            elif edges[j][1]==location:
                                teamLocations[i]=edges[j][0]
                                teamEdgeList[i].append((edges[j][1],edges[j][0]))
                                
                                edges[j][2]+=1
                                break
                else:
                    missingMoves=[]
                    edgeFound=False
                    for j in range(len(edges)):
                        if edges[j][2]==0:
                            missingMoves.append(edges[j])

                    for j in range(len(missingMoves)):
                        if missingMoves[j][0] in connections[location]:
                            for k in range(len(edges)):
                                if edges[k][0]==missingMoves[j][0] and edges[k][1]==location:
                                    teamLocations[i]=edges[k][0]
                                    teamEdgeList[i].append((edges[k][1],edges[k][0]))
                                    edgeFound=True
                                    edges[k][2]+=1
                                    break
                                elif edges[k][1]==missingMoves[j][0] and edges[k][0]==location:
                                    teamLocations[i]=edges[k][1]
                                    teamEdgeList[i].append((edges[k][0],edges[k][1]))
                                    edgeFound=True
                                    edges[k][2]+=1
                                    break
                            break
                        elif missingMoves[j][1] in connections[location]:
                            for k in range(len(edges)):
                                if edges[k][0]==missingMoves[j][0] and edges[k][1]==location:
                                    teamLocations[i]=edges[k][0]
                                    teamEdgeList[i].append((edges[k][1],edges[k][0]))
                                    edgeFound=True
                                    edges[k][2]+=1
                                    break
                                elif edges[k][1]==missingMoves[j][0] and edges[k][0]==location:
                                    teamLocations[i]=edges[k][1]
                                    teamEdgeList[i].append((edges[k][0],edges[k][1]))
                                    edgeFound=True
                                    edges[k][2]+=1
                                    break
                            break
                    
                    if edgeFound==False and len(missingMoves)>0:
                        # define array for use later
                        shortPathPairs=[]
                        # select an untraversed path
                        edgeSearch=missingMoves[0]
                        # get each node the path is connected to
                        target1=edgeSearch[0]
                        target2=edgeSearch[1]
                        # compute the distance to each node
                        distance1=nx.dijkstra_path_length(g,location,target1,weight="distance")
                        distance2=nx.dijkstra_path_length(g,location,target2,weight="distance")
                        # get the shortest path to the node which is closer and create a list of node pairs
                        if distance1<=distance2:
                            shortPath = nx.shortest_path(g, location, target1, weight='distance')
                            shortPathPairs = list(zip(shortPath[:-1], shortPath[1:]))
                        elif distance2<distance1:
                            shortPath = nx.shortest_path(g, location, target2, weight='distance')
                            shortPathPairs = list(zip(shortPath[:-1], shortPath[1:]))
                        
                        for j in range(len(shortPathPairs)):
                            for k in range(len(edges)):
                                if edges[k][0] in shortPathPairs[j] and edges[k][1] in shortPathPairs[j]:
                                    if edges[k][0]==teamLocations[i]:
                                        teamLocations[i]=edges[k][1]
                                        teamEdgeList[i].append((edges[k][0],edges[k][1]))
                                        edges[k][2]+=1
                                    elif edges[k][1]==teamLocations[i]:
                                        teamLocations[i]=edges[k][0]
                                        teamEdgeList[i].append((edges[k][1],edges[k][0]))
                                        edges[k][2]+=1
                        

    return(teamEdgeList)
            
    
            

                        

            
