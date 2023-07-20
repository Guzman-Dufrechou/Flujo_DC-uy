import pssarrays
import numpy as np
import pandas as pd

def calculo_de_ptdf(red,otdf,signosFactores):
    # cambia los signos de las columnas de la matriz que entrega PSS/E de acuerdo a signosFactores:
    matriz=np.dot(np.diag(signosFactores),np.asarray(otdf.factor))
    # se inserta la columna asociada a la barra slack
    #matriz=np.delete(matriz,otdf.trafos_a_borrar,axis=1)
   
    for num,i in enumerate(otdf.trafos_a_borrar):
        
        matriz = np.insert(matriz,matriz.shape[1],matriz[:,otdf.trafos_a_mover[num]],axis=1)
      
    matriz=np.delete(matriz,otdf.trafos_a_borrar,axis=1)
    
    return np.insert(matriz,red.barras.index[red.barras['TYPE']==3],np.zeros(matriz.shape[1]),0).T
    
def calculo_de_otdf(red, archivoDfx):
    # Obtiene los factores de distribucion
    otdf=pssarrays.otdf_factors(archivoDfx)
    
    trafos_a_borrar=[]
    melement_3WND= []
    ramas_trafos3=[]
    trafos_a_mover=[]
    indice= []

    if otdf.ierr!=0:
        print('error en pssarrays.otdf_factors codigo:' + str(otdf.ierr))
    otdf['ramas_trafos_3']=ramas_trafos3          
    
   
    for num, i in enumerate(otdf.melement):
            melement_3WND.append(i)
            indice.append(num)
            if '3WNDTR' in i:
                trafos_a_borrar.append(num)
              
    
    error = 0

    for trafo in red.trafos_3bob.index:
        if red.trafos_3bob['nombretrafo'][trafo]=="":
            error = 1 
            print('Error: hay un transformador de tres bobinados sin nombre')
            
    if error==0: 
    
        for trafo in red.trafos_3bob.index:
            
            trafos_a_moverP = -1
            trafos_a_moverS = -1
            trafos_a_moverT = -1
            id_Primario = red.trafos_3bob['Primario'][trafo]
            id_Secundario = red.trafos_3bob['Secundario'][trafo]
            id_Terciario = red.trafos_3bob['Terciario'][trafo]   
            
            nombre_trafo = red.trafos_3bob['nombretrafo'][trafo]
            
            for num in indice:
                
                if f'{nombre_trafo[0:14]}' in melement_3WND[num]:
                    
                    if f'{id_Primario}' in melement_3WND[num]:
                        trafos_a_moverP =num
                        
                    elif f'{id_Secundario}' in melement_3WND[num]:
                        trafos_a_moverS = num
                        
                    elif f'{id_Terciario}' in melement_3WND[num]:
                        trafos_a_moverT = num

            if trafos_a_moverP==-1 or trafos_a_moverS==-1 or trafos_a_moverT==-1:
                print('Error: No se encontró alguna rama del transformador')
            else:          
                trafos_a_mover.append(trafos_a_moverP)
                trafos_a_mover.append(trafos_a_moverS)
                trafos_a_mover.append(trafos_a_moverT)
        
    if otdf.ierr!=0:
        print('error en pssarrays.otdf_factors codigo:' + str(otdf.ierr))
    otdf['trafos_a_borrar']=trafos_a_borrar
    otdf['trafos_a_mover']=trafos_a_mover      
   
    return otdf

def signos_de_ptdf(otdf,archivoCon):
    '''
    Se genera un vector con el signo del factor de distribucion de potencia 
    dependiendo de si la contingencia se asocia a generacion o demanda
    '''
    # crea vector inicial con "ceros" para ajustar el signo de los factores ("power shift" de PSS/E)
    signosFactores=np.zeros(len(otdf.codesc))
    
    # Analiza la descripcion de cada contingencia para definir el signo
    for i in range(len(otdf.codesc)):
        codesc=otdf.codesc[i]
    # Generacion
        if 'GENERATION' in codesc:
            if 'INCREASE' in codesc:
                signosFactores[i]=-1 # cambia signo
            elif 'RAISE' in codesc:
                signosFactores[i]=-1 # cambia signo
            else:
                print("> Contingencia de generacion en .MON no reconocida: "  + codesc +"\n" + ">>Accion adoptada:: Se cambia el signo de PSS/E (otdf.factor)" + "\n" + ">>Archivo: " + archivoCon)
                signosFactores[i]=-1 # cambia signo
        # Demanda
        elif 'LOAD' in codesc:
            if 'INCREASE' in codesc:
                signosFactores[i]=-1
            elif 'RAISE' in codesc:
                signosFactores[i]=-1			# Esto lo modificamos.
            else:
                print("> Contingencia de demanda en .MON no reconocida: "  + codesc +"\n" + ">>Accion adoptada: No se afecta el signo de PSS/E (otdf.factor)" + "\n" + ">>Archivo: " + archivoCon)
                signosFactores[i]=1
        else:
            print("> Contingencia en .MON no reconocida: "  + codesc +"\n" + ">>Accion adoptada: No se afecta el signo de PSS/E (otdf.factor)" + "\n" + ">>Archivo: " + archivoCon)
            signosFactores[i]=1
    return signosFactores