##  
# File: Infestation.py
# Authors: Dalton Brooks, Daniel Reynoso, John Matta
# Org: Southern Illinois University Edwardsville
# Last Date Edited: Feb 19, 2019 
##

import networkx as nx
#import pydot
import collections
#from networkx.algorithms import community
import random
import operator
import time
import multiprocessing as mp
from ast import literal_eval
import sys
from pathlib import Path
import os.path

probabilities = [10, 12.5, 15, 17.5, 20]    # PROBABILITY - subject to change
removalRate = .01   # PERCENT OF NODE REMOVAL INTERVAL - subject to change
DIM = 2
q = 100
sims = 1000
def main():
    graphFile = sys.argv[1]
    config = Path(graphFile)
    if not config.is_file():
        print("Bad params. exiting.")
        return -1

    mp.set_start_method('spawn')
    processes = []
    totalStart = time.time()
    start = time.time()
    print("Loading graph of " + graphFile[:-4] + "...")
    G = nx.read_gml(graphFile) ## If we have the graph already generated
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Graph Load Time:" + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

    #removal = int(removalRate * nx.number_of_nodes(G))
    Gsize = len(G.node)
    ## calculate betweenness centrality here and use list for all removals instead of recalculating each time.
    # print("Calculating Something for " + city[:-4] + "..." )
    # start = time.time()
    #btw = nx.betweenness_centrality(G) takes too long, trying degree centrality
    # dc = nx.degree_centrality(G)  # going by max degree
    # print("Calculated Degree Centrality.")
    # end = time.time()
    # hours, rem = divmod(end-start, 3600)
    # minutes, seconds = divmod(rem, 60)
    #print("Betweenness Centrality Execution Time:" + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    #dc = sorted(dc.items(), key=operator.itemgetter(1), reverse=True)
    #print(str(dc))
    for p in probabilities:
        removed = [] # removed nodes
        totalInfested = 0
            ## add Degree distribution metric
            # initial simulations
        print("Starting simulations for " + graphFile[:-4] + " with probability: " + str(p))
        filename = "results/" + os.path.basename(graphFile)[:-4] + "_prob"+ str(p) + ".txt"
        process = mp.Process(target=simulate, args = (G, Gsize, p, q, sims, removed, filename))
        processes.append(process)
        process.start()
            # # removal simulations
            # for r in range(5): ### OLD
            #     percentRemoved = (removalRate * (r+1)) * 100
            #     # print(" nodes removed: " + "{:.2f}".format(percentRemoved, 1) + "%")
            #     totalInfested = 0
            #     index = len(removed)
            #     for remove in range(removal): ## remove top percentage of central nodes
            #         # print("removing node - " + str(btw[remove])) printed for testing
            #         removed.append(str(btw[index+remove][0]))
            #         # print(str(btw[index+remove][1]))
            #         # print(G.degree(str(btw[index+remove][0])))
            #         G.remove_node(btw[index+remove][0])
            #     # print("         Total nodes removed: " + str(len(removed)))
            #     # run more sims after removal
            #     print("    Spawning process to simulate after " + str(r+1) + "% removal")
            #     filename = "results/" + city[:-4] + "_SimulatedAvg_prob" + str(p) + "_rem" + "{:.2f}".format(percentRemoved, 1) + ".txt"
            #     process = mp.Process(target=simulate, args=(G, Gsize, p, q, sims, removed, filename,))
            #     processes.append(process)
            #     process.start()
            
    print("Waiting for running processes to complete...") ## runnning all 
    for proc in processes:
        proc.join()

        # RUN SIMS ON LARGEST COMPENENT AS WELL
    print("Running simulations on largest components...")
    largest = max(nx.connected_component_subgraphs(G), key=len)
    largestSize = nx.number_of_nodes(largest)
    print("Size of largest component:" + str(largestSize))
    for p in probabilities:
        print("Starting simulations for largest component of " + graphFile[:-4] + " with probability: " + str(p))
        filename = "results/" + os.path.basename(graphFile)[:-4] + "_prob"+ str(p) + "_largest_componenet.txt"
        process = mp.Process(target=simulate, args = (largest, Gsize, p, q, sims, removed, filename))
        processes.append(process)
        process.start()
                    
    print("Waiting for running processes to complete...") ## runnning all 
    for proc in processes:
        proc.join()
    
    totalEnd = time.time()
    hours, rem = divmod(totalEnd-totalStart, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Total Time for " + graphFile[:-4] + ": " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    f = open("results/" + os.path.basename(graphFile)[:-4] + "_runtime.txt", 'w')
    f.write("Total Time for " + graphFile[:-4] + ": " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    f.close()
    return 0

## this will be used to simulate using child processes instead of sequential processing
def simulate(G, size, p, q, sims, removedNodes, outputFile):
    
    data = [[0 for x in range(sims+1)] for y in range(size+1)]
    start = time.time()
    totalInfested = 0
    for sim in range(sims):
        # if sim%5 == 0:
        #     print("Probability " + str(p) + " is on simulation " + str(sim))
        rand = random.randint(0, size-1) # random node in graph as starting node
        while(str(rand) in removedNodes or str(rand) not in list(G.nodes())): # dont use removed nodes
            rand = random.randint(0, size-1) # random node in graph as starting node    
        initInfested = collections.deque()
        initInfested.append(str(rand))
        infested = SIRsim(G, p, q, initInfested, removedNodes)
        for node in infested:
            data[int(node)][sim] = 1
        totalInfested += (len(infested))
        # print("        simulation #" + str(sim+1) + " - infestation rate:" + str(len(infested)/Gsize) + "%")
    print("Writing sim data to file...")
    f = open(outputFile[:-4] + "_SIMDATA.txt", "w")
    for x in data:
        for y in x:
            f.write(str(y) + ",")
        f.write("\n")
    print("Done writing sim data to file...")
    f.close()
    avgInfested = (totalInfested / (sims * size)) * 100
    # print("        Probability: " + str(p) + " Removed: " + "{:.2f}".format((len(removedNodes)/size)*100, 1) +  "%   Average infestation rate: " + "{:.2f}".format(avgInfested, 1) + "%")
    print("        Probability: " + str(p) + "   Average infestation rate: " + "{:.2f}".format(avgInfested, 1) + "%")

    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("            Time for p=" + str(p) + ": " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    # f = open(outputFile, 'w')
    # # f.write("Probability: " + str(p) + " Removed: " + "{:.2f}".format((len(removedNodes)/size)*100, 1) +  "%   Average infestation rate: " + "{:.2f}".format(avgInfested, 1) + "%\n")
    # f.write("Probability: " + str(p) +"   Average infestation rate: " + "{:.2f}".format(avgInfested, 1) + "%\n")
    # f.write("            Time for p=" + str(p) + ": " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds) + "\n")
    # f.close()
    
    return 0


def SIRsim(G, p, q, initInfested, removed):
    # Graph, probability, q, I a queue of initially infested nodes 
    # and S(v) an array indicator of susceptible nodes
    # in our version, all nodes are susceptible, but we may use this 
    # instead for removed nodes and add a check to ignore nodes
    infested = []
    while(not len(initInfested) == 0):
        node = initInfested.pop()
        if(not int(node) in infested):
            infested.append(int(node))
        for neighbor in nx.neighbors(G,node):
            if((not int(neighbor) in infested) and (not neighbor in removed)):
                rand = random.randint(0,100)
                if(rand <= p):
                    infested.append(int(neighbor))
                    initInfested.append(neighbor)

        rand = random.randint(0,100)
        if(rand >= q):
            initInfested.append(node)

    return infested


if __name__ == '__main__':
    main()