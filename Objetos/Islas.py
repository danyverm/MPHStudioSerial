__author__ = 'daniel'
class Islas:
    def __init__(self):
        self.topologia=0
        self.nIslas=1
        self.islas=[]
        self.configuracion

class ConfiguracionIslas:
    def __init__(self):
        self.topologia=0
        self.nIslas=0
        self.metodoParo=0
        self.nGeneracionesNCParo=100
        self.nIslasNecesarias=1
        self.configuracionPoblaciones=[]
        self.nGeneracionesMaximasParo=1000



        self.nIndividuosTotal=10

        self.guardarDatosTXT=False
        self.archivoDatos=False
        self.guardarResultados=False
        self.archivoResultados=""

        self.generaPoblacion=True
        self.guardaPoblacion=False
        self.archivoPoblacion=""

        self.guardarTracking=False
        self.archivoTracking=""

        self.debug=False

        self.grafica=True

