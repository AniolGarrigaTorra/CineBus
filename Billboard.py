from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Set, Tuple, Any

@dataclass 
class Film: 
    title: str
    genre: list[str]
    directors: list[str]
    actors: list[str]

@dataclass
class Cinema: 
    name: str
    address: str

@dataclass 
class Projection: 
    film: Film
    cinema: Cinema
    time: tuple[int, int]   # hora:minut
    language: str

@dataclass 
class Billboard: 
    films: list[Film]
    cinemas: list[Cinema]
    projections: list[Projection]


def filter_films(film: Film, films: list[Film]) -> None:           #No podem fer list(set(films)) perquè ens surt: <TypeError: unhashable type: 'Film'>
    """Aquesta funció afegeix a la llista de pel·lícules només aquelles que no hi són ja abans en la llista"""
    added: bool = False
    i: int = 0
    while i < len(films) and not added:
        if film.title == films[i].title:
            added = True 
        i += 1
    if not added:
        films.append(film)                  #augmentem així la longitud, perquè així ens estalviem d'haver de mesurar-la (O(n)) cada cop que volem afegir una pel·lícula a la llista                


def fix_adresses(address: str) -> str:
    """S'encarrega d'arreglar les adreces dels cinemes de Barcelona, que tenen unes molt mal adreces"""
    return address.replace('Calle', 'Carrer')\
        .replace('Avda.', 'Avinguda')\
        .replace('Avenida', 'Avinguda')\
        .replace('Paseig', 'Passeig')\
        .replace('Centro Comercial Splau! -', '')\
        .replace('- Centro Comercial Gran Vía 2', '')\
        .replace('Sta Fé', 'Carrer de Santa Fe')\
        .replace('Paseo', 'Passeig')\
        .replace('- Centro Comercial La Maquinista', '')\
        .replace('Andreu', 'D\'Andreu')\
        .replace('s/n - Pintor Alzamora', '')\
        .replace('Avinguda Josep Tarradellas', 'Avinguda de Josep de Tarradellas i Joan')\
        .replace('Avinguda Virgen Montserrat', 'Avinguda Verge de Montserrat')\
        .replace('Centro Comercial Baricentro - Carretera Nacional 150', 'N-150')\
        .replace('Carrer Salvador Espriu', 'Carrer de Salvador Espriu')\
        .replace('Carrer Verdi', 'C/ de Verdi')\
        .replace('Carrer Aribau', 'Aribau - Gran Via')


def get_soup(page: int) -> BeautifulSoup:
    """Donada la pàgina que hem de cercar, entra en el link i obté la seva sopa de dades (soup)"""
    if page == 0: 
            url = "https://www.sensacine.com/cines/cines-en-72480/"                                 #Degut a que si acabem el url amb page=1 en el primer url, dona errors
    else:
        url = "https://www.sensacine.com/cines/cines-en-72480/?page=" + str(page + 1)
    
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


def get_proj_and_cinema_entries(i: int, projection_entries: list[Any], cinema_entries: list[Any]) -> Tuple[str, str, list[Any]]:
    """Consegueix de totes les entrades, l'entrada d'un cine i l'entrada de les seves projeccions. Retorna ja el nom del cinema i l'adreça, i l'entrada de les projeccions"""
    proj_entry = projection_entries[i]
    cinema_entry = cinema_entries[i]

    cinema_name:str = cinema_entry.find("a", class_ = "no_underline j_entities").get_text().replace("\n", "")             #Els replace els fem perquè ens surtin els strings bonics
    cinema_adress:str = list(cinema_entry.find_all("span", class_="lighten"))[1].get_text().replace("\n", "")         #fem el list(set)[1] per què hi ha dos ("span", class_="lighten") i així treiem el que volem
    cinema_adress = fix_adresses(cinema_adress)

    return cinema_name, cinema_adress, proj_entry


def read() -> Billboard:
    """Llegeix, utilitzant web scraping, les dades que ens interessen de les pàgines de SensaCine tot retornant una classe Billboard de la cartellera completa de Barcelona"""
    films: List[Film] = list()
    cinemas: List[Cinema] = list()
    projections: List[Projection] = list()

    for page in range(3):
        
        soup = get_soup(page)

        cinema_entries = list(soup.find_all('div', class_="margin_10b j_entity_container"))
        projection_entries = list(soup.find_all('div', class_ = "j_w j_tabs"))

        for i in range(len(cinema_entries)):
            
            cinema_name, cinema_adress, proj_entry = get_proj_and_cinema_entries(i, projection_entries, cinema_entries)

            if 'Barcelona' in cinema_adress:
                cinema = Cinema(cinema_name, cinema_adress)
                cinemas.append(cinema)

                item_0 = proj_entry.find('div', class_ = "tabs_box_pan item-0")
                
                if item_0 is not None:
                    items = item_0.find_all("div", class_="item_resa")
                
                    for item in items:
                        jw = item.find("div", class_="j_w")
                        
                        theater = jw.get("data-theater")
                        movie = jw.get("data-movie")
                        theater_dict = json.loads(theater)
                        movie_dict = json.loads(movie)

                        film = Film(movie_dict['title'], movie_dict['genre'], movie_dict['directors'], movie_dict['actors'])
                        filter_films(film, films)
                        lenguage = jw.find("span", class_ = "bold").get_text().replace(" ", "")             #el replace es per esborrar tots els espais en blanc

                        for em in item.find_all("em"):
                            times = em.get("data-times")
                            times_tuple = json.loads(times)[0].split(":")                       #ja que el format en el quals ens donen l'hora d'inici és "H:M"

                            time_hour, time_minute = int(times_tuple[0]), int(times_tuple[1])
                            if lenguage == "VersiónOriginal":
                                projections.append(Projection(film, cinema, (time_hour, time_minute), 'Versió Original' ))
                            else:
                                projections.append(Projection(film, cinema, (time_hour, time_minute), 'Versió Doblada' ))

    
    return Billboard(films, cinemas, projections)
        
        
