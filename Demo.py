import City 
import Billboard
import Buses
from typing import List, Tuple, Dict, Set
import pickle
import os
from datetime import datetime, timedelta
import osmnx as ox



def print_negreta(text: str) -> None:
    """Printeja el text donat en negreta"""
    print('\033[1m' + text + '\033[0m', end = "")


def authors() -> None:
    """Printeja els autors del treball"""
    print_negreta("Aniol Garriga Torra ")
    print("- Estudiant de primer del Grau en Ciència i Enginyeria de Dades de la UPC")


def make_billboard() -> Billboard.Billboard:
    """Crea la cartellera"""
    return Billboard.read()


def save_billboard() -> None:
    """Guarda la cartellera"""
    bb: Billboard.Billboard = make_billboard()
    filename = 'BillBoard'
    file = open(filename, 'wb')
    pickle.dump(bb, file)
    file.close()


def load_billboard() -> Billboard.Billboard:
    """Carrega la cartellera"""
    assert os.path.exists('BillBoard')
    file = open('BillBoard', 'rb')
    g = pickle.load(file)
    file.close()

    return g


def show_billboard() -> None:
    """Funció que mostra de manera interactiva les cartelleres dels diferents cinemes de Barcelona"""
    billboard: Billboard.Billboard = load_billboard()
    show: bool = True
    while show: 
        print('')
        for i in range(len(billboard.cinemas)):
            print(billboard.cinemas[i].name)
            
        cinema = input('\033[1m' + '\nTria un cinema: ' + '\033[0m')
        
        prev_film: str = ""
        for projection in billboard.projections:
            if projection.cinema.name == cinema:
                if prev_film != projection.film.title:
                    print("\n\n")
                    print_negreta(projection.film.title)
                    print("")
                    print(*projection.film.directors, sep = ", ")
                    print_negreta('Times: ')
                    print("{:02d}".format(projection.time[0]), "{:02d}".format(projection.time[1]), sep=":", end = " ")
                    prev_film = projection.film.title

                else:
                    print("{:02d}".format(projection.time[0]), "{:02d}".format(projection.time[1]), sep=":", end = " ")
    
        if input('\033[1m' + "\n\nVols cercar un altre cinema? (y/n): " + '\033[0m') == 'n': 
            show = False
    

def search_billboard() -> None:
    """Funció que serveix per crear l'interfície del buscador de la cartellera"""
    billboard: Billboard.Billboard = load_billboard()
    show: bool = True
    while show:
        ip = input('\033[1m' + 'Benvingut al cercador de la cartellera de tot Barcelona, siusplau, indiqui que està cercant:\n     1 - Buscar cinemes\n     2 - Buscar pel·lícules\n     EXIT - Tornar enrere\n' + '\033[0m')
    
        if ip == '1':
            search_cinema(billboard)
        
        elif ip == '2':
            search_film(billboard)
        
        elif ip != 'EXIT':
            print("Perdoni, els únics paràmetres d'entrada vàlids són: 1, 2, EXIT.\n")
        
        else:
            show = False

        
def search_cinema(billboard: Billboard.Billboard) -> None:
    """Dins del buscador de la cartellera, aquesta funció s'encarrega de buscar per cinemes"""
    print('')
    for i in range(len(billboard.cinemas)):
        print(billboard.cinemas[i].name)
        
    cinema = input('\033[1m' + '\nTria un cinema (per tornar enrere escriviu EXIT): ' + '\033[0m')
    cinema_address:str = ''

    searched: bool = False
    for cine in billboard.cinemas:
        if cine.name == cinema:
            cinema_address = cine.address
            searched = True

    if not searched and cinema != 'EXIT':    
        print("Aquest cinema no està a la llista de cinemes de Barcelona, per favor triïn un de la llista:")
        search_cinema(billboard)
    
    elif searched:
        show_1: bool = True
        while show_1:
            input_1 = input('\033[1m' + '\nBona tria, indiqui que voldria saber de ' + cinema + ':\n     1 - Adreça del lloc\n     2 - Cartellera\n     EXIT - Per tornar enrere' + '\033[0m')

            if input_1 == '1':
                print(cinema_address)


            elif input_1 == '2':
                films: Dict[str,Tuple[Billboard.Film, List[Tuple[int, int]], str]] = dict()          #Diccionari de nom pellicula: (pellicula, llistat horaris de la pellicula, idioma) de totes les projeccions del cinema
                prev_film: str = ''
                
                for projection in billboard.projections:
                    if projection.cinema.name == cinema:
                        if projection.film.title != prev_film:
                            films[projection.film.title] = (projection.film, [projection.time], projection.language)
                            prev_film = projection.film.title
                        else:
                            films[projection.film.title][1].append(projection.time)
                
                show_2: bool = True
                while show_2:
                    for film in films:
                        print(film)
                    
                    input_2 = input('\033[1m' + '\nSi voleu més informació sobre una pel·lícula, introduïu el seu nom, sinó, escriviu EXIT: ' + '\033[0m')

                    if input_2 in films:
                        print_negreta('\n' + input_2 + '\n')
                        
                        print_negreta('Directors: ')
                        print(*films[input_2][0].directors, sep = ", ")

                        print_negreta('Actors: ')
                        print(*films[input_2][0].actors, sep = ", ")

                        print_negreta('Gèneres: ')
                        print(*films[input_2][0].genre, sep = ", ")

                        print_negreta('Idioma: ')
                        print(films[input_2][2])

                        print_negreta('Horaris: ')
                        for horari in films[input_2][1]:
                            print("{:02d}".format(horari[0]), "{:02d}".format(horari[1]), sep=":", end = " ")
                        print("")

                        if input('\033[1m' + "\n\nVols anar-la a veure? (y/n): " + '\033[0m') == 'y':
                            input("Se't redirigirà al cercador de rutes de pel·lícules, siusplau recordi el nom de la seva pel·lícula. Premi ENTER per continuar...")
                            go_to_film()
                            show_2 = False
                            show_1 = False

                        if input('\033[1m' + "\n\nVols cercar una altra pel·lícula? (y/n): " + '\033[0m') == 'n': 
                            show_2 = False

        
                    elif input_2 != 'EXIT':
                        print('Aquesta pel·lícula no és a la llista, siusplau triïn una que hi sigui:\n')
                    
                    else:
                        show_2 = False
        
            elif input_1 != 'EXIT':
                print("Perdoni, els únics paràmetres d'entrada vàlids són: 1, 2, EXIT.\n")
                
            else:
                show_1 = False


def search_film(billboard: Billboard.Billboard) -> None:
    """Dins el buscador de cartellera de Barcelona, s'encarrega de buscar per pel·lícules"""
    input_1 = input('\033[1m' + 'Indiqui la forma la qual vol buscar la pel·lícula:\n     1 - Per títol\n     2 - Per gènere\n     3 - Per Horaris\n     EXIT - Tornar enrere\n' + '\033[0m')

    if input_1 == '1':
        show: bool = True
        while show:
            print_negreta("Aquestes són totes les pel·lícules que s'emeten a Barcelona el dia d'avui:\n")
            films: List[str] = list()
            for film in billboard.films:
                print(film.title)
                films.append(film.title)
            
            show = films_information(films, billboard)
            
    
    elif input_1 == '2':
        set_genres: Set[str] = get_set_genres(billboard)
        show = True
        while show:
            print_negreta('Aquests són tots els genères de pel·lícules disponibles:\n')
            print(*set_genres, sep="\n")
            input_2 = input('\033[1m' + "\n\nSi vol veure les pel·lícules d'un gènere en concret, siusplau indiqui el nom del gènere, sinó, escriviu EXIT: " + '\033[0m')
            
            if input_2 in set_genres:
                genre_films: Set[str] = get_genre_films(billboard, input_2)
                print('')
                print(*genre_films, sep = '\n')
                show = films_information(list(genre_films), billboard)

            elif input_2 != 'EXIT':
                print('Aquest gènere no és a la llista, siusplau triïn un que hi sigui:\n')

            else:
                show = False


    
    elif input_1 == '3':
        dict_films: Dict[str, Dict[str, List[Tuple[str, Tuple[int, int]]]]] = get_time_films(billboard)     #{hh: {cinema: [(pellicula, (hh:mm))]}}
        show = True
        while show:
            input_2 = input('\033[1m' + "\n\nIndiqui la hora la qual vol veure les projeccions de la forma: hh (p.ex. 16, 19, 23, 07, 09...), si voleu tornar enrere escriviu EXIT: " + '\033[0m')
            
            if input_2 in dict_films:
                show_2: bool = True
                while(show_2):
                    print('\n')
                    print(*dict_films[input_2], sep="\n")
                    input_3 = input('\033[1m' + "\n\nSiusplau indiqui a quin cinema vol cercar les projeccions:" + '\033[0m')
                    if input_3 in dict_films[input_2]:
                        print_negreta('\n\nLes pel·lícules que es projecten de les ' + input_2 + ':00 a les ' + input_2 + ':59 a ' + input_3 + ' són:\n')
                        films: list[str] = list()
                        for film_name, time in dict_films[input_2][input_3]:
                            films.append(film_name)
                            print(film_name + ' - ' + str(time[0]) + ':' + str(time[1]), sep = '')
                        print('')
                        show_2 = films_information(films, billboard)
                    
                    else:
                        print('\nAquest cinema no és a la llista, siusplau triïn un que hi sigui:\n')

            elif input_2 != 'EXIT':
                print("\nNo hi ha cap projecció a l'hora indicada, siusplau triï una altra hora:\n")

            else:
                show = False

    
    elif input_1 != 'EXIT':
        print("Perdoni, els únics paràmetres d'entrada vàlids són: 1, 2, 3, EXIT.\n")
        search_film(billboard)
    

def get_time_films(bb: Billboard.Billboard) -> Dict[str, Dict[str, List[Tuple[str, Tuple[int, int]]]]]:
    """Donada la cartellera retorna un diccionari amb els horaris de le pel·lícules"""
    time_films: Dict[str, Dict[str, List[Tuple[str, Tuple[int, int]]]]] = dict()    #{}
    
    for projection in bb.projections:
        if str(projection.time[0]) in time_films:
            if projection.cinema.name not in time_films[str(projection.time[0])]:
                time_films[str(projection.time[0])][projection.cinema.name] = [(projection.film.title, projection.time)]
            else:
                time_films[str(projection.time[0])][projection.cinema.name].append((projection.film.title, projection.time))
        else:
            time_films[str(projection.time[0])] = {projection.cinema.name: [(projection.film.title, projection.time)]}
    
    return time_films


def get_film_cinemas(bb: Billboard.Billboard, idx: int) -> Set[str]:
    """Donada la cartellera i un index que es refereix a la pel·lícula idx del llistat de pellicules, retorna els cinemes en els quals s'emet"""
    cinemas: Set[str] = set()
    film_name:str = bb.films[idx].title
    
    for projection in bb.projections:
        if projection.film.title == film_name:
            cinemas.add(projection.cinema.name)
    
    return cinemas


def films_information(films: List[str], billboard: Billboard.Billboard) -> bool:
    """Funció que dona informació rellevant sobre pel·lícules que li dones"""
    input_2 = input('\033[1m' + '\nSi voleu més informació sobre una pel·lícula, introduïu el seu nom, sinó, escriviu EXIT: ' + '\033[0m')
    show: bool = True
    if input_2 in films:
        idx = films.index(input_2)
        cinemas: Set[str] = get_film_cinemas(billboard, idx)
        print_negreta('\n' + input_2 + '\n')
        
        print_negreta('Directors: ')
        print(*billboard.films[idx].directors, sep = ", ")

        print_negreta('Actors: ')
        print(*billboard.films[idx].actors, sep = ", ")

        print_negreta('Gèneres: ')
        print(*billboard.films[idx].genre, sep = ", ")

        print_negreta('Cinemes: ')
        print(*cinemas, sep = ", ")
        print('Si voleu més informació sobre els cinemes i projeccions, siusplau redirigiu-vos al buscador de cinemes.')

        if input('\033[1m' + "\n\nVols cercar una altra pel·lícula? (y/n): " + '\033[0m') == 'n': 
            show = False

    elif input_2 != 'EXIT':
        print('Aquesta pel·lícula no és a la llista, siusplau triïn una que hi sigui:\n')

    else:
        show = False
    
    return show


def get_set_genres(bb: Billboard.Billboard) -> Set[str]:
    """Retorna el conjunt de gèneres de tot Barcelona"""
    genres: Set[str] = set()
    
    for film in bb.films:
        genres.update(film.genre)
    
    return genres


def get_genre_films(bb: Billboard.Billboard, genre_input: str) -> Set[str]:
    """Donat un gènere retorna totes les pel·lícules d'aquell gènere"""
    films: Set[str] = set()

    for film in bb.films:
        for genre in film.genre:
            if genre == genre_input:
                films.add(film.title)
    
    return films


def make_buses_graph() -> Buses.BusesGraph:
    """crea el graf de busos"""
    return Buses.get_buses_graph()


def save_buses_graph() -> None:
    """Guarda el graf de busos"""
    bg: Buses.BusesGraph = make_buses_graph()
    filename = 'BusesGraph'
    file = open(filename, 'wb')
    pickle.dump(bg, file)
    file.close()


def load_buses_graph() -> Buses.BusesGraph:
    """Carrega el graf de busos"""
    assert os.path.exists('BusesGraph')
    file = open('BusesGraph', 'rb')
    g = pickle.load(file)
    file.close()

    return g


def show_buses_graph() -> None:
    """Mostra el graf de busos"""
    buses_graph: Buses.BusesGraph = load_buses_graph()
    show: bool = True
    while show:    
        input_1 = input('\033[1m' + "\n\nDe quina manera voldries veure el graf de busos de Barcelona?:\n     1 - De manera interactiva en una altra finestra\n     2 - Amb una imatge de Barcelona amb la seva xarxa de busos\n     3 - EXIT - Tornar enrere\n" + '\033[0m')
        
        if input_1 == '1':
            Buses.show_buses(buses_graph)
            if input('\033[1m' + "\n\nVol tornar a veure el graf de busos? (y/n): " + '\033[0m') == 'n':
                show = False

        elif input_1 == '2':
            input_2 = input('\033[1m' + "\n\nBona elecció, amb quin nom vol guardar la imatge del graf de busos? " + '\033[0m')
            Buses.plot_buses(buses_graph, input_2 + '.png')
            if input('\033[1m' + "\n\nVol tornar a veure el graf de busos? (y/n): " + '\033[0m') == 'n':
                show = False
        
        elif input_1 != 'EXIT':
            print("Perdoni, els únics paràmetres d'entrada vàlids són: 1, 2, EXIT.\n")
        
        else:
            show = False


def make_street_graph() -> City.OsmnxGraph:
    """Crea el graf de carrers"""
    return City.get_osmnx_graph()


def save_street_graph() -> None:
    """guarda el graf de carrers"""
    sg: City.OsmnxGraph = make_street_graph()
    City.save_osmnx_graph(sg, 'StreetGraph')


def load_street_graph() -> City.OsmnxGraph:
    """carrega el graf de carrers"""
    return City.load_osmnx_graph('StreetGraph')


def save_city_graph() -> None:
    """guarda el graf ciutat"""
    bg: Buses.BusesGraph = load_buses_graph()
    sg: City.OsmnxGraph = load_street_graph()
    cg: City.CityGraph = City.build_city_graph(sg, bg)
    file = open('CityGraph', 'wb')
    pickle.dump(cg, file)
    file.close()


def load_city_graph() -> City.CityGraph:
    """carrega el graf ciutat"""
    assert os.path.exists('CityGraph')
    file = open('CityGraph', 'rb')
    cg = pickle.load(file)
    file.close()

    return cg


def show_city_graph() -> None:
    """Mostra el graf ciutat"""
    cg: City.CityGraph = load_city_graph()
    show: bool = True
    while show:    
        input_1 = input('\033[1m' + "\n\nDe quina manera voldries veure el graf de la ciutat de Barcelona?:\n     1 - De manera interactiva en una altra finestra\n     2 - Amb una imatge de Barcelona amb la seva xarxa de carrers i busos\n     3 - EXIT - Tornar enrere\n" + '\033[0m')
        
        if input_1 == '1':
            City.show(cg)
            if input('\033[1m' + "\n\nVol tornar a veure el graf de Barcelona? (y/n): " + '\033[0m') == 'n':
                show = False

        elif input_1 == '2':
            input_2 = input('\033[1m' + "\n\nBona elecció, amb quin nom vol guardar la imatge del graf de la ciutat? " + '\033[0m')
            City.plot(cg, input_2 + '.png')
            if input('\033[1m' + "\n\nVol tornar a veure el graf de Barcelona? (y/n): " + '\033[0m') == 'n':
                show = False
        
        elif input_1 != 'EXIT':
            print("Perdoni, els únics paràmetres d'entrada vàlids són: 1, 2, EXIT.\n")
        
        else:
            show = False


def ordenar_per_hores(tupla: tuple[str, tuple[int, int], str]) -> tuple[int,int]:
    """Ordena per hores"""
    return tupla[1][0], tupla[1][1]


def get_path_cinema(address: str, orig_coord: City.Coord, projection_hour: Tuple[int, int], cinema_name: str) -> City.Path:
    """Crea el camí més curt per anar al cinema escollit"""
    lat_dest, lon_dest = ox.geocoder.geocode(address)
    print('Calculant ruta per anar a ' + cinema_name + ' per anar a veure la sessió de les ' + str("{:02d}".format(projection_hour[0])) + ':' + str("{:02d}".format(projection_hour[1])) + '...', sep='')

    cg = load_city_graph()

    path: City.Path = City.find_path(load_street_graph(), cg, orig_coord, (lat_dest, lon_dest))

    path_time: float = 0.0
    for i in range(len(path) - 1):
        attributes = cg.get_edge_data(path[i], path[i + 1])
        path_time += attributes['time']
    
    initial_hour = datetime.now()
    arrival_time = initial_hour + timedelta(hours = path_time)
    todays_date = datetime.now().date()
    projection_time = datetime.combine(todays_date, datetime.min.time()).replace(hour=projection_hour[0], minute=projection_hour[1])
    
    if arrival_time > projection_time:
        print('No hi arribariem a temps... ;(')
        return []
    else:
        path.append(str(path_time))
        return path


def get_path_film(cg: City.CityGraph, film_title:str, bb: Billboard.Billboard, coord_orig: City.Coord) -> Tuple[City.Path, float, str, Tuple[int, int]]:
    """Genera el camí més curt per anara a veure la pel·lícula desitjada"""
    projections: List[Tuple[str, Tuple[int, int], str]] = list()

    for projection in bb.projections:
        if projection.film.title == film_title and projection.time[0] >= datetime.now().hour and projection.time[1] >= datetime.now().minute:
            projections.append((projection.cinema.address, projection.time, projection.cinema.name))
    
    projections = sorted(projections, key = ordenar_per_hores)

    path: City.Path = list()
    i: int = 0
    while len(path) == 0 and i < len(projections):
        path = get_path_cinema(projections[i][0], coord_orig, projections[i][1], projections[i][2])
        i += 1
    if len(path) != 0:    
        travel_time: float = float(path.pop())
        return (path, travel_time, projections[i - 1][2], projections[i][1])
    else: 
        return ([], 0.0, '', (0,0))
    

def go_to_film() -> None:
    """Anara a veure la pel·lícula desitjada!"""
    billboard: Billboard.Billboard = load_billboard()
    list_films: List[str] = list()
    for film in billboard.films:
        list_films.append(film.title)
    
    show: bool = True
    while show:
        print_negreta('\nAquestes són totes les pel·lícules de Barcelona:\n')
        print(*list_films, sep="\n")
        input_1 = input('\033[1m' + "\nJa tens triada la pel·lícula que vols anar a mirar? Perfecte, jo t'hi porto! Indiqui el nom de la pel·lícula que vol anar a mirar (EXIT per tornar enrere): " + '\033[0m')

        if input_1 in list_films:
            show_2: bool = True
            while show_2:
                input_2 = input('\033[1m' + "\nBona tria! " + input_1 + ' és molt bona. Siusplau indiqui les coordenades en les que es troba ara mateix de la forma: latitud, longitud (Si les coordenades indicades no corresponen a Barcelona, generaran errors en el càlcul de rutes.), si voleu tornar enrere escriviu EXIT: ' + '\033[0m')
                try:
                    latitud_str, longitud_str = input_2.split(',') 
                    (lat_orig, lon_orig) = float(latitud_str), float(longitud_str)

                    if lat_orig < 41.0 or lat_orig > 42.0 or lon_orig < 2.0 or lon_orig > 3.0:
                        print("\nAl Pallars no hi ha cinemes carallot! Les coordenades introduïdes són d'un punt lluny de Barcelona, siusplau introdueixi unes coordenades de Barcelona: ")

                    else:
                        path, travel_time, cinema, proj_time = get_path_film(load_city_graph(), input_1, billboard, (lat_orig, lon_orig))
                        if len(path) != 0:
                            travel_time *= 60
                            input_3 = input('\033[1m' + "\nRuta calculada! Temps de viatge: " + str(round(travel_time, 0)) + " minuts aproximadament fins a " + cinema + " per anar a veure el 'peliculón' de " + input_1 + " a les " + str(proj_time[0]) + ':' + str(proj_time[1]) + ". Siuspau indiqui el nom amb el qual vol guardar la imatge de la ruta fins al cinema: " + '\033[0m')
                            City.plot_path(load_city_graph(), path, input_3 + '.png')
                            show_2 = False

                            if input('\033[1m' + "\n\n Ja tens la ruta desada com una imatge al teu ordinador ;). Vols anar a veure una altra pel·lícula? (y, n): " + '\033[0m') == 'n':
                                show = False
                        else:
                            print('\nQuin greu!, és impossible que arribis a temps avui a veure ' + input_1)
                            show_2 = False

                except ValueError:
                    print("Les coordenaes inicials no són vàlides. Siusplau introduïu unes coordenades de la forma: latitud, longitud")
                    show_2 = False


        elif input_1 != 'EXIT':
            print("Perdoni, la pel·lícula que ha indicat no es troba a la llista de pel·lícules de Barcelona, siusplau indiquin una que hi sigui: \n")
        
        else:
            show = False


def main() -> None:
    print_negreta("Abans de començar amb el programa, es descarregaran quatre fitxers per a ser utilitzats més endavant, l'operació pot tardar uns minuts, siusplau no cancel·li el programa ni premi cap tecla mentre s'estiguin descarregant els fitxers.")
    
    input('\nPremi ENTER per continuar...')
    save_billboard()
    save_buses_graph()
    save_street_graph()
    save_city_graph()
    show: bool = True
    while show:
        input_1 = input('\033[1m' + '\n\nBenvigut al millor buscador de pel·lícules de tot Barcelona, gràcies per confiar en els nostres serveis ;). A continuació li mostro les principals funcionalitats del programa:\n\
     1 - Autor del projecte\n     2 - Mostrar cartelleres Barcelona\n     3 - Cercar per la cartellera de Barcelona\n     4 - Mostrar xarxa de Busos de Barcelona\n     5 - Mostrar xarxa de carrers i busos de Barcelona\n\
     6 - Anar a veure una pel·lícula\n     7 - Actualitzar cartellera\n     EXIT - Per finalitzar el programa\n' + '\033[0m')

        if input_1 == '1':
            authors()
            input("\n\nUs redirigirem altre cop a la pàgina d'inici. Pressiona ENTER per continuar... ")
        
        elif input_1 == '2':
            show_billboard()
            input("\n\nUs redirigirem altre cop a la pàgina d'inici. Pressiona ENTER per continuar... ")
        
        elif input_1 == '3':
            search_billboard()
            input("\n\nUs redirigirem altre cop a la pàgina d'inici. Pressiona ENTER per continuar... ")
        
        elif input_1 == '4':
            show_buses_graph()
            input("\n\nUs redirigirem altre cop a la pàgina d'inici. Pressiona ENTER per continuar... ")
        
        elif input_1 == '5':
            show_city_graph()
            input("\n\nUs redirigirem altre cop a la pàgina d'inici. Pressiona ENTER per continuar... ")
        
        elif input_1 == '6':
            go_to_film()
            input("\n\nUs redirigirem altre cop a la pàgina d'inici. Pressiona ENTER per continuar... ")

        elif input_1 == '7':
            print("\nL'operació tardara uns segons, siusplau no premi cap tecla mentre el fitxer es descarrega...")
            save_billboard()
            input("\n\nCartellera actualitzada! Us redirigirem altre cop a la pàgina d'inici. Pressiona ENTER per continuar... ")
        
        elif input_1 != 'EXIT':
            print_negreta('\nHeu introduït un paràmetre no vàlid. Els únics paràmetres vàlids són: 1, 2, 3, 4, 5, 6, 7, EXIT. Siusplau introduïu-ne un de vàlid\n')
        
        else:
            show = False

if __name__ == '__main__':
    main()