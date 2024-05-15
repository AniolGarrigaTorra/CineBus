from typing import TypeAlias, Set, List, Tuple, Dict
import networkx
import json
import requests
from bs4 import BeautifulSoup 
import matplotlib.pyplot as plt
from staticmap import StaticMap, CircleMarker, Line
import random

BusesGraph : TypeAlias = networkx.Graph

def get_buses_graph() -> BusesGraph: 
    """Analitza les dades de l'OpenDataAMB i crea amb networkx un graf on els nodes són parades de bus i les arestes, línies de Bus que les connecten."""
    url = "https://www.ambmobilitat.cat/OpenData/ObtenirDadesAMB.json"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    information = soup.get_text()
    complet_information_buses = json.loads(information)


    buses_graph = BusesGraph()

    information_lines = complet_information_buses['ObtenirDadesAMBResult']['Linies']['Linia']


    for line in information_lines:
        line_name: str = line['Nom']
        
        stations = line['Parades']['Parada']
        previous_station: str = ""
        
        lon_prev, lat_prev = 0.0, 0.0
        
        for station in stations:          
            station_code: str = station['CodAMB']
            station_name: str = station['Nom']
            station_y: float = station['UTM_X']         #Les coordenades estan al revés
            station_x: float = station['UTM_Y']
            station_lines: str = station['Linies']
            municipi: str = station['Municipi']
            

            if municipi == 'Barcelona':
                buses_graph.add_node(station_code, name = station_name, coord = (station_x, station_y), lines = station_lines)
                
                if previous_station != "" and previous_station != station_code: 
                    if buses_graph.has_edge(previous_station, station_code):    
                        buses_graph[previous_station][station_code]['lines'].append(line_name)
                    else:
                        buses_graph.add_edge(previous_station, station_code, lines = [line_name]) #, distance = distance_stations(lon_prev, lat_prev, station_x, station_y)
                
                previous_station = station_code
                lon_prev, lat_prev = station_x, station_y
    
    return buses_graph


def show_buses(g: BusesGraph) -> None: 
    """Mostra de manera interactiva en una altra finestra, el graf de busos"""
    coordenades = networkx.get_node_attributes(g, 'coord')
    networkx.draw(g, pos = coordenades, node_color='lightblue', edge_color='gray', node_size=5)
    plt.show()


def plot_buses(g: BusesGraph, nom_fitxer: str) -> None:
    """Guarda en un fitxer png anomenat com el paràmetre d'entrada un mapa de Barcelona on es mostren les parades i les diferents línies de Bus de la ciutat"""
    barna = StaticMap(3840, 2160, 50, 50)

    for coordinate in networkx.get_node_attributes(g, 'coord').values():        #Crea les parades de bus
        marker = CircleMarker(coordinate, 'red', 3)
        barna.add_marker(marker)
    
    color_lines: Dict[str, str] = dict()           #{(line, color)}
    for u, v, attributes in g.edges(data = True):
        line = attributes['lines'][0]
        if line not in color_lines:
            color_lines[line] = get_random_color([])
        
        color = color_lines[line]

        linia = Line([(g.nodes[u]['coord'][0], g.nodes[u]['coord'][1]),(g.nodes[v]['coord'][0], g.nodes[v]['coord'][1])], color, 1)  # Crea una línia entre els dos nodes
        barna.add_line(linia)

    image = barna.render(zoom = 14)
    image.save(nom_fitxer)


def get_random_color(colors: list[str]) -> str:
    """Donada una llista de colors ja utilitzats, retorna un color random que no sigui en aquesta. Si la llista de colors utilitzats ja és igual a la de colors disponibles retorna un color random."""
    
    colors_disponibles = ["green", "red", "pink", "purple", "orange", "brown", "black", "turquoise"]
    colors_no_utilitzats = [color for color in colors_disponibles if color not in colors]

    if colors_no_utilitzats:
        return random.choice(colors_no_utilitzats)
    else:
        return random.choice(colors_disponibles)

