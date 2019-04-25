
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

def main():
    city = sys.argv[1] ## get city file from cmd
    RADIUS = .001235177866 ## 450 feet in latitude -- ( 1/69 * 1/5280 * 300 )

    print("Normalizing graph of " + city)
    f = open(city, "r")
    G = f.read()
    f.close()
    positions = dict(literal_eval(G))
    print("num nodes:  " + str(len(positions)))
    # init min and max for x and y
    xMin = positions[1][0]
    xMax = positions[0][0]
    yMax = positions[0][1]
    yMin = positions[1][1]
    
    for node in positions:
        if positions[node][0] > xMax:
           xMax = positions[node][0]
        elif positions[node][0] < xMin:
            xMin = positions[node][0]
        if positions[node][1] > yMax: 
            yMax = positions[node][1]
        elif positions[node][1] < yMin: 
            yMin = positions[node][1]
    print("Min X coordinate: " + str(xMin) + "  Max X coordinate: " + str(xMax))
    print("Min Y coordinate: " + str(yMin) + "  Max Y coordinate: " + str(yMax))
    
    ## calculate the diagonal for normalization
    diagonal = math.hypot((xMax - xMin), (yMax - yMin))
    print("Diagonal = " + str(diagonal))
   
    ### Commented code is used to get denormalized positions of RGG
    # f = open("your_output_file",'w')
    ## reversing the normalization
    # G = nx.read_gml("your_normalized_gml")
    # for node in G.nodes():
    #     G.node[node]['pos'][0] = (G.node[node]['pos'][0] * diagonal) + xMin
    #     G.node[node]['pos'][1] = (G.node[node]['pos'][1] * diagonal) + yMin
    #     print(G.node[node]['pos'])
    #     f.write(str(G.node[node]['pos'][0]) + ',' + str(G.node[node]['pos'][1]) + '\n')

    # f.close()


    ## Min Max Normalization
    for node in positions:
        positions[node] = (((positions[node][0] - xMin) / (diagonal)),((positions[node][1] - yMin) / (diagonal)))
    
    ## Normalize Radius!!
    RADIUS = (RADIUS) / (diagonal)
    print("Normalized Radius based on diagonal: " + str(RADIUS))
    
    ## print RADIUS to file
    f = open("graphs/" + city[:-4] + "_radius.txt", 'w')
    f.write(str(RADIUS))
    f.close()


    print("Generating Normalized Graph of " + city[:-4])
    start = time.time()
    # Generate Graph
    G = nx.random_geometric_graph(len(positions), RADIUS, DIM, pos=positions)
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Graph Load Time:" + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    # Write Graph to GML file
    nx.write_gml(G, "graphs/" + city[:-4]+ "_Normalized.gml")
    # print stats
    print("#ofNodes: " + str(len(positions)) + ", #ofEdges: " + str(nx.number_of_edges(G)) )
    print("Done.")

if __name__ == "__main__":
    main()    




