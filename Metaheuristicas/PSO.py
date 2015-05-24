#!/usr/bin/python
# -*- coding: utf-8 -*
from distutils.command.config import config

__author__ = 'daniel'
from Objetos.Individuo import Individuo
from Objetos.Islas import Islas
from Objetos.Poblacion import Poblacion
import Constantes
from Problemas.Problemas import calculaFitness
from Problemas.Problemas import esMejor
from Problemas.Problemas import graficarFuncion
from Util import graficaConvergencia
from Objetos.Solucion import Solucion
import numpy
import math
from mpi4py import MPI
import time
class PSO:
    def __init__(self):
        self.C1=0
        self.C2=0


    def ejecutaPSOIsla(self,problema,configuracion,proceso,criterio,mejorIndividuo,copiaIndividuo):
        individuoGlobal=Individuo()
        isla=proceso
        C1=self.C1
        C2=self.C2
        nDimensiones=configuracion.nDimensiones
        individuoGlobal.nDimensiones=nDimensiones
        actual=Individuo()
        actual.nDimensiones=nDimensiones
        bestP=[nDimensiones]
        best=0
        #Inicializo la partícula
        for i in range(0,nDimensiones):
            nAux = numpy.random.random()
            nAux = (configuracion.rangosMax[i] - configuracion.rangosMin[i]) * nAux + (configuracion.rangosMin[i])
            nAux = numpy.float32(nAux)
            actual.valores.append(nAux)
            nAux = numpy.random.random()
            nAux = (configuracion.rangosMaxV[i] - configuracion.rangosMinV[i]) * nAux + (configuracion.rangosMinV[i])
            nAux = numpy.float32(nAux)
            actual.velocidades.append(nAux)
            individuoGlobal.rangosMax.append(configuracion.rangosMax[i])
            individuoGlobal.rangosMin.append(configuracion.rangosMin[i])
            individuoGlobal.rangosMaxV.append(configuracion.rangosMaxV[i])
            individuoGlobal.rangosMinV.append(configuracion.rangosMinV[i])
            #Variable Actual
            actual.rangosMax.append(configuracion.rangosMax[i])
            actual.rangosMin.append(configuracion.rangosMin[i])
            actual.rangosMaxV.append(configuracion.rangosMaxV[i])
            actual.rangosMinV.append(configuracion.rangosMinV[i])
        best=calculaFitness(problema,actual)
        xi=best
        individuoGlobal.aptitud=best
        bestP=actual.valores[:]
        individuoGlobal.valores=actual.valores[:]
        #Debo sincronizar para que todos los hilos vean el mismo valor

        #Si recibo un individuo mejor
        if mejorIndividuo is not None:
            if esMejor(criterio,mejorIndividuo.aptitud,individuoGlobal.aptitud):
                individuoGlobal=mejorIndividuo
            if esMejor(criterio,copiaIndividuo.aptitud,individuoGlobal.aptitud):
                individuoGlobal=copiaIndividuo

        #Ejecuto el algoritmo el número de iteraciones de intercambio
        for i in range(0,configuracion.nIteracionesIntercambio):
             #Actualizo la mejor posición de la partícula
            if i is not 0:
                xi=calculaFitness(problema,actual)
                if esMejor(criterio,xi,best):
                    best=xi
                    bestP=actual.valores[:]
                #Actualizo la mejor posición global
                if esMejor(criterio,best,individuoGlobal.aptitud):
                    individuoGlobal.aptitud=best
                    individuoGlobal.valores=bestP[:]
                    #Debo sincronizar aqui ya que se graba a la memoria global

            #Actualizo la velocidad y la posición de la partícula
            for w in range(0,nDimensiones):
                actual.velocidades[w]=actual.velocidades[w]+C1*numpy.random.random()*(bestP[w]-actual.valores[w])+C2*numpy.random.random()*(individuoGlobal.valores[w]-actual.valores[w])
                #Compruebo que los nuevos valores no se sangan del rango
                if actual.velocidades[w]>actual.rangosMaxV[w]:
                    actual.velocidades[w]=actual.rangosMaxV[w]
                if actual.velocidades[w]<actual.rangosMinV[w]:
                    actual.velocidades[w]=actual.rangosMinV[w]
                actual.valores[w]=actual.valores[w]+actual.velocidades[w]
                if actual.valores[w]>actual.rangosMax[w]:
                    actual.valores[w]=actual.rangosMax[w]
                if actual.valores[w]<actual.rangosMin[w]:
                    actual.valores[w]=actual.rangosMin[w]


        return individuoGlobal


    def PSO(self,configuracion,confproblema):
        #MPI
        size = MPI.COMM_WORLD.Get_size()
        proceso = MPI.COMM_WORLD.Get_rank()
        name = MPI.Get_processor_name()
        comm=MPI.COMM_WORLD
        mejorIndividuo=None
        soluciones=[]
        if proceso==0:
            print ("\t\t\tMPHStudio V1.0.0\n\n")
            print ("Modelos de Metaheurísticas Multipoblacionales implementadas en paralelo")
            print ("Algoritmo PSO")
            inicio = time.time()
            #Mando el arranque a todos los procesos
            comm.bcast(None, root=0)
            #Espero todos los individuos
            for x in range(0,size-1):
                indRecb=comm.recv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
                soluciones.append(indRecb)
                if x is not 0:
                    if esMejor(confproblema.criterio,indRecb.individuo.aptitud,mejorIndividuo.aptitud):
                        mejorIndividuo=indRecb.individuo
                else:
                    mejorIndividuo=indRecb.individuo
            fin = time.time()

            print ("Los valores más optimos son: ")
            for x in mejorIndividuo.valores:
                print(x)
            print ("El fitness es: "+mejorIndividuo.aptitud)
            print ("El tiempo de ejecución es: "+str(fin-inicio))
            #Gráfica de Convergencia
            graficaConvergencia(soluciones)


        else:
            #Espero a que el proceso 0 de el arranque
            comm.bcast(None, root=0)
            solucion=Solucion()
            copiaIndividuo=None
            #Controlo la topología entre las poblaciones y el método de paro
            if configuracion.metodoParo==Constantes.METODO_PARO_ITERACIONES:
                for i in range(0,int(math.ceil(configuracion.nParo/configuracion.configuracionPoblaciones[0].nIteracionesIntercambio))):
                    mejorIndividuo=self.ejecutaPSOIsla(confproblema.problema,configuracion,proceso,confproblema.criterio,mejorIndividuo,copiaIndividuo)
                    #Controlo la topología de intercambio
                    if configuracion.topologia==Constantes.TOPOLOGIA_ANILLO:
                        if configuracion.nIslas>1:
                            #Envio mi individuo a la poblacion a mi derecha
                            if proceso==configuracion.nIslas:#La última isla clona el individuo mas apto a la primera islas
                                comm.send(mejorIndividuo,dest=1,tag=proceso)
                                #Recibo el individuo
                                copiaIndividuo=comm.recv(source=proceso-1,tag=MPI.ANY_TAG)
                            elif proceso==1:
                                comm.send(mejorIndividuo,dest=proceso+1,tag=proceso)
                                copiaIndividuo=comm.recv(source=configuracion.nIslas,tag=MPI.ANY_TAG)
                            else:
                                comm.send(mejorIndividuo,dest=proceso+1,tag=proceso)
                                copiaIndividuo=comm.recv(source=proceso-1,tag=MPI.ANY_TAG)
                        else:
                            copiaIndividuo=mejorIndividuo


                    elif configuracion.topologia==Constantes.TOPOLOGIA_ESTRELLA:
                        pass
                    else:
                        pass


            elif configuracion.metodoParo==Constantes.CONVERGE:
                pass
            else:
                pass


           # print "El fitness del proceso ",proceso,"es: ",mejorIndividuo.aptitud
            #for x in mejorIndividuo.valores:
               # print"Valor del proceso ",proceso,"es: ",x

            #Envio el mejor individuo del proceso
            solucion.individuo=mejorIndividuo
            solucion.idIsla=proceso
            comm.send(solucion,dest=0,tag=proceso)

