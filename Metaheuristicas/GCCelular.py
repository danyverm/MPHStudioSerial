#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = 'daniel'
from GC import GC

import Constantes
import math
from Problemas.Problemas import calculaFitness
from Problemas.Problemas import esMejor
from Util import guardarDatosTXT
from Util import guardarResultados
from Util import guardarResultadosTracking
from Util import graficaConvergencia
from Util import graficaConvergenciaPromedio
from Util import solucionGeneral
from Util import iniciaConfiguracionIslas
from Util import guardarPoblacion
from Util import cargarPoblacion
from Util import crearArchivoTracking

from Util import crearArchivoRegistro
from Util import cerrarArchivoRegistro
from Util import registrarOperacionArchivo
from Util import iniciaConfiguracionCelular

from Objetos import Poblacion

from Objetos.Solucion import Solucion
import numpy
import random
import time
from multiprocessing import Process,Semaphore,current_process,Queue

class GCCelular(GC):
    def __init__(self):
        GC.__init__(self)
        self.radio=1
        self.forma=Constantes.CELULAR_FORMA_CRUZ
        self.vecinos=[]
        self.iteracionesTotales = 0

    def getCoordenadas(self,proceso,configuracion):

        fila=int(math.ceil(proceso/float(configuracion.columnas)))-1
        columna=proceso-fila*configuracion.columnas-1
        return (fila,columna)

    def getVecino(self,coordenada):
        fil,col=coordenada
        return self.vecinos[fil][col]

    def getVecinos(self,coordenadas):
        vecinos=[]
        for coordenada in coordenadas:
            vecinos.append(self.getVecino(coordenada))
        return vecinos


    def getListaVecinos(self,proceso,configuracion):
        vecinos=[]
        contador=1
        actual=self.getCoordenadas(proceso,configuracion)

        fila,columna=actual

        if self.forma==Constantes.CELULAR_FORMA_CRUZ:
            vecinos.append(actual)
            for i in range(self.radio):
                #print i
                #Arriba
                auxColumna=columna
                auxFila=(fila-contador)%configuracion.filas
                vecinos.append((auxFila,auxColumna))

                #Abajo
                auxFila=(fila+contador)%configuracion.filas
                vecinos.append((auxFila,auxColumna))

                #Izquierda
                auxFila=fila
                auxColumna=(columna-contador)%configuracion.columnas
                vecinos.append((auxFila,auxColumna))

                #Derecha
                auxColumna=(columna+contador)%configuracion.columnas
                vecinos.append((auxFila,auxColumna))

                contador+=1



        elif self.forma==Constantes.CELULAR_FORMA_CUADRADO:
            auxFila=(fila-self.radio)%configuracion.filas
            auxColumna=(columna-self.radio)%configuracion.columnas
            for i in range(self.radio*2+1):
                for j in range(self.radio*2+1):
                    vecinos.append(((auxFila+i)%configuracion.filas,(auxColumna+j)%configuracion.columnas))

        elif self.forma==Constantes.CELULAR_FORMA_ROMBO:
            contador2=0
            auxFila=fila
            auxColumna=columna
            for i in range(1,self.radio+1):
                contador2+=1
                #Arriba
                auxFila=(fila-i)%configuracion.filas
                vecinos.append((auxFila,columna))
                for j in range(1,self.radio-contador2+1):
                    #Izquierda
                    auxColumna=(columna-j)%configuracion.columnas
                    vecinos.append((auxFila,auxColumna))

                    #Derecha
                    auxColumna=(columna+j)%configuracion.columnas
                    vecinos.append((auxFila,auxColumna))
                #Abajo
                auxFila=(fila+i)%configuracion.filas
                vecinos.append((auxFila,columna))

                for j in range(1,self.radio-contador2+1):


                    #Izquierda
                    auxColumna=(columna-j)%configuracion.columnas
                    vecinos.append((auxFila,auxColumna))

                    #Derecha
                    auxColumna=(columna+j)%configuracion.columnas
                    vecinos.append((auxFila,auxColumna))

            auxFila=fila
            auxColumna=(columna-self.radio)%configuracion.columnas
            for j in range(1+self.radio*2):
                vecinos.append((auxFila,(auxColumna+j)%configuracion.columnas))

        else:
            pass

        return vecinos

    def sumaAptitud(self,listaVecinos):
        sumatoria = 0
        for i in range(len(listaVecinos)):
            sumatoria += self.getVecino(listaVecinos[i]).aptitud
        return sumatoria

    def giraRuleta(self, objetivo, sumatoria,padre1,listavecinos):
        suma = 0.0
        seleccionado = -1
        copiaInd=self.getVecinos(listavecinos)
        if padre1!=None:
            copiaInd.remove(padre1)

        while suma <= objetivo:
            seleccionado = seleccionado + 1
            suma += copiaInd[seleccionado].aptitud / float(sumatoria)

        return copiaInd[seleccionado]

    def seleccionRuleta(self,padre1,listavecinos):
        #Calculo el fitness de cada individuo
        if padre1 is None:
            sumatoria = self.sumatoria
        else:
            sumatoria = self.sumatoria-padre1.aptitud
        objetivo = numpy.random.random()
        #Selección, cruza y mutación
        return self.giraRuleta(objetivo, sumatoria,padre1,listavecinos)

    def seleccionTorneo(self,confproblema,listavecinos):
        individuos=self.getVecinos(listavecinos)
        totalInd=len(listavecinos)
        #Calculo el fitness de cada individuo
        sumatoria = self.sumatoria
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
            indRes1=individuo1 if esMejor(confproblema.criterio,individuos[individuo1].aptitud,individuos[individuo2].aptitud) else individuo2
        else:
            indRes1=individuo2 if esMejor(confproblema.criterio,individuos[individuo1].aptitud,individuos[individuo2].aptitud) else individuo1

        if objetivo>self.porcentajeSeleccion: #Selecciono el más apto
            indRes2=individuo3 if esMejor(confproblema.criterio,individuos[individuo3].aptitud,individuos[individuo4].aptitud) else individuo4
        else:
            indRes2=individuo4 if esMejor(confproblema.criterio,individuos[individuo1].aptitud,individuos[individuo2].aptitud) else individuo3

        return individuos[indRes1],individuos[indRes2]


    def ejecutaGC(self,proceso,nIndividuo,configuracion,confproblema,listavecinos):

        #print nIndividuo
        mejorIndividuo=self.getVecino(self.getCoordenadas(nIndividuo,configuracion))
        solucion=Solucion(nIndividuo)
        solucion.individuo=[]
        registros=[]

        for i in range(0,configuracion.nGeneracionesIntercambio):
            #self.iteracionesTotales+=1
            self.sumatoria = self.sumaAptitud(listavecinos)
            mutados=[]
            padre1=None
            #mutados+=self.getVecinos(listavecinos)
            for nPareja in range(configuracion.nParejasGeneracion):
                #Selección
                if self.metodoSeleccion==Constantes.GC_SELECCION_RULETA:
                    padre1=self.getVecino(self.getCoordenadas(nIndividuo,configuracion))
                    padre2 = self.seleccionRuleta(padre1,listavecinos)
                else:
                    (padre1,padre2) = self.seleccionTorneo(confproblema,listavecinos)
                    padre1=self.getVecino(self.getCoordenadas(nIndividuo,configuracion))

                #Registro la operacion
                if configuracion.guardarTracking==True:
                    #registrarOperacionArchivo(self.aS[proceso-1],1,Constantes.OPERACION_SELECCION,self.iteracionesTotales,(padre1,padre2))
                    registros.append((0,1,Constantes.OPERACION_SELECCION,self.iteracionesTotales,(padre1,padre2)))

                #Cruza
                (hijo1,hijo2)=self.fCruza(padre1,padre2)
                if configuracion.guardarTracking==True:
                    #registrarOperacionArchivo(self.aC[proceso-1],1,Constantes.OPERACION_CRUZA,self.iteracionesTotales,(hijo1,hijo2))
                    registros.append((1,1,Constantes.OPERACION_CRUZA,self.iteracionesTotales,(hijo1,hijo2)))
                #Mutación
                hijo1=self.fMutacion(hijo1,confproblema)
                if configuracion.guardarTracking==True:
                    #registrarOperacionArchivo(self.aM[proceso-1],1,Constantes.OPERACION_MUTACION,self.iteracionesTotales,hijo1)
                    registros.append((2,1,Constantes.OPERACION_MUTACION,self.iteracionesTotales,hijo1))
                hijo2=self.fMutacion(hijo2,confproblema)
                if configuracion.guardarTracking==True:
                    #registrarOperacionArchivo(self.aM[proceso-1],1,Constantes.OPERACION_MUTACION,self.iteracionesTotales,hijo2)
                    registros.append((2,1,Constantes.OPERACION_MUTACION,self.iteracionesTotales,hijo2))
                mutados.append(hijo1)
                mutados.append(hijo2)

            #Compruebo quien es el mejor
            for hijo in mutados:
                if esMejor(confproblema.criterio,hijo.aptitud,mejorIndividuo.aptitud):
                    mejorIndividuo=hijo

            solucion.generacion=self.iteracionesTotales
            solucion.individuo.append(mejorIndividuo)
            solucion.aptitudes.append(mejorIndividuo.aptitud)

            return proceso,solucion,registros


    def GCCelular(self,configuracion,confproblema):
        if not iniciaConfiguracionCelular(configuracion):
            return
        if configuracion.debug:
            print ("\t\t\tMPHStudio V1.0.0\n\n")
            print ("Modelos de Metaheurísticas Multipoblacionales implementadas en paralelo")
            print ("Algoritmo GC - Celular")
        inicio = time.time()
        historial=[]
        semaforo=Semaphore(5)
        cola = Queue()
        termina=False
        mejorIndividuo=None
        auxmejorIndividuo=None
        iteracionesSinMejorar=0

        aptitudes=[]

        self.aGP=[None]*configuracion.nVecinos
        self.aS=[None]*configuracion.nVecinos
        self.aC=[None]*configuracion.nVecinos
        self.aM=[None]*configuracion.nVecinos
        self.aR=[None]*configuracion.nVecinos
        self.aMI=[None]*configuracion.nVecinos
        self.aO=[None]*configuracion.nVecinos


        if configuracion.generaPoblacion==True:
            self.poblacion=self.fGenerarPoblacion(configuracion,confproblema,configuracion.nVecinos)
            if configuracion.guardaPoblacion:
                #Guardo los datos de la población
                guardarPoblacion(self.poblacion.individuos,configuracion.archivoPoblacion)
        else:
            self.poblacion.individuos=cargarPoblacion(configuracion.archivoPoblacion)

        contador=0
        #Convierte los individuos a vecinos
        for i in range(configuracion.filas):
            auxVecinos=[]
            for j in range(configuracion.columnas):
                auxVecinos.append(self.poblacion.individuos[contador])
                auxAptitud=[]
                auxAptitud.append(self.poblacion.individuos[contador].aptitud)
                aptitudes.append(auxAptitud)
                contador+=1
            self.vecinos.append(auxVecinos)
        if configuracion.debug:
            print aptitudes
            print "Población inicial"
            for i in range(configuracion.filas):
                lista=[]
                for j in range(configuracion.columnas):
                    lista.append(self.vecinos[i][j].aptitud)
                print lista

         #Creo la BD para guardar los registro de la ejecución del programa

        if configuracion.guardarTracking==True:
            for proceso in range(1,configuracion.nVecinos+1):
                self.aGP[proceso-1],self.aS[proceso-1],self.aC[proceso-1],self.aM[proceso-1],self.aR[proceso-1],self.aMI[proceso-1],self.aO[proceso-1]=crearArchivoRegistro(proceso)
                auxvecinos=self.getVecinos(self.getListaVecinos(proceso,configuracion))
                registrarOperacionArchivo(self.aGP[proceso-1],proceso,Constantes.OPERACION_GENERARPOBLACION,0,auxvecinos)

        while termina is not True:
            self.iteracionesTotales+=1
            procesos=[]
            if configuracion.metodoParo==Constantes.METODO_PARO_ITERACIONES:
                pass
            elif configuracion.metodoParo==Constantes.METODO_PARO_CONVERGENCIA:
                #Creo los procesos
                vecinoActual=1
                banderaSale=False

                while(True):
                    procesos=[]

                    if vecinoActual>configuracion.nVecinos:
                        break

                    for proceso in range(1,configuracion.totalProcesos+1):
                        if vecinoActual>configuracion.nVecinos:
                            banderaSale=True
                            break
                        vecinos=self.getListaVecinos(vecinoActual,configuracion)
                        #procesos.append(Process(target=, args=(proceso,vecinoActual,configuracion,confproblema,vecinos,cola,semaforo)))


                        proceso,solucion,registros=self.ejecutaGC(proceso,vecinoActual,configuracion,confproblema,vecinos)

                        vecinoActual+=1

                        nIndividuo=solucion.idIsla
                        aptitudes[solucion.idIsla-1]=aptitudes[solucion.idIsla-1]+solucion.aptitudes
                        fil,col=self.getCoordenadas(nIndividuo,configuracion)

                        #Guardo mis registros
                        if configuracion.guardarTracking==True:
                            for registro in registros:
                                if registro[0]==0:
                                    registrarOperacionArchivo(self.aS[nIndividuo-1],registro[1],registro[2],registro[3],registro[4])
                                elif registro[0]==1:
                                    registrarOperacionArchivo(self.aC[nIndividuo-1],registro[1],registro[2],registro[3],registro[4])
                                elif registro[0]==2:
                                    registrarOperacionArchivo(self.aM[nIndividuo-1],registro[1],registro[2],registro[3],registro[4])


                        if esMejor(confproblema.criterio,solucion.individuo[0].aptitud,self.vecinos[fil][col].aptitud):
                            self.vecinos[fil][col]=solucion.individuo[0]
                        #Compruebo si ya cumpli el número máximo de evoluciones sin cambio
                        if mejorIndividuo is None:
                            mejorIndividuo=self.vecinos[fil][col]
                            auxmejorIndividuo=self.vecinos[fil][col]
                        else:
                            if esMejor(confproblema.criterio,self.vecinos[fil][col].aptitud,mejorIndividuo.aptitud):
                                mejorIndividuo=self.vecinos[fil][col]
                                if configuracion.debug:
                                    print("Mejor individuo: "+str(mejorIndividuo.aptitud)+" Vecino: "+str(nIndividuo))

                        if configuracion.debug:
                            print("Proceso: "+str(proceso)+" Vecino: "+str(nIndividuo) +" Generación: "+str(self.iteracionesTotales*configuracion.nGeneracionesIntercambio)+" Aptitud: "+str(self.vecinos[fil][col].aptitud))
                            print self.vecinos[fil][col].valores

                    for proceso in procesos:
                        proceso.join()
                        proceso.terminate()





                if esMejor(confproblema.criterio,mejorIndividuo.aptitud,auxmejorIndividuo.aptitud):
                    auxmejorIndividuo=mejorIndividuo
                    iteracionesSinMejorar=0
                else:
                    iteracionesSinMejorar+=1

                #Envio mis individuos más optimos
                if self.iteracionesTotales>=configuracion.nGeneracionesMaximasParo:
                    termina=True

                if iteracionesSinMejorar>=configuracion.nGeneracionesNCParo:
                    termina=True

            else:
                pass

        if configuracion.debug:
            print "Población final"
        contador=0
        for i in range(configuracion.filas):
            lista=[]
            for j in range(configuracion.columnas):
                lista.append(self.vecinos[i][j].aptitud)
                solucion=Solucion(contador+1)
                solucion.aptitudes=aptitudes[contador]
                solucion.individuo.append(self.vecinos[i][j])
                historial.append(solucion)
                contador+=1
            if configuracion.debug:
                print lista

        fin = time.time()
        if configuracion.debug:
            print ("Los valores más optimos son: ")
            print (mejorIndividuo.valores)
            print ("El fitness es: "+str(mejorIndividuo.aptitud))
            print ("El total de generaciones: "+str(self.iteracionesTotales))
            print ("El tiempo de ejecución es: "+str(fin-inicio))

        for proceso in range(1,configuracion.nVecinos+1):
            if configuracion.guardarTracking==True:
                    cerrarArchivoRegistro((self.aGP[proceso-1],self.aS[proceso-1],self.aC[proceso-1],self.aM[proceso-1],self.aR[proceso-1],self.aMI[proceso-1],self.aO[proceso-1]))

        if configuracion.guardarDatosTXT is True:
            guardarDatosTXT(configuracion.archivoDatos,mejorIndividuo,str(fin-inicio),historial)

        datosH=None
        if configuracion.guardarResultados is True:
            datosH=[self.porcentajeSeleccion,self.porcentajeMutacion,self.forma,self.radio]
            guardarResultados(configuracion,confproblema,0,datosH,mejorIndividuo,str(fin-inicio),historial)


        #Creo un archivo que contenga el tracking de todos los procesos
        if configuracion.guardarTracking==True:
            print ("Creando archivo de tracking!!!")
            datosH=[self.porcentajeSeleccion,self.porcentajeMutacion,self.forma,self.radio]
            guardarResultadosTracking(configuracion,confproblema,0,datosH,mejorIndividuo,str(fin-inicio),historial)
            #Comprimo los archivos
            crearArchivoTracking(configuracion.archivoTracking,configuracion.nVecinos+1)
            print ("Archivo Creado!!!")

        #Gráfica de Convergencia
        if configuracion.grafica:
            if configuracion.tipoGrafica==Constantes.GRAFICA_POBLACIONES:
                graficaConvergencia(historial)
            else:
                graficaConvergenciaPromedio(solucionGeneral(historial,len(historial[0].aptitudes),confproblema.criterio))

        return mejorIndividuo