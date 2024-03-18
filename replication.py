import numpy as np
from numpy.polynomial.polynomial import polyfit
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

## Loop through years
graph_a = pd.DataFrame(columns=['year', 'num_authors', 'num_links'])
graph_b = pd.DataFrame(columns=['year', 'p', 's'])
for year in ['2019', '2020', '2021', '2022', '2023']:

    ## Read in data
    nodes = pd.read_csv('data/nodes_' + year + '.csv')
    edges = pd.read_csv('data/edges_' + year + '.csv')

    ## Number of authors
    N = nodes.shape[0]

    ## Create graph
    G = nx.Graph()
    G.add_nodes_from(nodes['n'])
    G.add_edges_from(list(zip(edges.v, edges.w)))

    ## Get connected components
    cc = nx.connected_components(G)

    ## Convert to DF
    ccs = pd.DataFrame({'cc_size' : [len(c) for c in cc]})

    max_component = max(ccs.cc_size)

    P = max_component / N
    S = (sum((ccs.cc_size ** 2)) - (max_component ** 2)) / (N ** 2)

    a_temp = pd.DataFrame({'year' : [year], 'num_authors' : [N], 'num_links' : [sum(edges.weight)]})
    graph_a = pd.concat([graph_a, a_temp], ignore_index=True)

    b_temp = pd.DataFrame({'year' : [year], 'p' : [P], 's' : [S]})
    graph_b = pd.concat([graph_b, b_temp], ignore_index=True)

b1, m1 = polyfit(graph_a.iloc[0:3, 1].to_list(), graph_a.iloc[0:3, 2].to_list(), 1)
b2, m2 = polyfit(graph_a.iloc[3:, 1].to_list(), graph_a.iloc[3:, 2].to_list(), 1)
b3, m3 = polyfit(graph_a.iloc[:, 1].to_list(), graph_a.iloc[:, 2].to_list(), 1)

plt.plot(graph_a.iloc[0:3, 1], graph_a.iloc[0:3, 1] * m1 + b1, '-', color='gray', 
         label=f'y = {round(m1, 2)} * x + {round(b1, 0)}')
plt.plot(graph_a.iloc[3:, 1], graph_a.iloc[3:, 1] * m2 + b2, '-', color='red', 
         label=f'y = {round(m2, 2)} * x + {round(b2, 0)}')
plt.plot(graph_a['num_authors'], graph_a['num_links'], '.', color='blue')
plt.xlabel('number of authors')
plt.ylabel('number of connections')
plt.title('Figure A')
plt.legend(loc='best')
plt.savefig('figs/fig_a.png')
plt.clf()

plt.plot(graph_b['year'], graph_b['p'], color='blue', label='relative size of largest cluster (P)')
plt.plot(graph_b['year'], graph_b['s'], color='red',label='cluster size susceptibility (S)')
plt.xlabel('year')
plt.ylabel('P, S')
plt.title('Figure B')
plt.legend(loc='best')
plt.savefig('figs/fig_b.png')
