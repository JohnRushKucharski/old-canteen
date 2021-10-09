import sys
sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
from simulation import Simulation

import networkx as nx

G = nx.Graph()

class Node:
    def __init__(self, sim: Simulation):
        self._name = sim.reservoir.name
        self._node = G.add(sim)

print(G)
print(G.nodes)