__author__ = 'daniel'
from math import *
def schwefel(valores):
    res=0.0
    for i in valores:
        res += i * sin(sqrt(fabs(i)))
    return res

def schwefelGrafica(X,Y):
    res = X * sin(sqrt(fabs(X)))+Y * sin(sqrt(fabs(Y)))
    return res