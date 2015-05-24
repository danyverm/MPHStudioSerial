#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = 'daniel'
from Objetos.Individuo import Individuo
from Objetos.Islas import Islas
from Objetos.Poblacion import Poblacion
import Constantes
from Problemas.Problemas import calculaFitness
from Problemas.Problemas import esMejor
from Util import guardarDatosTXT
from Util import guardarResultados
from Util import guardarResultadosTracking
from Util import graficaConvergencia
from Util import iniciaConfiguracionIslas
from Util import iniciaConfiguracionCelular
from Util import guardarPoblacion
from Util import cargarPoblacion
from Util import crearArchivoTracking

from Util import crearArchivoRegistro
from Util import cerrarArchivoRegistro
from Util import registrarOperacionArchivo

from Objetos.Solucion import Solucion
import numpy
import random
from mpi4py import MPI
import time
from multiprocessing import *

class GC:
    def __init__(self):
        self.metodoSeleccion = 0
        self.precision = 0.0
        self.nPuntosCruza = 1
        self.poblacion=[]
        self.porcentajeSeleccion = .10
        self.porcentajeMutacion = .10
        self.puntoCorte = 2

        self.sumatoria = []

        # Nombre de las funciones
        self.fGenerarPoblacion = self.generaPoblacion

        self.fCruza_Muta = self.cruza_mutacion
        self.fCruza = self.cruza
        self.fMutacion = self.mutacion
        self.fReemplazo = self.reemplazar

        # Parámetros de escape
        self.escape = False
        self.nIteracionesEscape = 100
        self.nIndividuosEscape = 1

        self.aGP = None
        self.aS = None
        self.aC = None
        self.aM = None
        self.aR = None
        self.aMI = None
        self.aO = None

        self.iteracionesTotales = []

        numpy.random.seed()


    #Método que genera una población de nIndividuos al azar
    def generaPoblacion(self, configuracion,confproblema,total):
        pobla=Poblacion()
        for i in range(0,total):
            aux = Individuo(i)
            aux.nDimensiones=configuracion.nDimensiones
            aux.rangosMin=configuracion.rangosMin
            aux.rangosMax=configuracion.rangosMax
            aux.calculaLongitud(self.precision)

            for j in range(0,configuracion.nDimensiones):
                nAux = numpy.random.random()
                nAux = (configuracion.rangosMax[j] - configuracion.rangosMin[j]) * nAux + (configuracion.rangosMin[j])
                nAux = numpy.float32(nAux)
                aux.valores.append(nAux)
            aux.aptitud=calculaFitness(confproblema.problema,aux)

            pobla.individuos.append(aux)
        return pobla

    def ejecutaEscape(self,configuracion,confproblema):
        total=len(self.poblacion.individuos)
        masApto=[self.poblacion.individuos[0]]
        respaldo=[]
        if (total-self.nIndividuosEscape)>1:
            respaldo=self.poblacion.individuos[1:total-self.nIndividuosEscape]

        nuevos=self.fGenerarPoblacion(configuracion,confproblema,self.nIndividuosEscape)

        self.poblacion.individuos=masApto+respaldo+nuevos


    def giraRuleta(self, objetivo, sumatoria,padre1,proceso):
        suma = 0.0
        seleccionado = -1
        copiaInd=self.poblacion[proceso-1].individuos[:]
        del(copiaInd[padre1])

        while suma <= objetivo:
            seleccionado = seleccionado + 1
            suma += copiaInd[seleccionado].aptitud / float(sumatoria)

        return copiaInd[seleccionado]

    def seleccionRuleta(self,padre1,proceso):
        #Calculo el fitness de cada individuo
        sumatoria = self.sumatoria[proceso-1]-self.poblacion[proceso-1].individuos[padre1].aptitud
        objetivo = numpy.random.random()
        #Selección, cruza y mutación
        return self.giraRuleta(objetivo, sumatoria,padre1,proceso)

    def seleccionTorneo(self,confproblema,proceso):
        totalInd=len(self.poblacion[proceso-1].individuos)
        #Calculo el fitness de cada individuo
        sumatoria = self.sumatoria[proceso-1]
        individuo1=random.randrange(totalInd)
        individuo2=individuo1
        while individuo2 == individuo1:
            individuo2=random.randrange(totalInd)
        indRes1=0
        individuo3=individuo2
        while individuo3== individuo2 or individuo3==individuo1:
            individuo3=random.randrange(totalInd)

        individuo4=individuo1
        while individuo4==individuo1 or individuo4==individuo2 or individuo4==individuo3:
            individuo4=random.randrange(totalInd)
        indRes2=0
        objetivo = numpy.random.random()

        if objetivo>self.porcentajeSeleccion: #Selecciono el más apto
            indRes1=individuo1 if esMejor(confproblema.criterio,self.poblacion[proceso-1].individuos[individuo1].aptitud,self.poblacion[proceso-1].individuos[individuo2].aptitud) else individuo2
        else:
            indRes1=individuo2 if esMejor(confproblema.criterio,self.poblacion[proceso-1].individuos[individuo1].aptitud,self.poblacion[proceso-1].individuos[individuo2].aptitud) else individuo1

        if objetivo>self.porcentajeSeleccion: #Selecciono el más apto
            indRes2=individuo3 if esMejor(confproblema.criterio,self.poblacion[proceso-1].individuos[individuo3].aptitud,self.poblacion[proceso-1].individuos[individuo4].aptitud) else individuo4
        else:
            indRes2=individuo4 if esMejor(confproblema.criterio,self.poblacion[proceso-1].individuos[individuo1].aptitud,self.poblacion[proceso-1].individuos[individuo2].aptitud) else individuo3

        return self.poblacion[proceso-1].individuos[indRes1],self.poblacion[proceso-1].individuos[indRes2]

    def cruza(self,padre1,padre2):
        #Copio los valores
        hijo1 = Individuo(-1)
        hijo2 = Individuo(-1)

        hijo1.longitud = padre1.longitud
        hijo2.longitud = padre1.longitud
        hijo1.rangosMin = padre1.rangosMin[:]
        hijo1.rangosMax = padre1.rangosMax[:]
        hijo2.rangosMin = padre1.rangosMin[:]
        hijo2.rangosMax = padre1.rangosMax[:]


        hijo1.valores = padre1.valores[:]
        hijo2.valores = padre1.valores[:]

        for (g1, g2, longitud) in zip(padre1.calculaGenotipo(), padre2.calculaGenotipo(),padre1.longitud):
            #Cruza
            tam = int(longitud / self.puntoCorte)

            #Hijo1 - Cruza
            auxHijo = g1[0:tam] + g2[tam:]
            hijo1.genotipo.append(auxHijo)
            #Hijo2 - Cruza
            auxHijo = g2[0:tam] + g1[tam:]
            hijo2.genotipo.append(auxHijo)


        return hijo1,hijo2

    def mutacion(self,hijo,confProblema):
        contador = 0
        for g1 in hijo.genotipo:
            auxHijo = g1
            #Hijo1 - Muta
            resultado=""
            for i in auxHijo:
                aleatorio=numpy.random.random()
                cambiado= "0" if i == "1" else "1"
                resultado+=i if aleatorio<=self.porcentajeMutacion else cambiado
            hijo.genotipo[contador]=resultado
            contador+=1


        hijo.calculaFenotipo()
        hijo.aptitud=calculaFitness(confProblema.problema,hijo)
        return hijo



    def cruza_mutacion(self, padre1, padre2, confProblema):
        #Copio los valores
        hijo1 = Individuo(-1)
        hijo2 = Individuo(-1)

        hijo1.longitud = padre1.longitud
        hijo2.longitud = padre1.longitud
        hijo1.rangosMin = padre1.rangosMin[:]
        hijo1.rangosMax = padre1.rangosMax[:]
        hijo2.rangosMin = padre1.rangosMin[:]
        hijo2.rangosMax = padre1.rangosMax[:]


        hijo1.valores = padre1.valores[:]
        hijo2.valores = padre1.valores[:]

        for (g1, g2, longitud) in zip(padre1.calculaGenotipo(), padre2.calculaGenotipo(),padre1.longitud):
            #Cruza
            tam = int(longitud / self.puntoCorte)
            #Mutación
            auxGenotipo = ""
            #Hijo1 - Cruza
            auxHijo = g1[0:tam] + g2[tam:]
            #Hijo1 - Muta
            resultado=""
            for i in auxHijo:
                aleatorio=numpy.random.random()
                cambiado= "0" if i == "1" else "1"
                resultado+=i if aleatorio<=self.porcentajeMutacion else cambiado
            hijo1.genotipo.append(resultado)
            #Hijo2 - Cruza
            auxHijo = g2[0:tam] + g1[tam:]
            #Hijo2 - Muta
            resultado=""
            for i in auxHijo:
                aleatorio=numpy.random.random()
                cambiado= "0" if i == "1" else "1"
                resultado+=i if aleatorio<=self.porcentajeMutacion else cambiado
            hijo2.genotipo.append(resultado)

        hijo1.calculaFenotipo()
        hijo1.aptitud=calculaFitness(confProblema.problema,hijo1)
        hijo2.calculaFenotipo()
        hijo2.aptitud=calculaFitness(confProblema.problema,hijo2)

        return hijo1,hijo2

    def reemplazar(self, nuevos,criterio,configuracion,proceso):
        self.poblacion[proceso-1].individuos = self.poblacion[proceso-1].individuos + nuevos
        #Ordenar los mejores
        if criterio==Constantes.MAXIMO:
            self.poblacion[proceso-1].individuos = sorted(self.poblacion[proceso-1].individuos, key=lambda individuo: individuo.aptitud, reverse=True)
        else:
            self.poblacion[proceso-1].individuos = sorted(self.poblacion[proceso-1].individuos, key=lambda individuo: individuo.aptitud, reverse=False)
        del(self.poblacion[proceso-1].individuos[configuracion.nIndividuos:])

    def ejecutaGCIsla(self,confproblema,configuracion,proceso,copiaIndividuo):
        #Si recibo un individuo mejor
        aptitudes=[]
        solucion=Solucion(proceso)
        solucion.individuo=[None]*(configuracion.nIndividuosIntercambio)

        if copiaIndividuo is not None:
            for x in range(0,len(copiaIndividuo)):
                self.poblacion[proceso-1].individuos.append(copiaIndividuo[x])


        for i in range(0,configuracion.nGeneracionesIntercambio):
            self.iteracionesTotales[proceso-1]+=1
            self.sumatoria[proceso-1] = self.poblacion[proceso-1].sumaAptitud()
            mutados=[]
            for j in range(len(self.poblacion[proceso-1].individuos)):
                #Selección
                if self.metodoSeleccion==Constantes.GC_SELECCION_RULETA:
                    padre1=self.poblacion[proceso-1].individuos[j]
                    padre2 = self.seleccionRuleta(j,proceso)
                else:
                    (padre1,padre2) = self.seleccionTorneo(confproblema,proceso)
                #Registro la operacion
                if configuracion.guardarTracking==True:
                    registrarOperacionArchivo(self.aS,proceso,Constantes.OPERACION_SELECCION,self.iteracionesTotales[proceso-1],(padre1,padre2))

                #Cruza
                (hijo1,hijo2)=self.fCruza(padre1,padre2)
                if configuracion.guardarTracking==True:
                    registrarOperacionArchivo(self.aC,proceso,Constantes.OPERACION_CRUZA,self.iteracionesTotales,(hijo1,hijo2))
                #Mutación
                hijo1=self.fMutacion(hijo1,confproblema)
                if configuracion.guardarTracking==True:
                    registrarOperacionArchivo(self.aM,proceso,Constantes.OPERACION_MUTACION,self.iteracionesTotales,hijo1)
                hijo2=self.fMutacion(hijo2,confproblema)
                if configuracion.guardarTracking==True:
                    registrarOperacionArchivo(self.aM,proceso,Constantes.OPERACION_MUTACION,self.iteracionesTotales,hijo2)
                #Cruza_Mutación
                #(hijo1,hijo2) = self.fCruza_Muta(padre1,padre2,confproblema)
                mutados.append(hijo1)
                mutados.append(hijo2)

            #Reemplazo
            self.reemplazar(mutados,confproblema.criterio,configuracion,proceso)
            aptitudes.append(self.poblacion[proceso-1].individuos[0].aptitud)


        #Regreso el mejor individuo
        for x in range(0,configuracion.nIndividuosIntercambio):
            solucion.individuo[x]=self.poblacion[proceso-1].individuos[x]
        solucion.aptitudes=aptitudes
        return solucion



    def GCIslas(self,configuracion,confproblema):
        #MPI
        size = configuracion.nIslas+1

        for proceso in range(1,size):
            if not iniciaConfiguracionIslas(configuracion,confproblema,proceso,size):
                return


        inicio = time.time()
        print ("\t\t\tMPHStudio V1.0.0\n\n")
        print ("Modelos de Metaheurísticas Multipoblacionales implementadas en paralelo")
        print ("Algoritmo GC - Islas Serial")
        pIndividuos=self.fGenerarPoblacion(configuracion.configuracionPoblaciones[0],confproblema,configuracion.nIndividuosTotal)


        print "Mi población inicial"
        for i in pIndividuos.individuos:
            print ("Poblacion : "+str(i.valores))

        base=0
        for x in range(1,size):
            auxPoblacion=Poblacion()
            auxPoblacion.individuos=pIndividuos.individuos[base:configuracion.configuracionPoblaciones[x-1].nIndividuos+base]
            base+=configuracion.configuracionPoblaciones[x-1].nIndividuos
            self.poblacion.append(auxPoblacion)
            self.sumatoria.append(0)
            self.iteracionesTotales.append(0)


        salir=False
        historial=[]

        solucion=[]
        solucionCopia=[]
        aptitudes=[]
        mejorIndividuo=[]
        noSinRecibir=[]
        iteracionesSinMejorar=[]
        iteracionesSinMejoraraEscape=[]
        termina=[]
        totalTerminados=0

        for proceso in range(1,size):
            auxSolucion=Solucion(proceso)
            auxSolucion.individuo=None
            solucion.append(auxSolucion)

            auxSolucion=Solucion(proceso)
            auxSolucion.individuo=None
            solucionCopia.append(auxSolucion)
            aptitudes.append([])
            mejorIndividuo.append(None)
            noSinRecibir.append(0)
            iteracionesSinMejorar.append(0)
            iteracionesSinMejoraraEscape.append(0)
            termina.append(False)
            aptitudes[proceso-1].append(self.poblacion[proceso-1].individuos[0].aptitud)


        while(salir==False):
            for proceso in range(1,size):
                if totalTerminados>=size-1:
                    salir=True
                    break

                if termina[proceso-1]!=True:



                    if configuracion.metodoParo==Constantes.METODO_PARO_CONVERGENCIA:

                        solucion[proceso-1]=self.ejecutaGCIsla(confproblema,configuracion.configuracionPoblaciones[proceso-1],proceso,solucionCopia[proceso-1].individuo if solucionCopia[proceso-1] else None)
                        if configuracion.debug:
                            print("Proceso: "+str(proceso) +" Generación: "+str(self.iteracionesTotales[proceso-1])+" Aptitud: "+str(solucion[proceso-1].individuo[0].aptitud)+" Para el paro:"+str(configuracion.nGeneracionesMaximasParo))
                            print solucion[proceso-1].individuo[0].valores

                        aptitudes[proceso-1]=aptitudes[proceso-1]+solucion[proceso-1].aptitudes
                        #Compruebo si ya cumpli el número máximo de evoluciones sin cambio
                        if mejorIndividuo[proceso-1] is None:
                            mejorIndividuo[proceso-1]=solucion[proceso-1].individuo[0]
                        else:
                            if esMejor(confproblema.criterio,solucion[proceso-1].individuo[0].aptitud,mejorIndividuo[proceso-1].aptitud):
                                mejorIndividuo[proceso-1]=solucion[proceso-1].individuo[0]
                                iteracionesSinMejorar[proceso-1]=0
                                iteracionesSinMejoraraEscape[proceso-1]=0
                            else:
                                iteracionesSinMejorar[proceso-1]=iteracionesSinMejorar[proceso-1]+1
                                iteracionesSinMejoraraEscape[proceso-1]=iteracionesSinMejoraraEscape[proceso-1]+1


                        #Envio mis individuos más optimos
                        if iteracionesSinMejorar[proceso-1]>=configuracion.nGeneracionesNCParo or self.iteracionesTotales[proceso-1]>=configuracion.nGeneracionesMaximasParo:
                            solucion[proceso-1].termina=True
                            termina[proceso-1]=True
                            totalTerminados+=1




                        for j in configuracion.configuracionPoblaciones[proceso-1].destinos:
                            for s in solucion[proceso-1].individuo:
                                if configuracion.guardarTracking==True:
                                    registrarOperacionArchivo(self.aMI,proceso,Constantes.OPERACION_MIGRACION,self.iteracionesTotales[proceso-1],(j,s))

                            #espera=comm.isend(solucion,dest=j,tag=proceso)
                            solucionCopia[j-1]=solucion[proceso-1]

                        #Comprubo Escape
                        if self.escape:
                            if iteracionesSinMejoraraEscape>=self.nIteracionesEscape:
                                self.ejecutaEscape(configuracion.configuracionPoblaciones[proceso-1],confproblema)
                                iteracionesSinMejoraraEscape=0
                                if configuracion.guardarTracking==True:
                                    registrarOperacionArchivo(self.aO,proceso,Constantes.OPERACION_OTRAS,0,"Ejecución de escape")


                        if termina[proceso-1]:
                            solucion[proceso-1].aptitudes=aptitudes[proceso-1]
                            historial.append(solucion[proceso-1])


        mejorIndividuo=None

        for x in range(0,size-1):
            solucionCopia=historial[x]
            if x is 0:
                mejorIndividuo=solucionCopia.individuo[0]
            else:
                if esMejor(confproblema.criterio,solucionCopia.individuo[0].aptitud,mejorIndividuo.aptitud):
                    mejorIndividuo=solucionCopia.individuo[0]

        fin = time.time()

        print ("Los valores más optimos son: ")
        print (mejorIndividuo.valores)
        print ("El fitness es: "+str(mejorIndividuo.aptitud))
        print ("El total de generaciones: "+str(len(historial[0].aptitudes) -1 ))
        print ("El tiempo de ejecución es: "+str(fin-inicio))

        datosH=None
        if configuracion.guardarResultados is True:
            datosH=[self.porcentajeSeleccion,self.porcentajeMutacion]
            guardarResultados(configuracion,confproblema,0,datosH,mejorIndividuo,str(fin-inicio),historial)



        #Gráfica de Convergencia
        if configuracion.grafica:
            graficaConvergencia(historial)








