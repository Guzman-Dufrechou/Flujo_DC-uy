import numpy as np
import psspy

_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
_s=psspy.getdefaultchar()

def modificar_X_en_red(net):
	R = net.ramas['R (pu)']
	X = net.ramas['X (pu)']
	X_modif = np.sqrt(R**2+X**2)
	cargar_X(net,X_modif)
	return

def cargar_X(net,X_modif):
	for rama in net.ramas.index:
		b_from = net.ramas['FROMNUMBER'][rama]
		b_to = net.ramas['TONUMBER'][rama]
		psspy.branch_chng_3(b_from,b_to ,r"""1""",[_i,_i,_i,_i,_i,_i],[_f,X_modif[rama],_f ,_f,_f,_f,_f,_f,_f,_f,_f,_f],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s)
	return