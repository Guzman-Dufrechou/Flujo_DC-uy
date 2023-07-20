import psspy
from os import path
import numpy as np

def cargar_archivo_sav(archivoSav):
    psspy.psseinit(100000)
    ierr = psspy.case(archivoSav)       #Levanta archivo sav con la topología de la red
    if ierr!=0: 
        print("Codigo de error al abrir el archivo .sav: " + str(ierr))
        raise SystemExit

def crear_archivos_auxiliares(Red,nombre_red,archivoDfx,archivoSub, archivoMon, archivoCon):
	'''Creación de archivos necesarios para correr PTDF_PSSE'''
	crear_archivoCON(Red,archivoCon) 
	areas = consultar_areas(Red)	
	crear_archivoSUB(archivoSub,nombre_red,areas)
	crear_archivoMON(archivoMon,nombre_red)			
	crear_subsistema(areas)
	crear_archivoDFAX(archivoDfx,archivoSub, archivoMon, archivoCon)
	


def crear_archivoCON(net,Ruta_archivoCON):

	f = open(f'{Ruta_archivoCON}',"w")		#La f dentro de open permite escribir texto y ponerle variables. Y la w crear archivo y se sobreescribe.
	f.write("COM\n")
	f.write("COM CONTINGENCY description file entry: creado por el grupo de Proyecto FlujoDC-UY\n")
	f.write("COM\n")
	for barra in net.barras[:net.numero_barras+1].index:
		if net.barras['TYPE'][barra]==2: 	#Type generación
			f.write('CONTINGENCY ' + str(net.barras['ID'][barra])+'\n')								#id es el número de barra definido en el .sav
			f.write('INCREASE BUS ' + str(net.barras['ID'][barra]) + ' GENERATION BY 1 MW \n')
			f.write('END\n')
		if net.barras['TYPE'][barra]==1:	#Type demanda
			f.write('CONTINGENCY ' + str(net.barras['ID'][barra])+'\n')
			f.write('RAISE BUS ' + str(net.barras['ID'][barra]) + ' LOAD BY 1 MW \n')
			f.write(f'END\n')
	f.write(f'END\n')
	f.close()
	return

def crear_archivoMON(Ruta_archivoMON,nombre_red):
	f = open(f'{Ruta_archivoMON}',"w")		#La f dentro de open permite escribir texto y ponerle variables. Y la w crear archivo y se sobreescribe.
	f.write("/PSS(R)E 34\n")
	f.write("COM\n")
	f.write("COM MONITORED element file entry created by PSS(R)E Config File Builder\n")
	f.write("COM\n")
	# f.write(f"MONITOR VOLTAGE RANGE SUBSYSTEM '{nombre_red}' 0.950 1.050\n")
	# f.write(f"MONITOR VOLTAGE DEVIATION SUBSYSTEM '{nombre_red}' 0.030 0.060\n")
	f.write(f"MONITOR BRANCHES IN SUBSYSTEM '{nombre_red}'\n")
	f.write(f"MONITOR TIES FROM SUBSYSTEM '{nombre_red}'\n")
	f.write(f'END\n')
	f.close()
	return

def crear_subsistema(areas):
	
	#psspy.bsys(0,0,[0.0, 500.],2,[93,99],0,[],0,[],0,[])	#La crea dentro de pss para armar el archivo dfax
	psspy.bsys(0,0,[0.0, 500.],2,[],0,[],0,[],0,[])
	#psspy.bsys(0,0,[0.0, 500.],2,[areas[0],areas[1]],0,[],0,[],0,[])	
	return

def crear_archivoSUB(Ruta_archivoSUB,nombre_red,areas):
	' Esto está creado para la red de 118 BUS, modificar para la Uruguaya área 93 y 99'
	f = open(f'{Ruta_archivoSUB}',"w")		#La f dentro de open permite escribir texto y ponerle variables. Y la w crear archivo y se sobreescribe.
	f.write("/PSS(R)E 34\n")
	f.write("COM\n")
	f.write("COM SUBSYSTEM description file entry created by PSS(R)E Config File Builder\n")
	f.write("COM\n")
	f.write(f"SUBSYSTEM '{nombre_red}'\n")
	for i in range(0,areas.shape[0]):
		if areas[i] != 0:						#El área es un número entre 1 y 9999
			f.write(f"AREA '{areas[i]}' \n")
	#f.write("AREA 99\n")
	#f.write("AREA 93\n")
	#**********************
	f.write("END\n")
	f.write("END\n")
	f.close()
	return

def crear_archivoDFAX(Ruta_archivoDFAX,Archivo_sub,Archivo_mon,Archivo_con):
	
	error_dfax=psspy.dfax_2([1,0,0],Archivo_sub,Archivo_mon,Archivo_con,Ruta_archivoDFAX)
	if error_dfax!=0: 	
		print ('error en psspy.dfax codigo:' + str(error_dfax))
	return

def consultar_areas(Red):
	area = np.zeros(32,dtype=int)
	i=1
	j=0
	for barra in Red.barras[:Red.numero_barras+1].index:
		iar=Red.barras['AREA'][barra]						#Defino variable iar de numero de área de esa barra
		
		if barra == 0: 
			area[0] = iar
		
		for i in range(0,area.shape[0]):

			if area[i]==iar:
				Area_cargada = True
				j = i+1
				break
			else: 
				Area_cargada = False
		if not Area_cargada:
			area[j] = iar	
	
	area = area[0:j]
	
	return area

