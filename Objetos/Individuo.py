#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'daniel'
import math


class Individuo:
    def __init__(self, ID=0):
        self.id = ID
        self.nDimensiones = 1
        self.rangosMin = []
        self.rangosMax = []
        self.valores = []
        self.aptitud = 0
        # Velocidad para PSO
        self.rangosMinV = []
        self.rangosMaxV = []
        self.velocidades = []
        #Valores para GC
        self.genotipo = []
        self.longitud = []


    def calculaLongitud(self,precision):
        for (a, b) in zip(self.rangosMin, self.rangosMax):
            aux = math.ceil(math.log((b - a) * math.pow(10, precision), 2))
            self.longitud.append(aux)


    def calculaGenotipo(self):
        genotipo = []
        for (valor, a, b, longitud) in zip(self.valores, self.rangosMin, self.rangosMax, self.longitud):
            aux = 0.0
            aux = ((valor - a) * (math.pow(2, longitud) - 1)) / (b - a)
            aux = math.ceil(aux)
            gen = bin(int(aux))[2:]
            ceros = longitud - len(gen)
            # Agrego ceros a la izquierda en caso de que falten
            while ceros > 0:
                gen = "0" + gen
                ceros = ceros - 1
            genotipo.append(gen)
        self.genotipo = genotipo
        return genotipo


    def calculaFenotipo(self):
        indice = 0
        for (gen, a, b, longitud) in zip(self.genotipo, self.rangosMin, self.rangosMax, self.longitud):
            valor = a + int(gen, 2) * ((b - a) / (math.pow(2, longitud) - 1))
            self.valores[indice] = valor
            indice = indice + 1

