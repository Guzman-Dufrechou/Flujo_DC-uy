import psse35
import numpy as np
import openpyxl
import os

from Modelos.modelo_red.red import red
from Modelos.modelo_FlujoAC_psse.FlujoAC_psse import FlujoAC_psse
from Modelos.modelo_PTDF_clasico.PTDF_clasico import PTDF_clasico
from Modelos.modelo_PTDF_psse.PTDF_psse import PTDF_psse
from Modelos.modelo_PTDF_psse_modificado.PTDF_psse_modificado import PTDF_psse_modificado
from Modelos.modelo_FlujoDC_con_reactiva.FlujoDC_con_reactiva import FlujoDC_con_reactiva
from Modelos.modelo_FlujoDC_con_reactivacopy.FlujoDC_con_reactiva_v2 import FlujoDC_con_reactiva_v2
#from Modelos.FlujoDC_Vtheta import FlujoDC_Vtheta

from Modelos.herramientas import cargar_archivo_sav,crear_archivos_auxiliares
from Modelos.guardar_resultados import guardar_PTDF, Borrar_hoja, guardar_Flujos, graficar_resultados

###-----------------------------------------------------------
###---------------------Código--------------------------------
###-----------------------------------------------------------

### RED A UTILIZAR (archivo sav)

    
nombre_red = 'new_england'
# nombre_red = 'IEEE118bus'
#nombre_red = 'illinois200bus'
#nombre_red = 'new_england_sin3bob'  #tiene un trafo de tres bobinados


# El .sav es el unico archivo que es necesario que exista, 
# el resto son las rutas de donde se van a generar los archivos con,mon,sub,dfax

archivoSav = f'Redes\{nombre_red}' 

archivoSub = f'Archivos_PTDF_psse\{nombre_red}.sub'
archivoMon = f'Archivos_PTDF_psse\{nombre_red}.mon'
archivoCon = f'Archivos_PTDF_psse\{nombre_red}.con'
archivoDfx = f'Archivos_PTDF_psse\{nombre_red}.dfx'

# SE ABRE EL .SAV EN PSSPY
cargar_archivo_sav(archivoSav)

### INICIALIZACION

# INICIALIZO RED
Red=red()   

# INICIALIZO MODELOS
ptdf_clasico            = PTDF_clasico()    
ptdf_psse               = PTDF_psse()         
flujo_ac                = FlujoAC_psse()
flujodc_novedoso        = FlujoDC_con_reactiva_v2()
ptdf_psse_modificado    = PTDF_psse_modificado()

### AJUSTE A LA TOPOLOGIA DE LA RED

Red.fit()                                               # Se carga la red
crear_archivos_auxiliares(Red,nombre_red,archivoDfx,archivoSub, archivoMon, archivoCon)

ptdf_clasico.fit(Red)                                   # Aplico el modelo ptdf clasico
ptdf_psse.fit(Red, archivoCon, archivoDfx)              # Aplico modelo ptdf del psse
ptdf_psse_modificado.fit(Red, archivoCon, archivoDfx)   # Aplico modelo ptdf del psse Modificado
flujodc_novedoso.fit(Red)                               # Aplico modelo flujodc novedoso
### SIMULACION DE CASO (cargado en .sav)

flujo_ptdf_clasico, deltas = ptdf_clasico.predict(Red.potencias)
flujo_ptdf_psse            = ptdf_psse.predict(Red.potencias)
flujo_ptdf_psse_modificado = ptdf_psse_modificado.predict(Red.potencias)
Sol_novedoso               = flujodc_novedoso.predict(Red.potencias,Red.voltajes)
flujo_ac.predict()

### DESPLEGAR SOLUCION

archivo_excel = openpyxl.Workbook()
# # Se borra la hoja que se genera por defecto
Borrar_hoja(archivo_excel, 'Sheet')

# # Se guardan los PTDF del modelo clasico en excel
# guardar_PTDF(archivo_excel,'PTDF_clasico',ptdf_clasico.ptdf,Red)
# # Se guardan los PTDF del modelo psse en excel
# guardar_PTDF(archivo_excel,'PTDF_psse',ptdf_psse.ptdf,Red)
# # Se guardan los PTDF del modelo psse en excel
# guardar_PTDF(archivo_excel,'PTDF_psse_Modificado',ptdf_psse_modificado.ptdf,Red)

# Genero la matriz para cargar los distintos flujos en el excel
# lista_de_modelos = [['Flujo AC end','Flujo AC start','Flujo DC Clasico' , 'Flujo DC psse','Flujo DC con reactiva','Flujo DC psse Modif','X/R','Error relativo clásico - AC','Error relativo DC psse - AC','Error relativo DC con reactiva - AC','Error relativo DC psse Modif - AC']]
lista_de_modelos = [['Flujo AC end','Flujo AC start','Flujo DC Clasico' , 'Flujo DC psse','Flujo DC con reactiva','Flujo DC psse Modif','X/R','Error absoluto clásico - AC','Error absoluto DC psse - AC','Error absoluto DC con reactiva - AC','Error absoluto DC psse Modif - AC']]
#n_modelos=6
#lista_de_modelos = [['Flujo AC end','Flujo AC start','Flujo DC Clasico','Flujo DC con reactiva','Flujo DC psse','Flujo DC psse Modif']]
n_modelos = 6

Matriz_de_flujos = np.zeros((len(Red.ramas),len(lista_de_modelos[0])))
# print('******************************************')
# print(len(flujo_ptdf_clasico))
# print(len(flujo_ptdf_psse))
# print(len(flujo_ptdf_psse_modificado))
# print(len(np.around(Sol_novedoso)))
# print(len(flujo_ac.p_branches_end))


Matriz_de_flujos[:,lista_de_modelos[0].index('Flujo DC Clasico')]=flujo_ptdf_clasico  
Matriz_de_flujos[:,lista_de_modelos[0].index('Flujo DC psse')]=flujo_ptdf_psse    #Se quitan los trafos de tres devanados
Matriz_de_flujos[:,lista_de_modelos[0].index('Flujo DC psse Modif')]=flujo_ptdf_psse_modificado  
Matriz_de_flujos[:,lista_de_modelos[0].index('Flujo DC con reactiva')]=np.around(Sol_novedoso,3) 
Matriz_de_flujos[:,lista_de_modelos[0].index('Flujo AC end')]=flujo_ac.resultado_ac['p_branches_end']
Matriz_de_flujos[:,lista_de_modelos[0].index('Flujo AC start')]=flujo_ac.resultado_ac['p_branches_end']

#Matriz_de_flujos[:,lista_de_modelos[0].index('X/R')]=Red.ramas['X (pu)'][:Red.numero_ramas]/Red.ramas['R (pu)'][:Red.numero_ramas]
Matriz_de_flujos[:,lista_de_modelos[0].index('X/R')]=Red.ramas['X (pu)']/Red.ramas['R (pu)']
#Matriz_de_flujos[:,lista_de_modelos[0].index('Error relativo clásico - AC')] = abs(np.divide(flujo_ptdf_clasico - flujo_ac.resultado_ac['p_branches_end'],flujo_ac.resultado_ac['p_branches_end']*100)
#Matriz_de_flujos[:,lista_de_modelos[0].index('Error relativo DC psse - AC')] = abs(np.divide(flujo_ptdf_psse - flujo_ac.resultado_ac['p_branches_end'],flujo_ac.resultado_ac['p_branches_end'])*100)
#Matriz_de_flujos[:,lista_de_modelos[0].index('Error relativo DC psse Modif - AC')] = abs(np.divide(flujo_ptdf_psse_modificado - flujo_ac.resultado_ac['p_branches_end'],flujo_ac.resultado_ac['p_branches_end'])*100)
#Matriz_de_flujos[:,lista_de_modelos[0].index('Error relativo DC con reactiva - AC')] = abs(np.divide(np.around(Sol_novedoso) - flujo_ac.resultado_ac['p_branches_end'],flujo_ac.resultado_ac['p_branches_end'])*100)

Matriz_de_flujos[:,lista_de_modelos[0].index('Error absoluto clásico - AC')] = abs(flujo_ptdf_clasico - flujo_ac.resultado_ac['p_branches_end'])
Matriz_de_flujos[:,lista_de_modelos[0].index('Error absoluto DC psse - AC')] = abs(flujo_ptdf_psse - flujo_ac.resultado_ac['p_branches_end'])
Matriz_de_flujos[:,lista_de_modelos[0].index('Error absoluto DC psse Modif - AC')] = abs(flujo_ptdf_psse_modificado - flujo_ac.resultado_ac['p_branches_end'])
Matriz_de_flujos[:,lista_de_modelos[0].index('Error absoluto DC con reactiva - AC')] = abs(np.around(Sol_novedoso) - flujo_ac.resultado_ac['p_branches_end'])

#print('*************************************************')

guardar_Flujos(archivo_excel,'Flujos',Matriz_de_flujos,Red,lista_de_modelos)

# # Se guarda el excel con el nombre "Resultados"
archivo_excel.save(filename = f'Resultados_{nombre_red}.xlsx')

graficar_resultados(Matriz_de_flujos , Red , lista_de_modelos[0][:n_modelos],lista_de_modelos[0][n_modelos:])
