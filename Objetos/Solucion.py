#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = 'daniel'
from Objetos.Individuo import Individuo
class Solucion:
    def __init__(self,idIsla=0):
        self.individuo=[]
        self.nGeneraciones=0
        self.idIsla=idIsla
        self.tiempo=0.0

        #Soluciones por cada generación
        self.aptitudes=[]
        self.generaciones=[]
        self.termina=False
