import osmnx as ox
import networkx as nx
import geopandas as gpd
from accident import ACCIDENT

def getEdgeWeights(df, G):
  #dictionary of edge tuples to weight
  weights = {}
  sumGraphWeights = 0 #used to get the sum of all injury indexes in the 
  sumGraphNodes = 0
  #loop through each node
  for node in df['G_NODE']:
    #if G.nodes[node]['accident_list'] !=[]:
    totalLen = 0     
    totalWeight = 0    
    sumGraphNodes += 1
    for edge in nx.edges(G, node):
      totalLen += G.get_edge_data(edge[0], edge[1])[0]['length']
    for x in G.nodes[node]['accident_list']:
      totalWeight += x.inj_index
      sumGraphWeights += x.inj_index
    baseWeight = totalWeight/len(G.nodes[node]['accident_list'])
    for edge in nx.edges(G, node):
      weights[(edge[0], edge[1], 0)] = (totalLen/G.get_edge_data(edge[0], edge[1])[0]['length']) * baseWeight
  avgWeight = sumGraphWeights/sumGraphNodes if sumGraphNodes else 0
  for node in G.nodes:
    if G.nodes[node]['accident_list'] == []:
      totalLen = 0
      totalWeight = 0
      for edge in nx.edges(G, node):
        totalLen += G.get_edge_data(edge[0], edge[1])[0]['length']
      for edge in nx.edges(G, node):
        weights[(edge[0], edge[1], 0)] = (totalLen/G.get_edge_data(edge[0], edge[1])[0]['length']) *avgWeight
  return weights

def assign_injury_index(injury:str):
  if injury == "Minimal":
    return 0.4
  elif injury == "Minor":
    return 0.6
  elif injury == "Major":
    return 0.8
  elif injury == "Fatal":
    return 1.0
  else:
    return 0.2

def ksi_data_preprocessing(G, filter_df):
  ksi_df = gpd.read_file("https://opendata.arcgis.com/datasets/cc17cc27ee5a4989b78d9a3810c6c007_0.geojson")
  ksi_df["INJ_INDEX"] = ksi_df["INJURY"].apply(lambda x: assign_injury_index(x))
  index_df = ksi_df[["ACCNUM", "INJ_INDEX"]].groupby(by="ACCNUM").sum()
  cols_to_keep = ["LATITUDE", "LONGITUDE", "ACCNUM", "YEAR", "TIME", "VISIBILITY", "LIGHT",	"RDSFCOND"]
  ksi_df = ksi_df[cols_to_keep]
  fatalities = ksi_df["ACCNUM"].value_counts()
  ksi_df["FATALITIES"] = ksi_df["ACCNUM"].apply(lambda x : fatalities[x])
  ksi_df = ksi_df.drop_duplicates()
  ksi_df.reset_index(drop=True, inplace=True)
  ksi_df["G_NODE"]= ox.get_nearest_nodes(G, ksi_df["LONGITUDE"], ksi_df["LATITUDE"], method="balltree")
  ksi_df.drop(["LATITUDE", "LONGITUDE"], axis=1, inplace=True)
  ksi_df = ksi_df.merge(index_df, on="ACCNUM")
  ksi_df = ksi_df.infer_objects()
  ksi_df["ACCIDENT"] = ksi_df.apply(lambda x: ACCIDENT(x["ACCNUM"], x["YEAR"], x["TIME"], x["VISIBILITY"], x["LIGHT"], x["RDSFCOND"], x["FATALITIES"], x["INJ_INDEX"]), axis=1)
  if filter_df == "VIS-CLEAR":
    return ksi_df.loc[ksi_df.VISIBILITY.isin(["Clear"])]
  elif filter_df == "VIS-NCLEAR":
    return ksi_df.loc[~ksi_df.VISIBILITY.isin(["Clear"])]
  elif filter_df == "RD-DRY":
    return ksi_df.loc[ksi_df.RDSFCOND.isin(["Dry"])]
  elif filter_df == "RD-WET":
    return ksi_df.loc[ksi_df.RDSFCOND.isin(["Wet"])]
  elif filter_df == "RD-OTHER":
    return ksi_df.loc[~ksi_df.RDSFCOND.isin(["Dry", "Wet"])]
  elif filter_df == "TIME-RUSH":
    ksi_df['TIME'] = ksi_df['TIME'].astype('int')
    return ksi_df.loc[(ksi_df.TIME.between(630,930, inclusive=True)) | (ksi_df.TIME.between(1500,1900, inclusive=True))]
  elif filter_df == "TIME-NRUSH":
    ksi_df['TIME'] = ksi_df['TIME'].astype('int')
    return ksi_df.loc[(ksi_df.TIME.between(0,629, inclusive=True)) | (ksi_df.TIME.between(1901,2400, inclusive=True)) | (ksi_df.TIME.between(931,1499, inclusive=True))]
  elif filter_df == "TIME-DAY":
    ksi_df['TIME'] = ksi_df['TIME'].astype('int')
    return ksi_df.loc[ksi_df.TIME.between(701,1900, inclusive=True)]
  elif filter_df == "TIME-NIGHT":
    ksi_df['TIME'] = ksi_df['TIME'].astype('int')
    return ksi_df.loc[(ksi_df.TIME.between(1901,2400, inclusive=True)) | (ksi_df.TIME.between(0,700, inclusive=True))]
  else:
    return ksi_df

def create_tor_graph(filter_df = "None", weighted=True):
  G = ox.graph_from_place('Toronto, Ontario, Canada', network_type='drive')
  ksi_df = ksi_data_preprocessing(G, filter_df)
  given_df = ksi_df.groupby('G_NODE')['ACCIDENT'].apply(list).reset_index(name='ACCIDENTS')
  attr = given_df.set_index('G_NODE')['ACCIDENTS'].to_dict()
  nx.set_node_attributes(G, [], "accident_list")
  nx.set_node_attributes(G, attr, "accident_list")
  if weighted:
    weights = getEdgeWeights(given_df, G)
    nx.set_edge_attributes(G, 0, 'w')
    nx.set_edge_attributes(G, weights, 'w')
  G = ox.add_edge_speeds(G)
  G = ox.add_edge_travel_times(G)
  return G
