import networkx as nx
import matplotlib.pyplot as mpp
import pandas as pd
from collections import namedtuple
from graphnodes import GraphNodes

Node = namedtuple("Node","ID STREET1 STREET2")
col_list = ["STREET1", "STREET2"]
df = pd.read_csv('KSI.csv', usecols=col_list)
df = df.drop_duplicates().reset_index(drop=True)

gn = GraphNodes(df)

nodes = gn.allNodes()
labels= gn.getLabels(nodes)


pos = {}

G = nx.Graph()
G.add_nodes_from(nodes)

#move this functionality to graphnodes

for n1 in nodes:
		for n2 in nodes:
				if (n1 != n2) and ((n1.street1 == n2.street2) or(n1.street2 == n2.street1) or (n1.street2 == n2.street2) or(n1.street1 == n2.street1)):
						G.add_edge(n1, n2)

pos=nx.spring_layout(G)
nx.draw_networkx(G, pos=pos, with_labels=False)
nx.draw_networkx_labels(G,pos, labels)

print(G.number_of_nodes())
print(G.number_of_edges())
# print(nodes[53])
# print(nodes[92])
mpp.show()

