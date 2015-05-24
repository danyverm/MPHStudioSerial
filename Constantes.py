#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = 'daniel'

#Método de paro
METODO_PARO_ITERACIONES=0
METODO_PARO_CONVERGENCIA=1
METODO_PARO_DIVERSIDAD=2


#Topologia
TOPOLOGIA_ANILLO=0
TOPOLOGIA_ESTRELLA=1
TOPOLOGIA_FULL=2
TOPOLOGIA_OTRA=3

#Grado de paralelismo
MPI=0
MPI_PROCESOS=1

#Criterios
MINIMO=0
MAXIMO=1

#Métodos de seleccion
GC_SELECCION_RULETA=0
GC_SELECCION_TORNEO=1

#Tipo de problema
PROBLEMA_NUMERICO=0
PROBLEMA_COMBINATORIO=1
PROBLEMA_OTRO=2

#Operaciones
OPERACION_GENERARPOBLACION=0
OPERACION_SELECCION=1
OPERACION_CRUZA=2
OPERACION_MUTACION=3
OPERACION_REEMPLAZO=4
OPERACION_MIGRACION=5
OPERACION_OTRAS=6

#Tipo de respuesta
TERMINACION_PROCESO=0
MEJOR_INDIVIDUO=1

#Tipo de gráfica
GRAFICA_POBLACIONES=0
GRAFICA_AVG=1

#GC Celular
CELULAR_FORMA_CRUZ=0
CELULAR_FORMA_CUADRADO=1
CELULAR_FORMA_ROMBO=2

#Tipo de configuración
CONFIGURACION_ISLAS=0
CONFIGURACION_POBLACION=1
CONFIGURACION_CELULAR=3
