#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = 'daniel'
import Constantes
from Objetos.Solucion import Solucion
from Problemas.Problemas import esMejor
import matplotlib.pyplot as plt
from random import random
from random import choice
from pylab import *
import os
import sqlite3
#from tabulate import tabulate
import time
import string
import numpy as np
import ConfigParser as cp
import tarfile
import tempfile
import math


try:
    import cPickle as pickle
except ImportError:
    import pickle


def cargarDatos(archivo):
    cfg = cp.ConfigParser()
    cfg.read([archivo])

def guardarDatosTXT(archivo,mejorIndividuo,tiempo,historial):
    fo=open(archivo,"w")
    fo.write("Los valores más optimos son: \n")
    for x in mejorIndividuo.valores:
        fo.write(str(x)+"\n")
    fo.write("El fitness es: "+str(mejorIndividuo.aptitud)+"\n")
    fo.write("El total de generaciones: "+str(len(historial[0].aptitudes))+"\n")
    fo.write("El tiempo de ejecución es: "+tiempo+"\n")
    for i in historial:
        fo.write("Población: "+str(i.idIsla)+",")
        for j in i.aptitudes:
            fo.write(str(j)+",")
        fo.write("\n")

    fo.close()

def guardarHistorialTXT(archivo,historial):
    fo=open(archivo,"w")
    fo.write("Los valores más optimos son: \n")

    for i in historial:
        fo.write("Población: "+str(i.idIsla)+",")
        for j in i.aptitudes:
            fo.write(str(j)+",")
        fo.write("\n")

    fo.close()


def solucionGeneral(soluciones,totalG,criterio):
    solucion=Solucion()
    for i in range(totalG):
        mejor=None
        for j in soluciones:
            try:
                if mejor is None:
                    mejor=j.aptitudes[i]
                elif esMejor(criterio,j.aptitudes[i],mejor):
                    mejor=j.aptitudes[i]
            except:
                pass
        solucion.aptitudes.append(mejor)

    return solucion


def graficaConvergencia(soluciones):
    x=[]
    y=[]

    ttext = plt.title("Grafica de Convergencia")
    ytext = ylabel("Aptitud")
    xtext = xlabel("Generaciones")
    setp(ttext, size='x-large', color='r', style='italic')
    setp(xtext, size='large', weight='bold', color='g')
    setp(ytext, size='large', weight='bold', color='b')


    ax = plt.subplot(111)

    for i in soluciones:
        x=np.arange(0,len(i.aptitudes),1)
        y=np.array(i.aptitudes)
        aleatorio=np.random.rand(3,1)
        ax.plot(x,y,'o-',color=aleatorio,label="Poblacion: "+str(i.idIsla))
    #Pongo el mejor punto
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

def graficaConvergenciaPromedio(solucion):
    x=[]
    y=[]

    ttext = plt.title("Grafica de Convergencia")
    ytext = ylabel("Aptitud")
    xtext = xlabel("Generaciones")
    setp(ttext, size='x-large', color='r', style='italic')
    setp(xtext, size='large', weight='bold', color='g')
    setp(ytext, size='large', weight='bold', color='b')


    ax = plt.subplot(111)
    x=np.arange(0,len(solucion.aptitudes),1)
    y=np.array(solucion.aptitudes)
    aleatorio=np.random.rand(3,1)
    ax.plot(x,y,'o-',color=aleatorio,label="General")
    #Pongo el mejor punto
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))


    plt.show()

def graficaConvergenciaComparacion(soluciones,nombre):
    x=[]
    y=[]

    ttext = plt.title("Grafica de Convergencia")
    ytext = ylabel("Aptitud")
    xtext = xlabel("Generaciones")
    setp(ttext, size='x-large', color='r', style='italic')
    setp(xtext, size='large', weight='bold', color='g')
    setp(ytext, size='large', weight='bold', color='b')


    ax = plt.subplot(111)

    for i,j in zip(soluciones,nombre):
        x=np.arange(0,len(i.aptitudes),1)
        y=np.array(i.aptitudes)
        aleatorio=np.random.rand(3,1)
        ax.plot(x,y,'o-',color=aleatorio,label=""+str(j))
    #Pongo el mejor punto
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))


    plt.show()

def guardarPoblacion(individuos,narchivo):
    archivo = file(narchivo, "w")
    pickle.dump(individuos, archivo, 2)

    archivo.close()

def cargarPoblacion(narchivo):
    archivo = file(narchivo)

    return pickle.load(archivo)

def creaBD(proceso):
    con=sqlite3.connect(str(proceso)+"tmpData.db")
    cursor=con.cursor()
    #Tabla población inicial
    query="CREATE TABLE PoblacionInicial(id INTEGER PRIMARY KEY AUTOINCREMENT, individuo TEXT, aptitud REAL)"
    cursor.execute("DROP TABLE IF EXISTS PoblacionInicial")
    cursor.execute(query)
    #Tabla Operación selección
    query="CREATE TABLE Seleccion(id INTEGER PRIMARY KEY AUTOINCREMENT, padre1 TEXT, padre1A REAL, padre2 TEXT, padre2A REAL, generacion INT, proceso INT)"
    cursor.execute("DROP TABLE IF EXISTS Seleccion")
    cursor.execute(query)
    #Tabla Operación Cruza
    query="CREATE TABLE Cruza(id INTEGER PRIMARY KEY AUTOINCREMENT, hijo1 TEXT, hijo2 TEXT, generacion INT, proceso INT)"
    cursor.execute("DROP TABLE IF EXISTS Cruza")
    cursor.execute(query)
    #Tabla Operación Mutación
    query="CREATE TABLE Mutacion(id INTEGER PRIMARY KEY AUTOINCREMENT, individuoI TEXT, individuoF TEXT, individuoA REAL, generacion INT, proceso INT)"
    cursor.execute("DROP TABLE IF EXISTS Mutacion")
    cursor.execute(query)
    #Tabla Operación Reemplazo
    query="CREATE TABLE Reemplazo(id INTEGER PRIMARY KEY AUTOINCREMENT, poblacionI TEXT, poblacionF TEXT, generacion INT, proceso INT)"
    cursor.execute("DROP TABLE IF EXISTS Reemplazo")
    cursor.execute(query)
    #Tabla Operación Migración
    query="CREATE TABLE Migracion(id INTEGER PRIMARY KEY AUTOINCREMENT, origen INT, destino INT,individuos TEXT)"
    cursor.execute("DROP TABLE IF EXISTS Migracion")
    cursor.execute(query)

    return con,cursor

def abreBD(nombre):
    con= sqlite3.connect(nombre)
    cursor=con.cursor()

    return con,cursor



def cerrarBD(conexion,cursor):
    if conexion:
        cursor.close()
        conexion.close()



def registraOperacionBD(cursor,proceso,operacion,generacion,datos):
    if operacion == Constantes.OPERACION_GENERARPOBLACION:
        for individuo in datos:
            valores=str(individuo.valores)

            aptitud=individuo.aptitud
            query="INSERT INTO PoblacionInicial(individuo,aptitud) VALUES(?,?)"
            cursor.execute(query,(valores,aptitud))

    elif operacion == Constantes.OPERACION_SELECCION:
        (padre1,padre2)=datos
        query="INSERT INTO Seleccion(padre1,padre1A,padre2,padre2A,generacion,proceso) VALUES(?,?,?,?,?,?)"
        cursor.execute(query,(str(padre1.valores),padre1.aptitud,str(padre2.valores),padre2.aptitud,generacion,proceso))
    elif operacion == Constantes.OPERACION_CRUZA:
        pass
    elif operacion == Constantes.OPERACION_MUTACION:
        pass
    elif operacion == Constantes.OPERACION_REEMPLAZO:
        pass
    elif operacion == Constantes.OPERACION_MIGRACION:
        pass
    else:
        pass

def crearArchivoRegistro(proceso):
     aGP=open(str(proceso)+"_GP_tmpData.db","w")
     aS=open(str(proceso)+"_SEL_tmpData.db","w")
     aC=open(str(proceso)+"_CZ_tmpData.db","w")
     aM=open(str(proceso)+"_MT_tmpData.db","w")
     aR=open(str(proceso)+"_RP_tmpData.db","w")
     aMI=open(str(proceso)+"_MI_tmpData.db","w")
     aO=open(str(proceso)+"_OO_tmpData.db","w")
     return aGP,aS,aC,aM,aR,aMI,aO

def abrirArchivoRegistro(nombre,tipo):
    return open(nombre,tipo)

def cerrarArchivoRegistro(archivos):
    for i in range(6):
        archivos[i].close()

def registrarOperacionArchivo(archivo,proceso,operacion,generacion,datos):
    if operacion == Constantes.OPERACION_GENERARPOBLACION:
        for individuo in datos:
            valores=str(individuo.valores)
            aptitud=individuo.aptitud
            query=valores+";"+str(aptitud)+"\n"
            archivo.write(query)
    elif operacion == Constantes.OPERACION_SELECCION:
        (padre1,padre2)=datos
        query=str(generacion)+";"+str(padre1.valores)+";"+str(padre1.aptitud)+";"+str(padre2.valores)+";"+str(padre2.aptitud)+"\n"
        archivo.write(query)
    elif operacion == Constantes.OPERACION_CRUZA:
        (hijo1,hijo2)=datos
        query=str(generacion)+";"+str(hijo1.valores)+";"+str(hijo2.valores)+"\n"
        archivo.write(query)
    elif operacion == Constantes.OPERACION_MUTACION:
        query=str(generacion)+";"+str(datos.valores)+";"+str(datos.aptitud)+"\n"
        archivo.write(query)
    elif operacion == Constantes.OPERACION_REEMPLAZO:
        pass
    elif operacion == Constantes.OPERACION_MIGRACION:
        destino,individuo=datos
        query=str(generacion)+";"+str(destino)+";"+str(individuo.valores)+";"+str(individuo.aptitud)+"\n"
        archivo.write(query)
    else:#Otras operaciones
        comentarios=datos
        query=str(generacion)+";"+str(comentarios)+"\n"
        archivo.write(query)

def crearArchivoTracking(archivo,nProcesos):
    ftar=tarfile.open(archivo,'w')
    ftar.add("resultados_mph.mpr")
    os.remove("resultados_mph.mpr")
    for proceso in range(1,nProcesos):
        ftar.add(str(proceso)+"_GP_tmpData.db")
        os.remove(str(proceso)+"_GP_tmpData.db")
        ftar.add(str(proceso)+"_SEL_tmpData.db")
        os.remove(str(proceso)+"_SEL_tmpData.db")
        ftar.add(str(proceso)+"_CZ_tmpData.db")
        os.remove(str(proceso)+"_CZ_tmpData.db")
        ftar.add(str(proceso)+"_MT_tmpData.db")
        os.remove(str(proceso)+"_MT_tmpData.db")
        ftar.add(str(proceso)+"_RP_tmpData.db")
        os.remove(str(proceso)+"_RP_tmpData.db")
        ftar.add(str(proceso)+"_MI_tmpData.db")
        os.remove(str(proceso)+"_MI_tmpData.db")
        ftar.add(str(proceso)+"_OO_tmpData.db")
        os.remove(str(proceso)+"_OO_tmpData.db")
    ftar.close()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(choice(chars) for _ in range(size))

def abrirArchivoTracking(archivo,aleatorio=None):
    if aleatorio==None:
        aleatorio=id_generator(10)

    try:
        carpeta=tempfile.gettempdir()+os.sep+"MPHSTUDIO"+os.sep+aleatorio+os.sep
        if not os.path.exists(tempfile.gettempdir()+os.sep+"MPHSTUDIO"):
            os.mkdir(tempfile.gettempdir()+os.sep+"MPHSTUDIO")
            os.mkdir(carpeta)
        elif not os.path.exists(carpeta):
            os.mkdir(carpeta)
        #Descomprimo el archivo
        ftar=tarfile.open(archivo,"r")
        listaA=ftar.getnames()
        ftar.extractall(path=carpeta)
        return aleatorio,carpeta,listaA
    except:
        print "Archivo no válido"
        return None,None,None

def cargarDatosTracking(carpeta,proceso,operacion,generacionInicial,generacionFinal):
    if operacion == Constantes.OPERACION_GENERARPOBLACION:
        datos=[]
        narchivo=carpeta+os.sep+str(proceso)+"_GP_tmpData.db"
        archivo=open(narchivo,"r")
        for linea in archivo:
            aux=linea.split(";")
            datos.append(aux)
        return datos
    elif operacion == Constantes.OPERACION_SELECCION:
        datos=[]
        narchivo=carpeta+os.sep+str(proceso)+"_SEL_tmpData.db"
        archivo=open(narchivo,"r")
        for linea in archivo:
            aux=linea.split(";")
            if int(aux[0])>= generacionInicial and int(aux[0])<=generacionFinal:
                datos.append(aux)
        return datos
    elif operacion == Constantes.OPERACION_CRUZA:
        datos=[]
        narchivo=carpeta+os.sep+str(proceso)+"_CZ_tmpData.db"
        archivo=open(narchivo,"r")
        for linea in archivo:
            aux=linea.split(";")
            if int(aux[0])>= generacionInicial and int(aux[0])<=generacionFinal:
                datos.append(aux)
        return datos
    elif operacion == Constantes.OPERACION_MUTACION:
        datos=[]
        narchivo=carpeta+os.sep+str(proceso)+"_MT_tmpData.db"
        archivo=open(narchivo,"r")
        for linea in archivo:
            aux=linea.split(";")
            if int(aux[0])>= generacionInicial and int(aux[0])<=generacionFinal:
                datos.append(aux)
        return datos
    elif operacion == Constantes.OPERACION_REEMPLAZO:
        datos=[]
        narchivo=carpeta+os.sep+str(proceso)+"_RP_tmpData.db"
        archivo=open(narchivo,"r")
        for linea in archivo:
            aux=linea.split(";")
            if int(aux[0])>= generacionInicial and int(aux[0])<=generacionFinal:
                datos.append(aux)
        return datos
    elif operacion == Constantes.OPERACION_MIGRACION:
        datos=[]
        narchivo=carpeta+os.sep+str(proceso)+"_MI_tmpData.db"
        archivo=open(narchivo,"r")
        for linea in archivo:
            aux=linea.split(";")
            if int(aux[0])>= generacionInicial and int(aux[0])<=generacionFinal:
                datos.append(aux)
        return datos
    else:#Otras operaciones
        datos=[]
        narchivo=carpeta+os.sep+str(proceso)+"_OO_tmpData.db"
        archivo=open(narchivo,"r")
        for linea in archivo:
            aux=linea.split(";")
            if int(aux[0])>= generacionInicial and int(aux[0])<=generacionFinal:
                datos.append(aux)
        return datos

def borrarDatosTracking(carpeta):
    if os.path.isdir(carpeta):
        for archivo in os.listdir(carpeta):
           os.remove(carpeta+os.sep+archivo)

        os.rmdir(carpeta)

def guardarResultados(configuracion,confProblema,tipo,datosHeuristica,mejorIndividuo,tiempo,historial):

    archivo = file(configuracion.archivoResultados, "w")

    pickle.dump(configuracion, archivo, 2)
    pickle.dump(mejorIndividuo, archivo, 2)
    pickle.dump(tiempo, archivo, 2)
    pickle.dump(historial, archivo, 2)

    pickle.dump(confProblema, archivo, 2)
    pickle.dump(tipo, archivo, 2)
    pickle.dump(datosHeuristica, archivo, 2)
    archivo.close()

def guardarResultadosTracking(configuracion,confProblema,tipo,datosHeuristica,mejorIndividuo,tiempo,historial):

    archivo = file("resultados_mph.mpr", "w")

    pickle.dump(configuracion, archivo, 2)
    pickle.dump(mejorIndividuo, archivo, 2)
    pickle.dump(tiempo, archivo, 2)
    pickle.dump(historial, archivo, 2)

    pickle.dump(confProblema, archivo, 2)
    pickle.dump(tipo, archivo, 2)
    pickle.dump(datosHeuristica, archivo, 2)
    archivo.close()

def cargarResultados(narchivo):
    archivo = file(narchivo)
    configuracion=pickle.load(archivo)
    mejor=pickle.load(archivo)
    tiempo=pickle.load(archivo)
    historial=pickle.load(archivo)

    problema=pickle.load(archivo)
    tipo=pickle.load(archivo)
    datosH=pickle.load(archivo)
    print ("\t\t\tMPHStudio V1.0.0\n\n")
    print ("Modelos de Metaheurísticas Multipoblacionales implementadas en paralelo")
    print("CONFIGURACIÓN")
    print("\tNo. de islas: "+str(configuracion.nIslas))
    if configuracion.topologia==Constantes.TOPOLOGIA_ANILLO:
        print("\tTopología: ANILLO")
    elif configuracion.topologia==Constantes.TOPOLOGIA_ESTRELLA:
        print("\tTopología: ESTRELLA")
    elif configuracion.topologia==Constantes.TOPOLOGIA_FULL:
        print("\tTopología: FULL")
    else:
        print("\tTopología: OTRO")

    if configuracion.metodoParo==Constantes.METODO_PARO_ITERACIONES:
        print("\tMétodo de paro: ITERACIONES")
    elif configuracion.metodoParo==Constantes.METODO_PARO_CONVERGENCIA:
        print("\tMétodo de paro: CONVERGENCIA")
    else:
        print("\tMétodo de paro: OTRO")
    print("\tNo. iteraciones sin resultado para detener: "+str(configuracion.nGeneracionesNCParo))
    print("\tNo. máximo de iteraciones: "+str(configuracion.nGeneracionesMaximasParo))

    print("\nConfiguración de las poblaciones")
    print("\tNo. de individuos: "+str(configuracion.configuracionPoblaciones[0].nIndividuos))
    print("\tNo. de individuos recibidos: "+str(configuracion.configuracionPoblaciones[0].nIndividuosRecibidos))
    print("\tNo. de individuos enviados: "+str(configuracion.configuracionPoblaciones[0].nIndividuosIntercambio))
    print("\tNo. de iteraciones por intercambio: "+str(configuracion.configuracionPoblaciones[0].nGeneracionesIntercambio))

    print("\nConfiguración del problema")
    print("\tComentarios: "+str(problema.comentarios))

    if tipo == 0:#Algoritmo genético
        print("\nAlgoritmo Genético")
        print("\tPorcentaje de selección: "+str(datosH[0]))
        print("\tPorcentaje de mutación: "+str(datosH[1]))


    print("\nRESULTADOS")
    print ("\tLos valores más optimos son: ")
    print ("\t"+str(mejor.valores))
    print ("\tEl fitness es: "+str(mejor.aptitud))
    print ("\tEl total de generaciones: "+str(len(historial[0].aptitudes)))
    print ("\tEl tiempo de ejecución es: "+str(tiempo))
    #Gráfica de Convergencia
    graficaConvergencia(historial)

def cargarResultadosUI(narchivo):
    try:
        archivo = file(narchivo)
        configuracion=pickle.load(archivo)
        mejor=pickle.load(archivo)
        tiempo=pickle.load(archivo)
        historial=pickle.load(archivo)

        problema=pickle.load(archivo)
        tipo=pickle.load(archivo)
        datosH=pickle.load(archivo)
        return configuracion,mejor,tiempo,historial,problema,tipo,datosH
    except Exception,e:
        print str(e)
        return None

def tabulaResultador(carpeta,campo,orden):

    print ("\t\t\tMPHStudio V1.0.0\n\n")
    print ("Modelos de Metaheurísticas Multipoblacionales implementadas en paralelo")
    print("Tabla de comparación de resultados")
    headers=[]
    try:
        archivos=os.listdir(carpeta)
        tabla=[]
        for narchivo in archivos:
            try:
                archivo = file(carpeta+narchivo)
                configuracion=pickle.load(archivo)
                mejor=pickle.load(archivo)
                tiempo=pickle.load(archivo)
                historial=pickle.load(archivo)

                problema=pickle.load(archivo)
                tipo=pickle.load(archivo)
                datosH=pickle.load(archivo)
                fila=[]
                fila.append(narchivo)
                fecha=time.ctime(os.path.getmtime(carpeta+narchivo))
                fecha=fecha.split(" ")
                fecha=[x for x in fecha if len(x)>0]
                hora=fecha[3].split(":")
                fila.append(fecha[2]+"/"+fecha[1]+"/"+fecha[4]+" "+hora[0]+":"+hora[1])
                if tipo == 0:
                    fila.append("Genetico")
                    fila.append("PS: "+str(datosH[0])+" PM: "+str(datosH[1]))

                else:
                    fila.append("Otro")
                    fila.append("")
                fila.append(mejor.aptitud)
                fila.append(float(tiempo))
                fila.append(str(configuracion.nIslas))
                if configuracion.topologia==Constantes.TOPOLOGIA_ANILLO:
                    fila.append("ANILLO")
                elif configuracion.topologia==Constantes.TOPOLOGIA_ESTRELLA:
                    fila.append("ESTRELLA")
                elif configuracion.topologia==Constantes.TOPOLOGIA_FULL:
                    fila.append("FULL")
                else:
                    fila.append("OTRO")

                if configuracion.metodoParo==Constantes.METODO_PARO_ITERACIONES:
                    fila.append("ITERACIONES")
                elif configuracion.metodoParo==Constantes.METODO_PARO_CONVERGENCIA:
                    fila.append("CONVERGENCIA")
                else:
                    fila.append("OTRO")


                fila.append(str(configuracion.configuracionPoblaciones[0].nIndividuos))
                fila.append(str(configuracion.nParo))
                fila.append(str(configuracion.nIteracionesParo))
                fila.append(str(configuracion.configuracionPoblaciones[0].nIndividuosRecibidos))
                fila.append(str(configuracion.configuracionPoblaciones[0].nIndividuosIntercambio))
                fila.append(str(problema.comentarios).decode("utf-8").encode('ascii', 'replace'))
                tabla.append(fila)
            except:
                print("Error al cargar el archivo "+str(narchivo))

        headers=["Archivo","Fecha","Algoritmo","P. Algoritmo","Aptitud","Tiempo (s)","Islas","Topologia","M. Paro","NI","NGP","NGM","NIR","NIE","Comentarios"]
        tabla=sorted(tabla, key=lambda llave: llave[campo], reverse=orden)
        print tabulate(tabla, headers, tablefmt="fancy_grid")

    except:
        print("Error al tabular!!!")

def tabulaResultadorUI(carpeta,campo,orden):
    try:
        archivos=os.listdir(carpeta)
        tabla=[]
        for narchivo in archivos:
            try:
                archivo = file(carpeta+os.sep+narchivo)
                configuracion=pickle.load(archivo)
                mejor=pickle.load(archivo)
                tiempo=pickle.load(archivo)
                historial=pickle.load(archivo)

                problema=pickle.load(archivo)
                tipo=pickle.load(archivo)
                datosH=pickle.load(archivo)

                try:
                    tipoConfiguracion=configuracion.cTipo

                except:
                    tipoConfiguracion=Constantes.CONFIGURACION_ISLAS

                fila=[]
                fila.append(narchivo)
                fecha=time.ctime(os.path.getmtime(carpeta+os.sep+narchivo))
                fecha=fecha.split(" ")
                fecha=[x for x in fecha if len(x)>0]
                hora=fecha[3].split(":")
                fila.append(fecha[2]+"/"+fecha[1]+"/"+fecha[4]+" "+hora[0]+":"+hora[1])
                if tipo == 0:

                    if tipoConfiguracion==Constantes.CONFIGURACION_ISLAS:
                        fila.append("Genetico")
                        fila.append("PS: "+str(datosH[0])+" PM: "+str(datosH[1]))
                    elif tipoConfiguracion==Constantes.CONFIGURACION_CELULAR:
                        fila.append("Genetico Celular")
                        fila.append("PS: "+str(datosH[0])+" PM: "+str(datosH[1])+" F: "+str(configuracion.filas)+" C: "+str(configuracion.columnas))

                else:
                    fila.append("Otro")
                    fila.append("")
                fila.append(mejor.aptitud)
                fila.append(float(tiempo))

                if tipoConfiguracion==Constantes.CONFIGURACION_ISLAS:
                    fila.append(str(configuracion.nIslas))
                    if configuracion.topologia==Constantes.TOPOLOGIA_ANILLO:
                        fila.append("ANILLO")
                    elif configuracion.topologia==Constantes.TOPOLOGIA_ESTRELLA:
                        fila.append("ESTRELLA")
                    elif configuracion.topologia==Constantes.TOPOLOGIA_FULL:
                        fila.append("FULL")
                    else:
                        fila.append("OTRO")
                elif tipoConfiguracion==Constantes.CONFIGURACION_CELULAR:
                    fila.append(str("NA"))
                    fila.append("NA")

                if configuracion.metodoParo==Constantes.METODO_PARO_ITERACIONES:
                    fila.append("ITERACIONES")
                elif configuracion.metodoParo==Constantes.METODO_PARO_CONVERGENCIA:
                    fila.append("CONVERGENCIA")
                else:
                    fila.append("OTRO")

                if tipoConfiguracion==Constantes.CONFIGURACION_ISLAS:
                    fila.append(str(configuracion.configuracionPoblaciones[0].nIndividuos))
                    fila.append(str(configuracion.nGeneracionesNCParo))
                    fila.append(str(configuracion.nGeneracionesMaximasParo))
                    fila.append(str(configuracion.configuracionPoblaciones[0].nIndividuosRecibidos))
                    fila.append(str(configuracion.configuracionPoblaciones[0].nIndividuosIntercambio))
                elif tipoConfiguracion==Constantes.CONFIGURACION_CELULAR:
                    fila.append(str(configuracion.nVecinos))
                    fila.append(str(configuracion.nGeneracionesNCParo))
                    fila.append(str(configuracion.nGeneracionesMaximasParo))

                fila.append(str(problema.comentarios).decode("utf-8").encode('ascii', 'replace'))
                tabla.append(fila)
            except Exception,e:
                print str(e)
                print("Error al cargar el archivo "+str(narchivo))
                return None


        tabla=sorted(tabla, key=lambda llave: llave[campo], reverse=orden)
        return tabla

    except:
        print("Error al tabular!!!")
        return None


def iniciaConfiguracionCelular(configuracion):
    configuracion.nVecinos=configuracion.filas*configuracion.columnas
    if configuracion.totalProcesos==0:
        configuracion.nIndividuosProceso=1
        configuracion.totalProcesos=configuracion.nVecinos
    else:
        configuracion.nIndividuosProceso = int(math.ceil(configuracion.nVecinos/float(configuracion.totalProcesos)))
    return True



def iniciaConfiguracionIslas(configuracion,confproblema,proceso,total):
    #Compruebo y configuro la topologia
    if configuracion.topologia==Constantes.TOPOLOGIA_ANILLO:
        if total>2:
            if proceso is 1:#Recibe del último y envía al siguiente
                configuracion.configuracionPoblaciones[proceso-1].destinos.append(2)
                configuracion.configuracionPoblaciones[proceso-1].fuentes.append(total-1)
            elif proceso is total-1:#ultimo
                configuracion.configuracionPoblaciones[proceso-1].destinos.append(1)
                configuracion.configuracionPoblaciones[proceso-1].fuentes.append(proceso-1)
            else:
                configuracion.configuracionPoblaciones[proceso-1].destinos.append(proceso+1)
                configuracion.configuracionPoblaciones[proceso-1].fuentes.append(proceso-1)
        else:
            pass


    elif configuracion.topologia==Constantes.TOPOLOGIA_ESTRELLA:
        if total>2:
            if proceso is 1:#Recibe de todos y envia a todos
                for i in range(2,total):
                    configuracion.configuracionPoblaciones[proceso-1].destinos.append(i)
                    configuracion.configuracionPoblaciones[proceso-1].fuentes.append(i)
            else:
                configuracion.configuracionPoblaciones[proceso-1].destinos.append(1)
                configuracion.configuracionPoblaciones[proceso-1].fuentes.append(1)
        else:
            pass
    elif configuracion.topologia==Constantes.TOPOLOGIA_FULL:
        if total>2:
            #Recibe de todos y envia a todos
            for i in range(1,total):
                configuracion.configuracionPoblaciones[proceso-1].destinos.append(i)
                configuracion.configuracionPoblaciones[proceso-1].fuentes.append(i)

        else:
            pass
    elif configuracion.topologia==Constantes.TOPOLOGIA_OTRA:
        pass


    #Genero el número total de individuos y copia de valores
    for i in range(total-1):
        configuracion.nIndividuosTotal+=configuracion.configuracionPoblaciones[i].nIndividuos
        configuracion.configuracionPoblaciones[i].guardarTracking=configuracion.guardarTracking
    #Compruebo el tipo de problema y asigno las funciones a utilizar
    if confproblema.tipoProblema==Constantes.PROBLEMA_NUMERICO:
        pass
    elif confproblema.tipoProblema==Constantes.PROBLEMA_COMBINATORIO:
        pass
    else:
        pass

    return True







