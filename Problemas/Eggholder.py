__author__ = 'daniel'
from math import *
def eggHolder(valores):
    x=valores[0]
    y=valores[1]
    res=0.0
    res=-(y+47)*sin(sqrt(abs(y+(x/2)+47)))-x*sin(sqrt(abs(x-(y+47))))
    return res
