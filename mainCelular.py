#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'daniel'
import Constantes
from Objetos.Islas import ConfiguracionIslas
from Objetos.Poblacion import ConfiguracionPoblacion
from Objetos.Celulas import ConfiguracionCelular
from Metaheuristicas.GCCelular import GCCelular
from Problemas.Rosenbrock import *
from Problemas.TSP import *
from Problemas.Schwefel import *
from Problemas.Otra import *
from Problemas.Eggholder import *
from Problemas.Problemas import Problema
from Util import cargarDatos
import sys
def main():
    """

    """
    # Declaro las variables
    if len(sys.argv) > 1:
        # Cargo los datos necesarios para correr la metaheurística
        cargarDatos(sys.argv[1])
    else:
        #Configuración de las Islas

        #Configuración del TSP
        tsp=ConfiguracionTSP()#10 Ciudades
        tsp.cargarTSPLib("TSPData/dj38.tsp")
        tsp.nVecesMuta=1
        tsp.nPosiciones=1
        tsp.porcentajeMutacion=0.7

        confproblema=Problema()
        confproblema.problema=eggHolder
        confproblema.tipoProblema=Constantes.PROBLEMA_NUMERICO
        confproblema.otrosDatos=tsp
        confproblema.criterio=Constantes.MINIMO
        confproblema.comentarios="TSP"


        configCelulas=ConfiguracionCelular()
        configCelulas.columnas=50
        configCelulas.filas=50
        configCelulas.rangosMin=(-512,-512)
        configCelulas.rangosMax=(512,512)
        configCelulas.nDimensiones=2
        configCelulas.metodoParo=Constantes.METODO_PARO_CONVERGENCIA
        #Número máximo de generaciones por ejecución
        configCelulas.nGeneracionesMaximasParo=20000
        #Número máximo de generaciones sin cambio en la aptitud del mejor individuo
        configCelulas.nGeneracionesNCParo=500
        configCelulas.nParejasGeneracion=4

        #configCelulas.nIndividuosProceso=10
        configCelulas.totalProcesos=100


        #Utilidades
        configCelulas.guardarDatosTXT=False
        configCelulas.archivoDatos="resultado1.txt"
        configCelulas.guardarResultados=True
        configCelulas.archivoResultados="Resultados/resultado_pruebaCelular_Nueva2500.mpr"
        configCelulas.debug=True
        configCelulas.grafica=True
        configCelulas.tipoGrafica=Constantes.GRAFICA_AVG

        configCelulas.guardaPoblacion=False
        configCelulas.generaPoblacion=True
        configCelulas.archivoPoblacion="poblacion1.pbl"
        configCelulas.guardarTracking=False
        configCelulas.archivoTracking="/home/daniel/Tracking/track1CelularDemo.mpt"

        gc=GCCelular()
        gc.radio=5
        gc.forma=Constantes.CELULAR_FORMA_ROMBO
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
        gc.nIteracionesEscape=150
        gc.nIndividuosEscape=50

        gc.GCCelular(configCelulas,confproblema)



if __name__ == "__main__":
    main()
