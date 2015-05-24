__author__ = 'daniel'
from math import *
def rosenBrock(valores):
    res=0.0
    for i in range(0,len(valores)):
        res+=100*pow((pow(valores[i],2)-valores[i+1]),2)+pow(valores[i+1]-1,2)
    return res

def rosenBrockGrafica(X,Y):
    return 100*(X**2-Y)**2+(Y-1)**2