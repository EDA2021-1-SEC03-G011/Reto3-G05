﻿"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """

import random
import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.DataStructures import linkedlistiterator as slit
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""
# ======================
# Creacion del catalogo
# ======================

def newCatalog():
    catalog = {'user-track-createdMap':None,
               'eventMap':None,
               'trackMap':None,
               'tempoMap':None,
               'trackTempoMap':None,
               'genres':None,
               'characteristics':None
               }

    catalog['user-track-createdMap'] = om.newMap(omaptype='BST')

    catalog['eventMap'] = om.newMap(omaptype='BST')

    catalog['trackMap'] = om.newMap(omaptype='BST')

    catalog['tempoMap'] = om.newMap(omaptype='RBT')

    catalog['trackTempoMap'] = om.newMap(omaptype='RBT')

    catalog['genres'] = {'reggae':(60,90),'down-tempo':(70,100),'chill-out':(90,120),'hip-hop':(85,115),
                         'jazz and funk':(120,125),'pop':(100,130),"r&b":(60,80),'rock':(110,140),'metal':(100,160)}

    catalog['characteristics'] = ['instrumentalness','liveness','speechiness','danceability',
                                  'valence','acousticness','energy']

    return catalog

# ==============================================
# Funciones para agregar informacion al catalogo
# ==============================================

def addUserTrack(catalog, usertrack):
    """
    Durante la carga del archivo user-track se guarda en el mapa 'user-track-createdMap'
    un evento unico identificado por (user+track+created)
    """
    userTrackMap = catalog['user-track-createdMap']
    event = (usertrack['user_id'],usertrack['track_id'],usertrack['created_at'])
    om.put(userTrackMap,event, usertrack)


def eventInUserTrackMap(catalog, event):
    id_event =(event['user_id'],event['track_id'],event['created_at'])
    track_id = event['track_id']
    """
    Para cada evento que se repite en los dos archivos se agrega a un RBT que los
    clasifica por Tempo
    Ademas se filtra por track_id para luego meter los tracks segun el Tempo en 
    otro RBT
    """
    #Creando los mapas mirando si el evento se repite en ambos archivos

    if om.contains(catalog['user-track-createdMap'],id_event):
        om.put(catalog['eventMap'],id_event,event)
        

        #Creando el mapa 'tempoMap' segun eventos (user+track+created) unicos

        if om.contains(catalog['tempoMap'],float(event['tempo'])):
            couple = om.get(catalog['tempoMap'],float(event['tempo']))
            list = me.getValue(couple)
            lt.addLast(list,event)

        else:
            list = lt.newList(datastructure='SINGLE_LINKED')
            lt.addLast(list,event)
        om.put(catalog['tempoMap'],float(event['tempo']),list)

        #Creando el mapa 'trackMap' segun tracks unicos y creando el trackTempoMap 

        if om.contains(catalog['trackMap'],track_id) == False:
            om.put(catalog['trackMap'],track_id,event)

            if om.contains(catalog['trackTempoMap'],float(event['tempo'])):
                couple = om.get(catalog['trackTempoMap'],float(event['tempo']))
                list = me.getValue(couple)
                lt.addLast(list,event)

            else:
                list = lt.newList(datastructure='SINGLE_LINKED')
                lt.addLast(list,event)
            om.put(catalog['trackTempoMap'],float(event['tempo']),list)


# ================================
# Funciones para creacion de datos
# ================================

def createArtistMap(tempoList):
    # FUNCION REQ 4
    map = mp.newMap(maptype='PROBING')

    iterator = slit.newIterator(tempoList)
    while slit.hasNext(iterator):
        event = slit.next(iterator)
        
        artist = event['artist_id']
        mp.put(map,artist,event)
    return mp.size(map)


def createTempoList(tempoMap, loTempo, hiTempo):
    # FUNCION REQ 3, REQ 4
    """
    Recibe por parametro un RBT del tempo y los rangos, retorna una lista con 
    los eventos/tracks que estan en ese rango
    """
    listOfLists = om.values(tempoMap, loTempo, hiTempo)
    answerMap = mp.newMap(maptype='CHAINING',loadfactor=1.0,numelements=28000)

    iteratorLists = slit.newIterator(listOfLists)
    while slit.hasNext(iteratorLists):
        list = slit.next(iteratorLists)

        iteratorSongs = slit.newIterator(list)
        while slit.hasNext(iteratorSongs):
            song = slit.next(iteratorSongs)
            id = song['user_id'],song['track_id'],song['created_at']
            mp.put(answerMap, id, song)
    
    return mp.valueSet(answerMap)


def createInstruList(tempoList,loInstru,hiInstru):
    #FUNCION UNICA REQ 1
    """
    Recibe por parametro una lista con los tempos filtrados y rangos
    de instrumentalidad, y retorna una lista de tracks con la instrumentalidad 
    filtrada dentro de los rangos
    """
    instruList = lt.newList(datastructure="SINGLE_LINKED")

    iterator = slit.newIterator(tempoList)
    while slit.hasNext(iterator):
        event = slit.next(iterator)

        if float(event['instrumentalness'])>= loInstru and float(event['instrumentalness'])<= hiInstru:
            lt.addLast(instruList, event)

    return instruList


def createSubList(list, rank):
    # FUNCION REQ 4
    sublist = lt.subList(list,1,rank)
    return sublist


def filterByChar(catalog, characteristic, loValue,hiValue):
    # FUNCION UNICA REQ 1
    list = om.valueSet(catalog['eventMap'])
    answerMap = mp.newMap(maptype='PROBNG', numelements=1800)
    counter = 0


    for event in lt.iterator(list):
        if float(loValue) <= float(event[characteristic]) <= float(hiValue):
            counter += 1
            mp.put(answerMap, event['artist_id'],event)
    
    return (counter, mp.size(answerMap))


# =====================    
# Funciones de consulta
# =====================

def eventsSize(catalog):
    return lt.size(catalog['eventList'])

def artistsSize(catalog):
    return om.size(catalog['artistMap'])

def tracksSize(catalog):
    return om.size(catalog['trackMap'])

def uniqueSongsChar(charList):
    return lt.size(charList)

def mapSize(map):
    return om.size(map)

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento

# ====================================
# Funciones creacion datos por usuario
# ====================================

def askGenre(catalog):
    # FUNCION UNICA REQ 4
    continuing = True
    genreList = []
    genreDictionary = catalog['genres']

    while continuing == True:
        print("\nLos generos disponibles son")
        print("\nGenero\tBMP Tipico")
        for genre in genreDictionary.keys():
            print(str(genre)+"\t"+str(genreDictionary[genre]))
        print("\nQue accion desea realizar:\n")
        print(">1< Agregar un nuevo genero al diccionario")
        print(">2< Agregar un genero a la lista de busqueda")
        print(">3< Finalizar proceso y comenzar a buscar")
        action = int(input("\nDigite el numero de la accion deseada: "))

        if action == 1:
            newGenreName = input("Ingrese el nombre unico para el nuevo genero musical: ")
            loTempo = int(input("Digite el valor entero minimo del tempo del nuevo genero musical: "))
            hiTempo = int(input("Digite el valor entero maximo del tempo del nuevo genero musical: "))
            correct = verifyRanges(loTempo,hiTempo)
            if correct:
                genreDictionary[newGenreName] = (loTempo,hiTempo)
            else:
                print("Los rangos ingresados no son validos")

        elif action == 2:
            print("La lista de busqueda que tiene es la siguiente "+str(genreList))
            existingGenre = input("Ingrese el nombre del genero que desea agregar a la busqueda: ")
            if existingGenre in genreDictionary:
                genreList.append(existingGenre)
            else:
                print("\n>>>El genero deseado no existe en el diccionario<<<")
        
        elif action == 3:
            print("La lista de busqueda que tiene es la siguiente "+str(genreList))
            continuing = False
    
    return genreList

def verifyRanges(loRange,hiRange):
    # FUNCION REQ 1, REQ 3, REQ4
    """
    Verifica que los rangos proporcionados por el usuario sean validos
    """
    correct = False
    if (loRange <= hiRange) and loRange>=0 and hiRange>=0:
        correct = True
    return correct


# =======================
# Funciones para imprimir
# =======================

def printReqThree(list,loInstru,hiInstru,loTempo,hiTempo):
    # FUNCION UNICA REQ 3
    top = 5
    if top > lt.size(list):
        top = lt.size(list)
    randomList = random.sample(range(1, lt.size(list)), top)
    counter = 1
    print("\n+++++++ Resultados Req No. 3 +++++++")
    print("Instrumentalidad entre: "+ str(loInstru)+" - "+str(hiInstru))
    print("Tempo entre: "+ str(loTempo)+" - "+str(hiTempo))
    print("Total de tracks encontrados: "+str(lt.size(list)))
    print("")
    for i in randomList:
        song = lt.getElement(list, i)
        print("Track "+str(counter)+": "+ song['track_id']+" con instrumentalness de: "+str(song['instrumentalness'])+" y tempo de: "+str(song['tempo'])+str(song['created_at']))
        counter +=1

def printReqFour(genreResults,totalReproductions):
    # FUNCION UNICA REQ 4
    print("\n+++++++ Resultados Req No. 4 +++++++")
    print("Total de reproducciones: "+str(totalReproductions))
    for genre in genreResults.keys():
        tempo = genreResults[genre]['tempo']
        reproductions = genreResults[genre]['reproductions']
        artists = genreResults[genre]['artists']
        list = genreResults[genre]['list']
        print("\n\n======== "+genre.upper()+" ========")
        print("Para "+genre+" el tempo esta entre "+str(tempo[0])+" y "+str(tempo[1])+" BPM")
        print("El total de reproducciones de "+genre+" son: "+str(reproductions)+" con "+str(artists) +" diferentes artistas")
        print("Algunos artistas para "+genre)

        iterator = slit.newIterator(list)
        counter = 1

        while slit.hasNext(iterator):
            event = slit.next(iterator)
            print("Artista "+str(counter)+": "+event['artist_id'])
            counter +=1
