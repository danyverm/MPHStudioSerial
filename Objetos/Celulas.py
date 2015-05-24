__author__ = 'daniel'
from Objetos.Poblacion import ConfiguracionPoblacion
import Constantes

class Celulas:
    def __init__(self):
        self.vecinos=[]


class ConfiguracionCelular(ConfiguracionPoblacion):

    def __init__(self):
        ConfiguracionPoblacion.__init__(self)
        self.cTipo=Constantes.CONFIGURACION_CELULAR
        self.metodoParo=0
        self.nGeneracionesMaximasParo=10
        self.nGeneracionesNCParo=100
        self.nParejasGeneracion=1


        self.filas=1
        self.columnas=1

        self.nVecinos=1

        self.nIndividuosProceso=0
        self.totalProcesos=0


        self.nParo=100
        self.metodoParo=0

        self.nDimensiones=2
        self.rangosMin=[]
        self.rangosMax=[]

        self.gradoParalelo=0

        self.guardarTracking=False

        self.generaPoblacion=True
        self.guardaPoblacion=False
        self.archivoPoblacion=""


        self.archivoTracking=""

        self.debug=False

        self.grafica=True
        self.tipoGrafica=Constantes.GRAFICA_POBLACIONES

        self.guardarDatosTXT=False
        self.archivoDatos=False
        self.guardarResultados=False
        self.archivoResultados=""
