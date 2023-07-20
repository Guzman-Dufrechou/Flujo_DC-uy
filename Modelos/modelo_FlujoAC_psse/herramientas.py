import numpy as np
import psspy
import pandas as pd

def resolver_flujo_ac():
    # [(1)tap, (2)area int, (3)phase shift, (4)dc tap, (5)switched shunt, (6)flat start, (7)var limit, (8)non divergent solution ]		
    ierr = psspy.fdns([0,0,0,0,0,1,99,0])	#Resuelve: fixed slope decoupled Newton-Raphson power flow calculation.
    if ierr!=0: 
        print("Error FlujoAC_psse - Codigo de error al resolver N-R: " + str(ierr))

def levantar_resultado():
    '''
    Funcion que consulta el resultado de P y Q luego de que se resuelve un flujo AC en psse
    '''
    ierr, PQ_branches_end = psspy.abrncplx(-1, flag=3,string='PQ')
    ierr, PQ_branches_los = psspy.abrncplx(-1, flag=3,string='PQLOSS')
    ierr, S_trafos3 = psspy.awndcplx(-1, ties = 2, entry = 2, flag=1, string ='PQ')
    ierr, S_trafos3_loss = psspy.awndcplx(-1, ties = 2,entry = 2, flag=1, string ='PQLOSS')
   
    
    
    #ierr, P_trafos3 = psspy.awndreal(-1, ties = 2, entry=2, flag=1, string ='P')

    Potenciastrafos3={
            'p_branches_end':np.round(np.real(np.array(S_trafos3[0])),2),
            'q_branches_end':np.round(np.imag(np.array(S_trafos3[0])),2),
            'p_branches_start': np.round(np.real(np.array(S_trafos3[0])+np.array(S_trafos3_loss[0])),2),		#variable con valores de flujo de P por las ramas a partir de N-R de PSSE
            'q_branches_start': np.round(np.imag(np.array(S_trafos3[0])+np.array(S_trafos3_loss[0])),2)	
    }
    PQtrafos3=pd.DataFrame(Potenciastrafos3)

    if ierr!=0: 
        print("Error FlujoAC_psse - Codigo de error al consultar P y Q en las ramas del sistema: " + str(ierr))
    Potenciasramas={
        'p_branches_end': np.round(np.real(PQ_branches_end[0]),2),	#variable con valores de flujo de P por las ramas a partir de N-R de PSSE
        'q_branches_end': np.round(np.imag(PQ_branches_end[0]),2),		#variable con valores de flujo de Q por las ramas a partir de N-R de PSSE
        'p_branches_start': np.round(np.real(np.array(PQ_branches_end[0])+np.array(PQ_branches_los[0])),2),		#variable con valores de flujo de P por las ramas a partir de N-R de PSSE
        'q_branches_start': np.round(np.imag(np.array(PQ_branches_end[0])+np.array(PQ_branches_los[0])),2)		#variable con valores de flujo de Q por las ramas a partir de N-R de PSSE
    }
    PQramas = pd.DataFrame(Potenciasramas)

    # for rama in net.ramas.index:
    #	print('FROM NODO '+str(net.ramas['FROMNUMBER'][rama]) +' - TO NODO ' + str(net.ramas['TONUMBER'][rama]) + ' el flujo P es: ' + str(self.p_branches[rama]) + ' MW' ' y el flujo de Q es:' + str(self.q_branches[rama]) + ' MVAr')
    #print(PQramas)
    #print(PQtrafos3)
    #print(pd.concat([PQramas,PQtrafos3],ignore_index = True))
    
    return pd.concat([PQramas,PQtrafos3],ignore_index = True)

    #return p_branches_end, q_branches_end, p_branches_start, q_branches_start

#########################
##### Condigo viejo #####
#########################

_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
		
def modificar_potencia(self,P,Q,net):
    '''Asumiendo que el vector es de largo cantidad de barras con la potencia activa y reactiva consumida y generada.'''
    for barra in net.barras.index:
        if net.barras['TYPE'][barra]==1: 	#Type demanda (No generación)
            psspy.load_chng_5(net.barras['ID'][barra],r"""1""",[_i,_i,_i,_i,_i,_i],[-P[barra], -Q[barra],_f,_f,_f,_f])

        if net.barras['TYPE'][barra]==2:	#Type generación
            psspy.machine_chng_2(net.barras['ID'][barra],r"""1""",[_i,_i,_i,_i,_i,_i],[P[barra],_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])

def inicializar_barras(self,net):
    for carga in net.cargas.index:
        psspy.load_chng_5(net.cargas['BUS'][carga],net.cargas['ID_LOAD'][carga],[_i,_i,_i,_i,_i,_i],[0,0,_f,_f,_f,_f])
    for gener in net.generadores.index:
        psspy.machine_chng_2(net.generadores['BUS'][gener],net.generadores['ID_GEN'][gener],[_i,_i,_i,_i,_i,_i],[0,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
