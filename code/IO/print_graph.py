import matplotlib.pyplot as plt
import networkx as nx
G = nx.Graph()
G.add_nodes_from([2,3])
G.add_edge(2,3)
G.number_of_nodes()

""" MORE INFO
https://plot.ly/python/network-graphs/
https://networkx.github.io/documentation/stable/index.html

"""

G[3][2]['weight'] = 4.6

G.add_nodes_from([4,5])
G.add_edge(4,5)
G[4][5]['weight'] = 0.3

edge_color = [e[2]['weight'] for e in G.edges(data=True)]

nx.draw(G,with_labels=True,width=10.0,edge_cmap=plt.cm.coolwarm,edge_vmin=0,edge_vmax=5,edge_color=edge_color)

sm = plt.cm.ScalarMappable(cmap=plt.cm.coolwarm,norm=plt.Normalize(vmin=0,vmax=5))
sm.set_array([])
cbar = plt.colorbar(sm, shrink=0.5)

plt.show()
