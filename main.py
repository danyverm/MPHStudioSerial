#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'daniel'
import Constantes
from Objetos.Islas import ConfiguracionIslas
from Objetos.Poblacion import ConfiguracionPoblacion
from Objetos.Celulas import ConfiguracionCelular
from Metaheuristicas.GC import GC
from Problemas.Rosenbrock import *
from Problemas.TSP import *
from Problemas.Schwefel import *
from Problemas.Otra import *
from Problemas.Eggholder import *
from Problemas.Problemas import Problema
from Util import cargarDatos
import sys
from mpi4py import MPI


def main():

    nPoblaciones = 10
    #Configuración de las Islas
    configIslas=ConfiguracionIslas()
    configIslas.nIslas=nPoblaciones
    configIslas.topologia=Constantes.TOPOLOGIA_ANILLO
    configIslas.metodoParo=Constantes.METODO_PARO_CONVERGENCIA
    #Número máximo de generaciones sin cambio en la aptitud del mejor individuo
    configIslas.nGeneracionesNCParo=1000
    #Número máximo de generaciones por ejecución
    configIslas.nGeneracionesMaximasParo=20000

    #Utilidades
    configIslas.guardarDatosTXT=False
    configIslas.archivoDatos="resultado1.txt"
    configIslas.guardarResultados=True
    configIslas.archivoResultados="Resultados/resultado_SGA15_DEMO0.mpr"
    configIslas.debug=True
    configIslas.grafica=False
    configIslas.guardaPoblacion=False
    configIslas.generaPoblacion=True
    configIslas.archivoPoblacion="poblacion1.pbl"
    configIslas.guardarTracking=False
    configIslas.archivoTracking="Tracking/track.mpt"

    #Configuración Poblaciones
    confPoblacion=ConfiguracionPoblacion()
    confPoblacion.rangosMin=(-513,-513)
    confPoblacion.rangosMax=(512,512)
    confPoblacion.nIndividuos=100
    confPoblacion.nDimensiones=2
    confPoblacion.nIndividuosIntercambio=15
    confPoblacion.nIndividuosRecibidos=15
    confPoblacion.nGeneracionesIntercambio=100

    #Le pongo la misma configuración a todas las poblaciones
    configIslas.configuracionPoblaciones=[confPoblacion]*nPoblaciones

    #Configuración del TSP
    tsp=ConfiguracionTSP()#10 Ciudades
    tsp.cargarTSPLib("TSPData/dj38.tsp")
    #tsp.cargarTSPSolucion("st70.opt.tour")
    tsp.nVecesMuta=1
    tsp.nPosiciones=1
    tsp.porcentajeMutacion=0.7

    #Configuración del problema
    confproblema=Problema()
    confproblema.problema=eggHolder
    confproblema.tipoProblema=Constantes.PROBLEMA_NUMERICO
    confproblema.otrosDatos=tsp
    confproblema.criterio=Constantes.MINIMO
    confproblema.comentarios="Problema TSP xqf131.tsp -1 veces mutacion - ESCAPE 400-100"


    #GC
    gc=GC()
    gc.metodoSeleccion=Constantes.GC_SELECCION_RULETA
    gc.precision=0.3
    gc.porcentajeMutacion=0.3
    gc.porcentajeSeleccion=0.80
    #Funciones a utilizar
    gc.fGenerarPoblacion=tsp.generaPoblacion
    gc.fCruza=tsp.cruzaPosicion
    gc.fMutacion=tsp.mutacionInsercion
    #Parámetros de escape
    gc.escape=False
    gc.nIteracionesEscape=400
    gc.nIndividuosEscape=100


    gc.GCIslas(configIslas,confproblema)



if __name__ == "__main__":
    main()
