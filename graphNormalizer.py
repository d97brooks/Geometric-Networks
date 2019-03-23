
import networkx as nx
import collections
from networkx.algorithms import community
import random
import operator
import time
from ast import literal_eval
import math
import sys
DIM = 2
city = ""

def main():
    city = sys.argv[1] ## get city file from cmd
    RADIUS = .001235177866 ## 450 feet in latitude -- 1/69 * 1/5280 * 300
    # start = time.time()
    # print("Loading graph " + city[:-4] + "...")
    # positions = open(city, 'r')
    # positions = literal_eval(positions.read())
    #     #print(positions)
    # G = nx.random_geometric_graph(len(positions), RADIUS, DIM, pos=positions)
    # end = time.time()
    # hours, rem = divmod(end-start, 3600)
    # minutes, seconds = divmod(rem, 60)
    # print("Graph Load Time:" + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    # #nx.write_gml(G, city[:-4]+".gml")
    # print("#ofNodes: " + str(len(positions)) + ", #ofEdges: " + str(nx.number_of_edges(G)) )
    # print("Done.")
    print("Normalizing graph of " + city)
    f = open(city, "r")
    G = f.read()
    f.close()
    positions = dict(literal_eval(G))
    print("num nodes:  " + str(len(positions)))
    time.sleep(10)
    xMin = positions[1][0]
    xMax = positions[0][0]
    yMax = positions[0][1]
    yMin = positions[1][1]
    
    for node in positions:
        if positions[node][0] > xMax:
           xMax = positions[node][0]
        elif positions[node][0] < xMin:
            xMin = positions[node][0]
        if positions[node][1] > yMax: # less than because the coord. is negative
            yMax = positions[node][1]
        elif positions[node][1] < yMin: # again, flipped because negative
            yMin = positions[node][1]
    print("Min X coordinate: " + str(xMin) + "  Max X coordinate: " + str(xMax))
    print("Min Y coordinate: " + str(yMin) + "  Max Y coordinate: " + str(yMax))
    
    ## calculate the diagonal for normalization
    diagonal = math.hypot((xMax - xMin), (yMax - yMin))
    print("Diagonal = " + str(diagonal))

    
    ## Min Max Normalization
    for node in positions:
        positions[node] = (((positions[node][0] - xMin) / (diagonal)),((positions[node][1] - yMin) / (diagonal)))
    
    ## Normalize Radius!!
    RADIUS = (RADIUS) / (diagonal)
    print("Normalized Radius based on diagonal: " + str(RADIUS))
    

    for x in positions:
        #if (positions[x][0] == 0) or (positions[x][1] == 0) or (positions[x][0] == 1) or (positions[x][1] == 1):
        print(positions[x])
        #time.sleep(1)

    f = open("graphs/" + city[:-4] + "_radius.txt", 'w')
    f.write(str(RADIUS))
    f.close()
    print("Generating Normalized Graph of " + city[:-4])
    start = time.time()
    G = nx.random_geometric_graph(len(positions), RADIUS, DIM, pos=positions)
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Graph Load Time:" + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    nx.write_gml(G, "graphs/" + city[:-4]+ "_Normalized.gml")
    #G = nx.read_gml(city[:-4] + ".gml")
    print("#ofNodes: " + str(len(positions)) + ", #ofEdges: " + str(nx.number_of_edges(G)) )
    # #print("#ofNodes: " + str(nx.number_of_nodes(G)) + ", #ofEdges: " + str(nx.number_of_edges(G)) )
    print("Done.")

if __name__ == "__main__":
    main()    




