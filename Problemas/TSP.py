#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = 'daniel'
import numpy as np
import random
from Objetos.Individuo import Individuo
from Objetos.Poblacion import Poblacion
import math


class ConfiguracionTSP:

    def __init__(self, n=1):
        self.id = 0
        self.aristas = np.zeros((n, n))
        self.nPosiciones = 2
        self.nVecesMuta = 1
        self.porcentajeMutacion = .10
        random.seed()

    def registroCamino(self, origen, destino, valor):
        self.aristas[origen][destino] = valor
        self.aristas[destino][origen] = valor


    def generaPoblacion(self, configuracion, confProblema,total):
        poblacion = Poblacion()
        for i in range(0,total):
            aux = Individuo(i)
            lista=range(len(confProblema.otrosDatos.aristas))
            random.shuffle(lista)

            aux.nDimensiones = len(confProblema.otrosDatos.aristas)
            aux.valores = lista
            aux.aptitud = confProblema.otrosDatos.calculaFitness(aux)
            poblacion.individuos.append(aux)

        return poblacion

    def cruzaOrdenada(self,padre1, padre2):
        #Copio los valores
        hijo1 = Individuo(-1)
        hijo2 = Individuo(-1)
        hijo1.nDimensiones = padre1.nDimensiones
        hijo2.nDimensiones = padre2.nDimensiones

        # Cruza Ordenada
        punto1 = random.randrange(padre1.nDimensiones)
        punto2 = punto1
        while punto2 == punto1:
            punto2 = random.randrange(padre1.nDimensiones)

        if punto2<punto1:
            aux=punto1
            punto1 = punto2
            punto2 = aux

        centro1 = padre1.valores[punto1:punto2]
        centro2 = padre2.valores[punto1:punto2]
        # Ordeno los centros
        auxP1 = []
        auxP2 = []
        for i,j in zip(padre1.valores,padre2.valores):
            if i in centro2:
                auxP2.append(i)
            if j in centro1:
                auxP1.append(j)
        centro1 = auxP1[:]
        centro2 = auxP2[:]

        #Creo los hijos
        hijo1.valores = padre1.valores[:punto1]+auxP1+padre1.valores[punto2:]
        hijo2.valores = padre2.valores[:punto1]+auxP2+padre2.valores[punto2:]

        return  hijo1, hijo2

    def cruzaPosicion(self, padre1, padre2):
        #Cruza basada en posición
        #Copio los valores
        hijo1 = Individuo(-1)
        hijo2 = Individuo(-1)
        hijo1.nDimensiones = padre1.nDimensiones
        hijo2.nDimensiones = padre2.nDimensiones

        hijo1.valores = padre1.valores[:]
        hijo2.valores = padre1.valores[:]
        lista=range(padre1.nDimensiones)
        #Paso 1
        random.shuffle(lista)
        corte=self.nPosiciones
        #posicionesBuenas=lista[corte:]
        posicionesMalas=lista[corte:]
        #Elimino de P1 todos los valores excepto los elegidos
        listaValoresBorrados=[]
        listaValoresBorrados2=[]
        for i in posicionesMalas:
            #Hijo1
            listaValoresBorrados.append(hijo1.valores[i])
            hijo1.valores[i]=None
            #Hijo2
            listaValoresBorrados2.append(hijo2.valores[i])
            hijo2.valores[i]=None
        restantes = []
        restantes2=[]
        for (i,j) in zip(padre2.valores,padre1.valores):
            #Hijo1
            if i in listaValoresBorrados:
                restantes.append(i)
            #Hijo2
            if j in listaValoresBorrados2:
                restantes2.append(j)
        bandera=0
        bandera2=0


        for i in range(0,len(hijo1.valores)):
            if hijo1.valores[i] == None:
                hijo1.valores[i]=restantes[bandera]
                bandera+=1
            if hijo2.valores[i] == None:
                hijo2.valores[i]=restantes2[bandera2]
                bandera2+=1


        return hijo1,hijo2

    def mutacionInsercion(self,hijo1,confproblema):
        #Mutación por insert
        for i in range(0,self.nVecesMuta):
            aleatorio=np.random.random()
            pos1=random.randrange(0,math.ceil(hijo1.nDimensiones/2))
            while(aleatorio<=self.porcentajeMutacion):
                aleatorio=np.random.random()
                pos1=random.randrange(0,math.ceil(hijo1.nDimensiones/2))

            aleatorio=np.random.random()
            pos2=random.randrange(math.ceil(hijo1.nDimensiones/2),hijo1.nDimensiones)
            while(aleatorio<=self.porcentajeMutacion):
                aleatorio=np.random.random()
                pos2=random.randrange(math.ceil(hijo1.nDimensiones/2),hijo1.nDimensiones)

            #Insert
            tmp=hijo1.valores[pos2]
            del[hijo1.valores[pos2]]
            hijo1.valores.insert(pos1+1,tmp)

        hijo1.aptitud=confproblema.otrosDatos.calculaFitness(hijo1)
        return hijo1

    def mutacionIntercambio(self,hijo1,confproblema):
        for i in range(0,self.nVecesMuta):
            aleatorio=np.random.random()
            pos1=random.randrange(0,math.ceil(hijo1.nDimensiones/2))
            while(aleatorio<=self.porcentajeMutacion):
                aleatorio=np.random.random()
                pos1=random.randrange(0,math.ceil(hijo1.nDimensiones/2))

            aleatorio=np.random.random()
            pos2=random.randrange(math.ceil(hijo1.nDimensiones/2),hijo1.nDimensiones)
            while(aleatorio<=self.porcentajeMutacion):
                aleatorio=np.random.random()
                pos2=random.randrange(math.ceil(hijo1.nDimensiones/2),hijo1.nDimensiones)
            #Swap
            tmp=hijo1.valores[pos1]
            hijo1.valores[pos1]=hijo1.valores[pos2]
            hijo1.valores[pos2]=tmp
        hijo1.aptitud=confproblema.otrosDatos.calculaFitness(hijo1)
        return hijo1

    def calculaFitness(self,individuo):
        sumatoria=0
        puntoInicio=individuo.valores[0]

        for i in range(0,individuo.nDimensiones):
            origen=individuo.valores[i]

            if i == individuo.nDimensiones-1:
                destino=puntoInicio
            else:
                destino=individuo.valores[i+1]

            sumatoria+=self.aristas[origen][destino]

        return sumatoria

    def cargarTSPLib(self,archivo):

        archi=open(archivo,'r')
        datos=[]
        linea=archi.readline().rstrip("\n")

        while linea.strip()!="NODE_COORD_SECTION":
            linea=archi.readline()


        linea=archi.readline()
        while linea.strip()!="EOF":
            aux=linea.rstrip('\n').split(" ")

            del(aux[0])
            aux[0]=float(aux[0])
            aux[1]=float(aux[1])
            datos.append(aux)
            linea=archi.readline()

        archi.close()
        #LLenar la tabla de datos
        self.aristas=np.zeros((len(datos),len(datos)))

        for i in range(0,len(datos)):
            for j in range(i):
                distancia=math.sqrt(((datos[i][0]-datos[j][0])**2)+((datos[i][1]-datos[j][1])**2))
                self.registroCamino(i,j,distancia)

    def cargarTSPSolucion(self,archivo):

        archi=open(archivo,'r')
        datos=[]
        linea=archi.readline().rstrip("\n")

        while linea.strip()!="TOUR_SECTION":
            linea=archi.readline()


        linea=archi.readline()
        while linea.strip()!="-1":
            aux=linea.rstrip('\n').split(" ")
            aux[0]=float(aux[0])
            datos.append(float(aux[0]))
            linea=archi.readline()

        archi.close()
        #LLenar la tabla de datos
        sumatoria=0
        puntoInicio=datos[0]-1

        for i in range(0,len(datos)):
            origen=datos[i]-1

            if i == len(datos)-1:
                destino=puntoInicio
            else:
                destino=datos[i+1]-1

            sumatoria+=self.aristas[origen][destino]
        print ("SUmatoria: "+str(sumatoria))