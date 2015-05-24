#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = 'daniel'
import Constantes
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import cm

import numpy as np
from mpl_toolkits.mplot3d.axes3d import Axes3D

from Objetos import Individuo
class Problema:
    def __init__(self):
        self.criterio=Constantes.MINIMO
        self.problema=None
        self.comentarios=""

        #Otros
        self.tipoProblema=Constantes.PROBLEMA_NUMERICO
        self.otrosDatos=None


def calculaFitness(funcion,individuo):
    return funcion(individuo.valores)

def ejecutaFuncion(funcion,valores):
    return funcion(valores)
def ejecutaFuncionGrafica(funcion,X,Y):
    return funcion(X,Y)

def esMejor(criterio,primero,segundo):
    if criterio==Constantes.MINIMO:
        if primero<segundo:
            return True
        else:
            return False
    elif criterio==Constantes.MAXIMO:
        if primero>segundo:
            return True
        else:
            return False
    else:
        pass
def grafica3D(X,Y,Z,individuo):
    fig = plt.figure()
    # `ax` es una instancia de ejes 3D, ya que se usó el argumento projection='3d' en add_subplot
    ax = Axes3D(fig, azim = 115, elev =90)
    s = .05
    ax.plot_surface(Y,X, Z, rstride=4, cstride=4, linewidth=0)
    plt.show()


def graficarFuncion(configuracion,individuo):
    if individuo.nDimensiones==2:
        x=np.arange(individuo.rangosMin[0],individuo.rangosMax[0],0.1)
        y=np.arange(individuo.rangosMin[1],individuo.rangosMax[1],0.1)
        X, Y = np.meshgrid(x,y)
        Z=ejecutaFuncionGrafica(configuracion.graficaFuncion,X,Y)
        grafica3D(X,Y,Z,individuo)

    elif individuo.nDimensiones==1:
        x=np.arange(individuo.rangosMin[0],individuo.rangosMax[0],0.1)
        y=[]
        for i in x:
            valor=[i]
            y.append(ejecutaFuncion(configuracion.problema ,valor))
        y=np.array(y)
        plt.plot(x,y)
        #Pongo el mejor punto
        plt.plot(individuo.valores[0], individuo.aptitud, 'ro')
        plt.show()
    else:
        print("No es posible graficar funciones con mas de 3 Dimensiones")


