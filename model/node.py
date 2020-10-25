class Node:
	def __init__(self, id, street1, street2): #, coordinates, accident):
		self.id = id
		self.street1 = street1
		self.street2 = street2
		# self.coordinates = coordinates
		# self.accident = accident

class Accident:
	def __init__(self, day, time, weather):
		self.day = day
		self.time = time
		self.weather = weather