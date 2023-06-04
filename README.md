# CineBus
Tria una pel·li i ves-hi en Bus!🚌 🎬 
## Introducció
CineBus és un programa amb multifuncions. Principalment, permet indagar a través d'un menú, pels cinemes i pel·lícules que s'emeten per tot Barcelona del dia actual amb un moment. També permet calcular i mostrar la xarxa de busos i la xarxa de busos i carrers de Barcelona. Per últim i més important, sap calcular rutes utilitzant la xarxa de busos i carres de la ciutat per arribar per exemple a una pel·lícula desitjada en aquell moment.
## Arquitectura del programa
CineBus es basa principalment en 4 sub programes: Demo.py, City.py, Buses.py, Billboard.py:

- `Demo.py`: Es bàsicament el menú del programa, demo.py utilitza els altres tres programes per a realitzar els càlculs i gestionar les funcions del programa CineBus.
- `Billboard.py`: S'encarrega d'aconseguir la cartellera del dia actual, utilitzant mètodes de web.scraping a la web de [Sensacine](https://www.sensacine.com/cines/cines-en-72480/).
- `Buses.py`: El mòdul Buses s'encarrega de generar el graf de la xarxa de busos de Barcelona a través de dades del [Catàleg OpenData de l'Àrea Metropolitana de Barcelona](https://www.amb.cat/s/web/area-metropolitana/dades-obertes/cataleg-opendata.html).
- `City.py`: Per últim el mòdul City s'encarrega de generar el graf de la xarxa de carrers, utilitzant dades d'[Open Street Map](https://www.openstreetmap.org). I genera també juntant el graf de busos del modul Buses i el graf de carrers, el graf de la ciutat (City) que conté totes les línies de bus, carrers peatonals de la ciutat i connexions parada de bus. A més el graf de la ciutat, conté molta informació sobre coordenades, distàncies, temps, linies de bus, etc. També és capaç de generar rutes per Barcelona d'un punt a un altre.

## Llibreries
CineBus, utilitza diverses llibreries que potser s'han d'instal·lar amb `pip3 install ...`:

- `requests`: per baixar-vos fitxers de dades.
- `bs4`: per utilitzar la llibreria de BeautifulSoup que serveix per llegir els arbres HTML.
- `json`: per manipular dades que estan amb format json.
- `networkx`: per a manipular grafs.
- `osmnx`: per a obtenir grafs de llocs (Barcelona en aquest cas).
- `staticmap`: per pintar mapes.
- `matplotlib.pyplot`: per a mostrar grafs de manera interactiva.
- `random`: per obtenir paràmetres aleatoris.
- `pickle`: per escriure i llegir grafs.
- `os`: per saber si un fitxer existeix.
- `datetime`: per manejar dades de tipus temps.

## Execució del programa
Per a executar el programa i entrar al menú, només cal executar el mòdul demo.py per exemple de la següent forma a la terminal de l'ordinador, un cop dins el directori CineBus:

```
python Demo.py
python3 Demo.py
```

Executant aquest programa ho tenim tot per començar. Al principi del programa es descarregaran el fitxer de la cartellera actual, graf de busos, graf de carrers i graf de la ciutat. Un cop generats i descarregats, se'ns obrirà un menú amb diferens funcions per a realitzar el que s'especifiqui. El programa acabarà quan excriguem `EXIT` al menú principal.

## Mòdul `Billboard`
El mòdul billboard està contingut principalment de la funció `read()` que s'encarrega de llegir dades que ens interessen de la cartellera de la web de [Sensacine](https://www.sensacine.com/cines/cines-en-72480/) i guardar-les en una dataclass anomenada Billboard, fent servir mètodes de web scraping. La dataclass Billboard està fromada per un llistat de totes les pel·lícules que s'emeten el dia actual a Barcelona, un llistat de tots els cinemes de Barcelona i per últim un llistat amb totes les projeccions dels diferents cines de Barcelona.

Aprofitem per a crear diferents dataclasses que serien les següents:
```python3
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
```

## Mòdul `Buses`
El mòdul Buses, s'encarrega de generar, amb la funció `get_buses_graph()`, un graf de les diferents línies de Bus de Barcelona, informació que extraiem del [Catàleg OpenData de l'Àrea Metropolitana de Barcelona](https://www.amb.cat/s/web/area-metropolitana/dades-obertes/cataleg-opendata.html).

A part, tenim la funció `show_buses()` i `plot_buses()` que s'encarreguen de mostrar el graf de busos a l'usuari. Amb `show_buses()` obtenim en una pantalla interactiva el graf, i amb `plot_buses()` desem el graf de busos amb la ciutat de Barcelona de fons en un arxiu.png

## Mòdul `City`
El mòdul City, s'encarrega bàsicament de tres coses principals:

- Creació i desament del graf de carrers de Barcelona fet amb la llibreria `osmnx`
- Unificació dels grafs de busos i carrers, generant així un sol graf que conté nodes de tipus 'parada' i 'cruïlla', i arestes de tipus 'linia' i 'carrer', que anomenem graf ciutat.
- Càlcul del camí més curt entre dos punts de Barcelona

En la primera part, tenim les funcions per a generar el graf `get_osmnx_graph()`, i guardar-lo i carregar-lo `save_osmnx_graph()` `load_osmnx_graph()`

En la segona Part, tenim les funcions per unificar els grafs i crear el graf ciutat `build_city_graph()` i les funcions per a mostrar el graf a l'usuari de forma idèntica a com ho fem amb el graf de busos `show()` `plot()`

En la tercera i útlima part, tenim les funcions per a calcular el camí més curt entre dos punts de Barcelona `find_path()` i la funció per mostrar el camí més curt amb un mapa de la ciutat de fons `plot_path()`

## Mòdul `Demo`
El mòdul demo s'encarrega de crear "l'interfície" on l'usuari pot obtenir diferents informacions depenent el que triï en aquesta interfície. Les principals funcions que realitza `Demo.py` són:
- Mostrar l'autor del projecte
- Mostrar les cartelleres de Barcelona
- Cercar per la cartellera de tot Barcelona
- Mostrar la xarxa de Busos de Barcelona (BusesGraph)
- Mostrar la xarxa de carrers i busos de Barcelona (CityGraph)
- Càlcul de la ruta per anar a veure una pel·lícula en concret
- Actualitzar la cartellera de Barcelona


## Conclusions
I això és tot, si voleu veure la cartellera de Barcelona, o buscar una pel·lícula interessant, o càlcular la ruta la qual arribi abans a veure una pel·lícula en concret, etc. Ja sabeu que heu de fer ;)! Executeu el programa i a disfrutar del Bo Cultural!

## Autor
Aniol Garriga Torra - Estudiant de primer en el Grau en Ciència i Enginyeria de Dades a la Universitat Politècnica de Catalunya




