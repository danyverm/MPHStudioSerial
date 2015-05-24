__author__ = 'daniel'
class Poblacion:
    def __init__(self):
        self.id=0
        self.nIndividuos=0
        self.individuos=[]


    def sumaAptitud(self):
        sumatoria = 0
        for i in self.individuos:
            sumatoria += i.aptitud
        return sumatoria

class ConfiguracionPoblacion:
    def __init__(self):
        self.nParo=100
        self.nGeneracionesIntercambio=1
        self.nIndividuosIntercambio=1
        self.nIndividuosRecibidos=1
        self.metodoParo=0
        self.nIndividuos=10
        self.nDimensiones=2
        self.rangosMin=[]
        self.rangosMax=[]

        self.destinos=[]
        self.fuentes=[]

        #Velocidad para PSO
        self.rangosMinV=[]
        self.rangosMaxV=[]

        self.gradoParalelo=0

        self.guardarTracking=False