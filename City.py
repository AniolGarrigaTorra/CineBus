from typing import TypeAlias, List, Tuple, Dict
import networkx as nx
import Buses
import osmnx as ox
import pickle
import os
import matplotlib.pyplot as plt
from staticmap import CircleMarker, Line, StaticMap
import random

CityGraph : TypeAlias = nx.Graph
OsmnxGraph : TypeAlias = nx.MultiDiGraph
Coord : TypeAlias = Tuple[float, float]   # (latitude, longitude)
Path: TypeAlias =  List[str] 

def get_osmnx_graph() -> OsmnxGraph:
    """Retorna el graf de carrers de Barcelona tot utilitzant dades d'Open Street Map"""
    place_name = "Barcelona, Spain"
    street_graph = ox.graph_from_place(place_name, "walk", True)

    for id_cruilla in street_graph.nodes():
        cruilla_coord: Coord = (street_graph.nodes[id_cruilla]['x'], street_graph.nodes[id_cruilla]['y'])
        street_graph.nodes[id_cruilla]['coord'] = cruilla_coord

    for u, v, k, data in street_graph.edges(keys=True, data=True):
        distance = data['length']
        
        time = distance / (1000 * 4)    #4 és una constant que simbolitza la velocitat mitja en km/h d'un peató. El 1000 és per passar de metres a quilòmetres.
        
        # Agreguem el temps que l'usuari tardaroa en realitzar aquesta aresta
        street_graph.edges[u, v, k]['time'] = time
        
        if 'geometry' in data:
            del street_graph.edges[u, v, k]['geometry']
    
    return street_graph


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    """guarda el graf g al fitxer filename"""
    file = open(filename, 'wb')
    pickle.dump(g, file)
    file.close()


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    """retorna el graf guardat al fitxer filename"""
    assert os.path.exists(filename)
    file = open(filename, 'rb')
    g = pickle.load(file)
    file.close()

    return g


def get_stations_distance(bg: Buses.BusesGraph, sg: OsmnxGraph) -> None:
    """Calcula utilitzant el graf de carrers, la distància i temps que necessitaria un bus per anar d'una parada a una altra, per cada un dels nodes del graf"""
    u: str
    v: str
    
    lon_stations: List[float] = [attribute['coord'][0] for node, attribute in bg.nodes(data = True)]
    lat_stations: List[float] = [attribute['coord'][1] for node, attribute in bg.nodes(data = True)]
    nearest_cruilles: List[str] = ox.distance.nearest_nodes(sg, lon_stations, lat_stations, return_dist =  False)
    
    dict_nearest_cruilles: Dict[str, str] = dict(zip(bg.nodes(), nearest_cruilles))
    
    for u, v in bg.edges():
        distance: float = nx.shortest_path_length(sg, dict_nearest_cruilles[u], dict_nearest_cruilles[v], weight= 'length')
        bg.edges[u, v]['length'] = distance
        bg.edges[u, v]['time'] = distance /(1000 * 15)      #15 és una 'cnt' que simbolitza la velocitat mitja d'un Bus per Barcelona en km/h. El 1000 és perque la distància és donada en metres


def build_city_graph(g1: OsmnxGraph, g2: Buses.BusesGraph) -> CityGraph:
    """retorna un graf fusió de g1 i g2"""
    city_graph = CityGraph()
    get_stations_distance(g2, g1)

    #Per passar de multigraf a graf
    city_graph.add_nodes_from(g1.nodes(data = True), type = 'cruilla')
    
    afegits = set()  # Conjunt per controlar les connexions ja afegides
    for node1, node2, data in g1.edges(data=True):
        connexio = (node1, node2)
        if connexio not in afegits and node1 != node2:
            # Afegeix l'aresta al nou graf
            city_graph.add_edge(node1, node2, **data, type = 'carrer')
            afegits.add(connexio)
    

    city_graph.add_nodes_from(g2.nodes(data = True), type = 'parada')
    city_graph.add_edges_from(g2.edges(data = True), type = 'linia')

    
    lon_stations: List[float] = [attributes['coord'][0] for id, attributes in g2.nodes(data = True)]
    lat_stations: List[float] = [attributes['coord'][1] for id, attributes in g2.nodes(data = True)]

    nearest_cruilla, distances = ox.distance.nearest_nodes(g1, lon_stations, lat_stations, return_dist =  True)
    
    llista_temps = [{'time': d / (1000 * 4)} for d in distances]   
    
    station_cruilla_connexions: list[tuple[int, int, List[Dict[str, float]]]] = list(zip(nearest_cruilla, g2.nodes(), llista_temps))
    city_graph.add_edges_from(station_cruilla_connexions, type = 'carrer')

    return city_graph


def show(cg: CityGraph) -> None:
    """mostra cg de forma interactiva en una finestra"""
    colors_nodes = {'cruilla': 'blue', 'parada': 'red'}
    colors_edges = {'carrer': 'gray', 'linia': 'orange'}

    node_colors = [colors_nodes[cg.nodes[node]['type']] for node in cg.nodes()]
    edge_colors = [colors_edges[cg.edges[edge]['type']] for edge in cg.edges()]

    coordenades = nx.get_node_attributes(cg, 'coord')

    nx.draw(cg, pos = coordenades, node_color = node_colors, edge_color = edge_colors, node_size = 3)
    plt.axis('off')
    plt.show()


def plot(cg: CityGraph, filename: str) -> None:
    """desa cg com una imatge amb el mapa de la cuitat de fons en l'arxiu filename"""
    map = StaticMap(3840, 2160, 0, 0)

    for node in cg.nodes():
        lon, lat = cg.nodes[node]['coord']
        tipus = cg.nodes[node]['type']
        if tipus == 'parada':
            color = 'red'  # Nodes de tipus 'parada' en vermell
        else:
            color = 'blue'  # Nodes de tipus 'cruilla' en blau

        marcador = CircleMarker((lon, lat), color, 2)
        map.add_marker(marcador)

    # Afegir línies per a les arestes del graf
    for u, v in cg.edges():
        tipus = cg[u][v]['type']

        if tipus == 'carrer':
            color = 'gray'  # Arestes de tipus 'carrer' en color gris
        else:
            color = 'orange'  # Arestes de tipus 'linia' en color taronja

        linia = Line([(cg.nodes[u]['coord'][0], cg.nodes[u]['coord'][1]),(cg.nodes[v]['coord'][0], cg.nodes[v]['coord'][1])], color, 1)
        map.add_line(linia)  # Afegeix la línia al mapa estàtic

    image = map.render(zoom = 14)
    image.save(filename)
 

def find_path(sg: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> Path:
    """Cerca el camí més curt entre dos punts src, dst utilitzant l'algoritme de dijkstra en el graf ciutat."""
    lon_stations: List[float] = [src[1], dst[1]]
    lat_stations: List[float] = [src[0], dst[0]]

    nearest_cruilla, distance = ox.distance.nearest_nodes(sg, lon_stations, lat_stations, return_dist =  True)  #Busquem els Nodes cruïlla més propers a les coordenades d'inici i fi.
    shortest_path: list[str] = nx.dijkstra_path(g, nearest_cruilla[0], nearest_cruilla[1], weight = 'time')

    return shortest_path


def plot_path(g: CityGraph, p: Path, filename: str) -> None:
    """mostra el camí p en l'arxiu filename"""
    map = StaticMap(3840, 2160, 50, 50)

    prev_node: str = ''
    used_colors: List[str] = list()
    color: str = 'blue'
    prev_line: str = ''
    lon_prev, lat_prev = 0.0, 0.0
    
    #Tots aquests if serveixen per printejar de blau els trossos a peu, i d'altres colors les diferents línies de Bus que agafem
    for node in p:
        lon, lat = g.nodes[node]['coord']
        tipus = g.nodes[node]['type']

        if prev_node == '':
            marcador = CircleMarker((lon, lat), 'blue', 10)
            map.add_marker(marcador) 
        
        elif g.nodes[prev_node]['type'] != tipus:
            linia = Line([(lon_prev, lat_prev),(lon, lat)], 'blue', 5)
            map.add_line(linia) 

            if tipus == 'cruilla':
                marcador = CircleMarker((lon_prev, lat_prev), color, 10)
                map.add_marker(marcador)

        elif tipus == 'cruilla':
            linia = Line([(lon_prev, lat_prev),(lon, lat)], 'blue', 5)
            map.add_line(linia)

        else:
            if prev_line in g.edges[prev_node, node]['lines']:
                linia = Line([(lon_prev, lat_prev),(lon, lat)], color, 5)
                map.add_line(linia)
            
            else:
                prev_line = g.edges[prev_node, node]['lines'][0]
                color = get_random_color(used_colors)
                used_colors.append(color)
                marcador = CircleMarker((lon_prev, lat_prev), color, 10)
                map.add_marker(marcador)
                

                linia = Line([(lon_prev, lat_prev),(lon, lat)], color, 5)
                map.add_line(linia)
        
        prev_node = node
        lon_prev, lat_prev = lon, lat
    
    image = map.render()

    image.save(filename)


def get_random_color(colors: list[str]) -> str:
    """Donat una llista de colors usats, en retorna un color aleatori."""
    colors_disponibles = ["green", "red", "pink", "purple", "orange", "brown", "black", "turquoise"]
    colors_no_utilitzats = [color for color in colors_disponibles if color not in colors]

    if colors_no_utilitzats:
        return random.choice(colors_no_utilitzats)
    else:
        return random.choice(colors_disponibles)



