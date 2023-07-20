import numpy as np
import pandas as pd
from Modelos.modelo_red.herramientas import levantar_potencias, datos_ramas, datos_barras, levantar_datos_trafo3,crear_modelo_T,max_barra,filtrar_ramas_zinf

class red():
    '''
    Clase red es una clase con las propiedades:
    
    barras: dataframe con datos de las barras
    ramas: dataframe con datos de las ramas
    potencias: dataframe con datos de generacion y carga
    
    '''
    def __init__(self):
        self.barras=pd.DataFrame()
        self.ramas=pd.DataFrame()
    def fit(self):
        '''
        fit es una funcion que recopila los datos de el archivo .sav y los guarda en las variables barras y ramas
        Previo a hacer un fit, se debe ejecutar cargar_archivo_sav(ruta_archivoSAV) (ubicado en Modelos.herramientas.py) 
        '''
        #Eliminamos ramas de impedancia infinitas utilizados para estudio de transitorios
        filtrar_ramas_zinf()
        # Se cargan los datos de las barras
        self.barras = datos_barras()
        # Se cargan los datos de las ramas
        self.ramas = datos_ramas()
        # Se cargan las potencias activas y reactivas setadas en el .sav

        # print('*********************************************************') 
        # print(self.barras)  
        # Se levanta la informacion de los trafos de 3 bobinados
        self.trafos_3bob= levantar_datos_trafo3()
    
        self.Id_init,self.numero_barras = max_barra(self.barras)

        ramas_trafos3bob, barras_trafos3bob = crear_modelo_T(self.trafos_3bob,self.Id_init,self.numero_barras)
        # print('----------------------------------------')
        self.ramas = pd.concat([self.ramas,ramas_trafos3bob],ignore_index=True)
        self.barras = pd.concat([self.barras,barras_trafos3bob],ignore_index=True)
        self.voltajes, self.potencias = levantar_potencias(self)
        self.numero_ramas = len(self.ramas) - len(ramas_trafos3bob)
        