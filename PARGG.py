##  
# File: PARGG.py
# Authors: Dalton Brooks
# Org: Southern Illinois University Edwardsville
# Last Date Edited: April 25, 2019 
##


import sys
import networkx as nx

import collections

import random
import operator
import time
import math

def main():
    ## get graph requirements (size, radius, output)
    size = 0
    radius = 0
    size = int(sys.argv[1])
    radius = float(sys.argv[2])
    output = sys.argv[3]
    if size <= 0 or radius <= 0 or sys.argv[3] == "":
        print("bad input")
        return -1

    ## preferentialRGG.py size radius outputfile       ## how to run

    ## Build graph using Preferential Attachment

    starting = 100 # start with 100~ groups?
    
    ## generate a starting graph
    G = nx.random_geometric_graph(starting, radius, 2)
    
    start = time.time() ## track time
    s = starting
    ## O(size - starting)
    i = 0
    ## GET GROUPS
    probabilities = [] ## holds probabilities of being positioned in each group
    components = sorted(nx.connected_component_subgraphs(G), key=len, reverse = True)
    for component in range(len(components)):
        #print( str( nx.number_of_nodes(components[component]) )  + " in component " + str(component + 1))
        probabilities.append( len(components[component].node) )
    for n in range(size - starting):
        # print progress
        printProgressBar(n + 1, size-starting, prefix = 'Progress:', suffix = 'Complete', length = 50)
        
        s += 1 ## this is used to track the new nodes index
        ## GET RANDOM NUMBER -- probability
        rand = random.random()
        
        p = 0 ## this tracks the probability for each component,
              ## add the probability to p, check if less than p, if not, continue
        for probability in range( len( probabilities ) ):
            p += (probabilities[probability] / s)
            if rand <= p:
                ## update probabilities list
                probabilities[probability] += 1
                ## IN THE COMPONENT/GROUP
                ## Get a random node in the compenent to be the new node's neighbor.
                neighbor = random.randint(0,len(components[probability].node)-1)
                neighbor = list(components[probability])[neighbor]
                
                #generate points within radius of new neighbor
                x = random.uniform(-radius, radius) #+ G.node[neighbor]['pos'][0]
                ## we can generate a random value between -r and r for x
                ## but the y value must be dependent on x, as the point (r,r) would be out of the radius
                ## so y would have to be (-sqrt(radius**2 - x**2),sqrt(radius**2 - x**2))  ie Path. Theorm
                yRange = math.sqrt( (radius**2) - (x**2) )
                y = random.uniform(-yRange, yRange)
                ## add node
                G.add_node(s, pos=(x + G.node[neighbor]['pos'][0], y + G.node[neighbor]['pos'][1]))
                for node in G.nodes():
                    ## if within distance of r, add edge
                    if math.sqrt( (G.node[node]['pos'][0] - G.node[s]['pos'][0])**2 + (G.node[node]['pos'][1] - G.node[s]['pos'][1])**2 ) <= radius:
                        G.add_edge(node, s)

                break
        ## case of adding to no group, handle by random points
        if rand > p: ## p is not in the components
            ## we don't want edges from this node, lets check
            edges = 1
            while edges > 0: ## new node must have no neighbors
                x = random.random() # get random points
                y = random.random() 
                edges = 0
                for node in G.nodes():
                ## if within distance of r, add edge
                    if math.sqrt( (G.node[node]['pos'][0] - x)**2 + (G.node[node]['pos'][1] - y)**2 ) <= radius:
                        edges += 1
                        break
            
            ## add node with no neighbors
            G.add_node(s, pos=(x,y))
            
            ## recalculate components when new node is added randomly
            probabilities = [] ## holds probabilities of being positioned in each group
            components = sorted(nx.connected_component_subgraphs(G), key=len, reverse = True)
            for component in range(len(components)):
                probabilities.append( len(components[component].node) )


    ## Uncomment to print statistics
    # largest = sorted(nx.connected_component_subgraphs(G), key=len, reverse=True)
    # print("Number of Components: " + str(len(largest)))
    # print("Largest Component: " + str(nx.number_of_nodes(largest[0])))
    # print("Second Largest Component: " + str(nx.number_of_nodes(largest[1])))
    
    # print("Smallest Component: " + str(nx.number_of_nodes(largest[len(largest)-1])))
    # print("Number of Nodes: " + str(nx.number_of_nodes(G)))
    # print("Number of edges: " + str(nx.number_of_edges(G)))

    nx.write_gml(G, output)
    



## Pulled this from StackOverflow to show progress on long running generations
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


if __name__ == '__main__':
    main()