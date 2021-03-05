# Graph Coloring algorithms
import networkx as nx
from typing import Dict, FrozenSet, Set


def coloring(vertices, edges):
	"""
	This is the handler for choosing coloring algorithm

	Inputs:
		vertices: all nodes in the graph
			:type vertices: Set[str]

		edges:	all edges in the graph
			:type edges: Set[FrozenSet[str, str]]

	Returns:
		Color Assignment in form of Dictionary, node as key and color as val.
			:type :return: Dict[str: int]
	"""
	# Call method to create a graph
	G = create_graph(vertices, edges)

	# Perform Graph Coloring by applying welsh powell algorithm
	result = welsh_powell(G)		# type: Dict[str: int]

	return result


def create_graph(vertices, edges):
	"""
	Method to create graph from given vertices and edges

	Inputs:
		vertices: all nodes in the graph
			:type vertices: Set[str]

		edges:	all edges in the graph
			:type edges: Set[FrozenSet[str, str]]

	Returns:
		Graph created from given vertices and edges
			:type :return: nx.Graph
	"""
	# Create a graph object
	G = nx.Graph()

	# Add all edges
	for e in edges:
		e2l = list(e)
		G.add_edge(e2l[0], e2l[1])

	# Add all vertices
	for v in vertices:
		G.add_node(v)

	return G


# implementation of welsh_powell algorithm
def welsh_powell(G):
	"""
	This is the implementation of welsh-powell algorithm

	Input:
		G: The graph to be colored
			:type G:	nx.Graph[str]

	Returns:
		Color Assignment in form of Dictionary, node as key and color as val.
			:type :return: Dict[str: int]
	"""

	# Sort nodes based on number of neighbors
	node_list = sorted(G.nodes(), key=lambda x: G.neighbors(x))

	# Assign first node to first color (0)
	col_val = {node_list[0]: 0}  # dictionary to store the color assignment

	# Assign colors to remaining nodes
	for node in node_list[1:]:
		# Initialize available colors list
		available = [True] * len(G.nodes())

		# Colors are not available if used by adjacent nodes
		for adj_node in G.neighbors(node):
			if adj_node in col_val.keys():
				col = col_val[adj_node]
				available[col] = False

		# Find smallest available color to assign to the current node
		for clr in range(len(available)):
			if available[clr]:		# True
				col_val[node] = clr
				break

	return col_val
