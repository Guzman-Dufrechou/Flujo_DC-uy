
import numpy as np
import openpyxl
import psse34
import psspy


x= np.load('matriznoinvertible.txt.npy')
from Modelos.herramientas import cargar_archivo_sav,crear_archivos_auxiliares
from Modelos.guardar_resultados import guardar_PTDF, Borrar_hoja, guardar_Flujos, graficar_resultados
from Modelos.modelo_red.red import red

### RED A UTILIZAR (archivo sav)
#nombre_red = 'tutoresv2'
nombre_red = 'tutoresv3 - copia' 

# El .sav es el unico archivo que es necesario que exista, 
# el resto son las rutas de donde se van a generar los archivos con,mon,sub,dfax
archivoSav = f'Redes\{nombre_red}.sav' 

# SE ABRE EL .SAV EN PSSPY
cargar_archivo_sav(archivoSav)

### INICIALIZACION

# INICIALIZO RED
Red=red()   

### AJUSTE A LA TOPOLOGIA DE LA RED

Red.fit()                                  

archivo_excel = openpyxl.Workbook()
# # Se borra la hoja que se genera por defecto
Borrar_hoja(archivo_excel, 'Sheet')
guardar_PTDF(archivo_excel,'matriz',x,Red)
archivo_excel.save(filename = f'Matriz.xlsx')