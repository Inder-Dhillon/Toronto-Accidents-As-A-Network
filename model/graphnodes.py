from node import Node

class GraphNodes:
	def __init__(self, dataframe):
		self.dataframe = dataframe

	def allNodes(self):
		#TODO
		nodes = []
		for i in range (29):
			node = Node(i, self.dataframe["STREET1"][i], self.dataframe["STREET2"][i])
			nodes.append(node)
		return nodes

	def getLabels(self, nodes):
		labels ={}
		for node in nodes:
			labels[node] = node.id
		return labels


	# def nodesByWeather(self, weatherType):
	# 	#TODO

	# def nodesByDay(self, day):
	# 	#TODO

	# def nodesByYear(self, year):
	# 	#TODO

	# def nodesByDistrict(self, district):
	# 	#TODO