import numpy as np
from igraph import *
import pdb

def expansion(g, memberships):
    n = len(memberships)
    groups = len(np.unique(memberships))
    fc = np.zeros(groups)
    
    for e in EdgeSeq(g):
        v1, v2 = e.tuple
        different_group = memberships[v1] != memberships[v2]
        fc[memberships[v1]] += int(different_group)
        fc[memberships[v2]] += int(different_group)
    
    return sum(fc)/n
    
def conductance(g, memberships):
    n = len(memberships)
    groups = len(np.unique(memberships))
    nc = [memberships.count(x) for x in np.unique(memberships)]
    
    fc = np.zeros(groups)
    mc = np.zeros(groups)
    
    for e in EdgeSeq(g):
        v1, v2 = e.tuple
        if memberships[v1] == memberships[v2]:
            mc += 1
        else:
            fc += 1
    
    return sum(nc*fc/(n*(2*mc+fc)))
      
def tp_ratio(g, memberships):
    n = len(memberships)
    groups = len(np.unique(memberships))
    nt = np.zeros(groups)    
    
    for i in range(0,groups):
        subgraph_indices = [j for j, x in enumerate(memberships) if x == i]
        subgraph = g.subgraph(subgraph_indices)
        triangles = subgraph.cliques(min=3,max=3)
        triangle_vertices = []
        for triangle in triangles:
            triangle_list = list(triangle)
            triangle_vertices.extend(triangle_list)
        
        triangle_vertices = set(triangle_vertices)
        nt[i] = len(triangle_vertices)
        
    return sum(nt)/n