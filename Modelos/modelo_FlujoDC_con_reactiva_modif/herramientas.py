import numpy as np
def reordenar_y_guardar_barras(red):
    # self.barras = net.barras.sort_values(['TYPE','ID'],ascending=[False,True]) #si desordeno tendria que tener en cuenta el orden para Potencia      
    barras = red.barras.sort_values(['TYPE'],ascending=[False]) #si desordeno tendria que tener en cuenta el orden para Potencia
    barras = barras.reset_index(drop=True)
    return barras, red.ramas

def reordenar_PQV(self,P,Q,V):
    P_aux = np.zeros(len(P))
    Q_aux = np.zeros(len(P))
    V_aux = np.ones(len(P))
    for barra_indx in self.barras.index:
        P_aux[barra_indx]=P[self.barras['NUMBER'][barra_indx]]
        Q_aux[barra_indx]=Q[self.barras['NUMBER'][barra_indx]]
        try:
            V_aux[barra_indx]=V[self.barras['NUMBER'][barra_indx]]
        except:
            barr_err=self.barras['NUMBER'][barra_indx]
            #En caso de necesitar definir otro valor de tension que no sea 1, se debe agregar aca como V_aux[barra_indx]=lo que sea
            print(f'no hay voltaje definido para la barra: {barr_err}')
    return P_aux,Q_aux,V_aux
        
def generar_Ymodif(self,red,lambda1):
    m=len(red.barras)
    G=np.zeros((m,m))
    B=np.zeros((m,m))
    contador = np.zeros((m,m))
    for rama in red.ramas.index:
        desde=red.ramas['FROMNUMBER'][rama]
        hasta=red.ramas['TONUMBER'][rama]
        indice_desde=self.barras.index[self.barras['ID']==desde]
        indice_hasta=self.barras.index[self.barras['ID']==hasta]

        b=red.ramas['B (pu)'][rama]
        g=red.ramas['G (pu)'][rama]

        B[indice_desde,indice_hasta]+= -b
        B[indice_hasta,indice_desde]=B[indice_desde,indice_hasta]

        G[indice_desde,indice_hasta]+= g
        G[indice_hasta,indice_desde]=G[indice_desde,indice_hasta]

        contador[indice_desde,indice_hasta]+= 1
        contador[indice_hasta,indice_desde]= contador[indice_desde,indice_hasta]
    
    for i in range(B.shape[0]):
        B[i,i]=-np.sum(B[i,:])
        G[i,i]=-np.sum(G[i,:])
    G=G*lambda1
    B=B*lambda1
    return G, B, contador

def separar_matriz(M,m):
    Mmm = M[:m,:m]
    Mmn = M[:m,m:]
    Mnm = M[m:,:m]
    Mnn = M[m:,m:]
    return Mmm, Mmn, Mnm, Mnn
	
def generar_H(G,B,m):
    Gmm, Gmn, Gnm, Gnn = separar_matriz(G,m)
    Bmm, Bmn, Bnm, Bnn = separar_matriz(B,m)

    Hmm = - (Gmn @ np.linalg.inv(Bnn) @ Gnm + Bmm)
    Hmn = - (Gmn @ np.linalg.inv(Bnn) @ Gnn + Bmn)
    Hnm = - (Gnn @ np.linalg.inv(Bnn) @ Gnm + Bnm)
    Hnn = - (Gnn @ np.linalg.inv(Bnn) @ Gnn + Bnn)

    H_up = np.concatenate((Hmm, Hmn), axis=1)
    H_down = np.concatenate((Hnm, Hnn), axis=1)

    H = np.concatenate((H_up,H_down), axis=0)
    #Eliminar primer fila y primer columna de H ñoqui para obtener H
    H = np.delete(H, 0, 1)
    H = np.delete(H, 0, 0)
    return H 

def generar_L(G,B,m):
    Gmm, Gmn, Gnm, Gnn = separar_matriz(G,m)
    Bmm, Bmn, Bnm, Bnn = separar_matriz(B,m)

    L_vm = Gmm - (Gmn @ np.linalg.inv(Bnn) @ Bnm)
    L_Qm = - (Gmn @ np.linalg.inv(Bnn) ) 
    L_vn = Gnm - (Gnn @ np.linalg.inv(Bnn) @ Bnm)
    L_Qn = - (Gnn @ np.linalg.inv(Bnn) ) 

    L_up = np.concatenate((L_vm,L_Qm), axis=1)
    L_down = np.concatenate((L_vn, L_Qn), axis=1)

    L = np.concatenate((L_up, L_down), axis=0)
    
    return L 

def generar_PvQ(L,Q,V,m):
    # m es el indice de la ultima barra de generación + 1
    Vm = V[:m] #Tensión nodos de generación
    Qn = Q[m:] #Reactiva nodos de carga
    V_Q = np.concatenate((Vm**2, Qn), axis=None)
    PvQ = L@V_Q 
    #Eliminar primer fila y primer columna de Pvq ñoqui para obtener Pvq
    PvQ = np.delete(PvQ, 0, 0)
    return PvQ

def generar_delta_modif(H,P,PvQ):
    # abria que ver la dimension de P y PvQ para ver si concuerdan
    delta_modif = np.linalg.inv(H)@(P[1:] - PvQ)
    delta_modif = np.insert(delta_modif,obj=0,values=0,axis=0)
    return delta_modif

def calcular_m(self):
    m = int(np.sum(self.barras['TYPE']==2)) # más la slack
    return m

def calcular_flujo(self,delta_modif,tension, G, B, lambda1):
    flujo=np.zeros(len(self.ramas))
    
    for rama in self.ramas.index:
        i=self.barras.index[self.barras['ID'] == self.ramas['FROMNUMBER'][rama]].values[0]
        j=self.barras.index[self.barras['ID'] == self.ramas['TONUMBER'][rama]].values[0]     
        flujo[rama] = (G[i,j]*(tension[i]**2-tension[j]**2) + B[i,j]*(delta_modif[i]-delta_modif[j]))/self.contador[i,j]
        deltai= delta_modif[i]/(tension[i]**2)
        deltaij = delta_modif[i]/(tension[i]**2) - delta_modif[j]/(tension[j]**2)
        #flujo[rama] = B[i,j]/lambda1*(delta_modif[i]-delta_modif[j])
       
       # print('Para la rama: ', self.ramas['FROMNUMBER'][rama],'/',self.ramas['TONUMBER'][rama], ' (',rama,') ', ' el delta i: ', delta_modif[i] , ' el delta j: ', delta_modif[j])
       # print(deltaij)
       # print(deltai)
       # print('tensión from',tension[i],'tensión to',tension[j])
        
    return flujo