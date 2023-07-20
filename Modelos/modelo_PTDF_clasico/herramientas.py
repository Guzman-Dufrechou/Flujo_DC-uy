import numpy as np
import pandas as pd
def generar_matriz_A_B(net):
    m=net.barras.shape[0] #numero de nodos
    l=net.ramas.shape[0] #numero de lineas
    A=np.zeros([l,m])
    B=np.zeros([l,l])

    for rama in net.ramas.index:
        A[rama,net.barras['NUMBER'][net.barras['ID']==net.ramas['FROMNUMBER'][rama]]]=1
        A[rama,net.barras['NUMBER'][net.barras['ID']==net.ramas['TONUMBER'][rama]]]=-1
        B[rama,rama]=net.ramas['B (pu)'][rama]
    return A, B

	
def CalculoDePTDF(A,B,i):
    '''
    A : Es la matriz de incidencia que indica la forma de la red (entre que nodos se conecta una línea)
    B : Es la matriz de admitancias de las lineas (matriz diagonal)
    i : Nodo de referencia (con este nodo determinamos la barra slack)
    '''
    l,m = A.shape # l : Cantidad de lineas // m : cantidad de nodos
    
    #Calculo de la matriz B*A y quitandole el nodo de referencia
    K1=(B @ A) 
    #Se borra la columna asociada a la barra slack
    K1 = np.delete(K1, i, 1)
    #Calculo de la matriz A.T@B@A y quitandole el nodo de referncia
    K2=A.T @ B @ A 
    #Se borra la columna y la fila asociada a la barra slack
    K2 = np.delete(K2, i, 1)
    K2 = np.delete(K2, i, 0)
    # np.save('matriznoinvertible.txt',B)
    #Se calculan los factores de angulos en las barras
    FDelta = np.linalg.inv(K2)
    #Calculo de los PTDF propiamente dicho
    PTDF = K1 @ FDelta
    # Se agregan filas y columnas de 0s asociadas a la barra slack
    FDelta = np.insert(FDelta, i, 0, axis=1)
    FDelta = np.insert(FDelta, i, 0, axis=0)
    
    PTDF = np.insert(PTDF, i, 0, axis=1)
    return PTDF, FDelta        