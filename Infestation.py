##  
# File: Infestation.py
# Authors: Dalton Brooks
# Org: Southern Illinois University Edwardsville
# Last Date Edited: April 25, 2019 
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

probabilities = [10, 12.5, 15, 17.5, 20]    # PROBABILITY 
DIM = 2 # dimensions
q = 100 # recovery
sims = 1000 # number of simulations


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

    
    Gsize = len(G.node)
    # initial simulations
    for p in probabilities:
        removed = [] # removed nodes
        totalInfested = 0
        print("Starting simulations for " + graphFile[:-4] + " with probability: " + str(p))
        filename = "results/" + os.path.basename(graphFile)[:-4] + "_prob"+ str(p) + ".txt"
        process = mp.Process(target=simulate, args = (G, Gsize, p, q, sims, removed, filename))
        processes.append(process)
        process.start()
            
    
    print("Waiting for running processes to complete...")
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
        
        rand = random.randint(0, size-1) # random node in graph as starting node
        while(str(rand) in removedNodes or str(rand) not in list(G.nodes())): # dont use removed nodes
            rand = random.randint(0, size-1) # random node in graph as starting node    
        initInfested = collections.deque()
        initInfested.append(str(rand))
        infested = SIRsim(G, p, q, initInfested, removedNodes)
        for node in infested:
            data[int(node)][sim] = 1
        totalInfested += (len(infested))
        
    print("Writing sim data to file...")
    f = open(outputFile[:-4] + "_SIMDATA.txt", "w")
    for x in data:
        for y in x:
            f.write(str(y) + ",")
        f.write("\n")
    print("Done writing sim data to file...")
    f.close()
    avgInfested = (totalInfested / (sims * size)) * 100
    
    print("        Probability: " + str(p) + "   Average infestation rate: " + "{:.2f}".format(avgInfested, 1) + "%")

    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("            Time for p=" + str(p) + ": " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    
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