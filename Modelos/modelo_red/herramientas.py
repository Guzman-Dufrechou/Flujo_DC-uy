import numpy as np
import psspy
import pandas as pd


dtypes_barras = np.dtype(
[
    ('NUMBER', int),
    ('ID', int),
    ('TYPE', int),
    ('NAME', str),
    ('EXNAME',str),
    ('AREA',int)
]
)
dtype_ramas = np.dtype(
[
('ID',int),
('FROMNUMBER',int),
('TONUMBER',int),
('FROMNAME',str),
('TONAME',str),
('TYPE',int),
('R (pu)',float),
('X (pu)',float),
('G (pu)',float),
('B (pu)',float),
('B_ch (pu)',float) 
]
)


def datos_barras():
    '''
    Funcion encargada de levantar los datos de las barras del .sav
    
    Devuelve:
    
        NUMBER, ID, TYPE, NAME, EXNAME
    
    '''
    ierr, number = psspy.abusint(-1, 1, 'NUMBER')
    ierr, name = psspy.abuschar(-1, 1, 'NAME')
    ierr, xname = psspy.abuschar(-1, 1, 'EXNAME')
    ierr, type_bus = psspy.abusint(-1, 1, 'TYPE')
    ierr, areas = psspy.abusint(-1,1,'AREA')
    datos={
        'NUMBER':range(len(number[0])),	# Numero asignado por nosotros para cada barra
        'ID':number[0],                 # Numero de identificacion de cada barra
        'TYPE':np.abs(type_bus[0]),             # Tipo de barra (PV, PQ o Slack) se identifica cada tipo con un numero
        'NAME':name[0],                 # Nombre de la barra
        'EXNAME':xname[0],               # Nombre extendido de la barra
        'AREA':areas[0]
    }
    
    return pd.DataFrame(data=datos)
    
def filtrar_ramas_zinf():    
    '''
    Función encargada de levantar los datos de las ramas del .sav y eliminar las ramas con impedancia infinita
    
    Devuelve:
    
        .sav editado sin esas ramas
    
    '''

    ierr, name_branch = psspy.abrnchar(-1, flag=1, string='ID')
    ierr, fromnumber = psspy.abrnint(-1, flag=1, string='FROMNUMBER')
    ierr, tonumber = psspy.abrnint(-1, flag=1, string='TONUMBER')
    ierr, zarray = psspy.abrncplx(-1, flag=1,string='RX')    
     
    z_module = np.absolute(zarray[0])
    
 
    for i, z_ramas in enumerate(z_module):
        if z_ramas>9999:
            psspy.purgbrn(fromnumber[0][i],tonumber[0][i],name_branch[0][i])
    
    return

def datos_ramas():    
    '''
    Funcion encargada de levantar los datos de las ramas del .sav
    
    Devuelve:
    
        ID, FROMNUMBER, TONUMBER, FROMNAME, TONAME, TYPE, R (pu), X (pu), G (pu), B (pu), B_ch (pu)
    
    '''

    ierr, name_branch = psspy.abrnchar(-1, flag=3, string='ID')
    ierr, fromname = psspy.abrnchar(-1, flag=3, string='FROMNAME')
    ierr, toname = psspy.abrnchar(-1, flag=3, string='TONAME')
    ierr, fromnumber = psspy.abrnint(-1, flag=3, string='FROMNUMBER')
    ierr, tonumber = psspy.abrnint(-1, flag=3, string='TONUMBER')
    ierr, type_linea = psspy.abrnint(-1, flag=3, string='TYPE')
    ierr, zarray = psspy.abrncplx(-1, flag=3,string='RX')    
    ierr, b_charging = psspy.abrnreal(-1, flag=3, string='CHARGING')
    ierr, Rate = psspy.abrnreal(-1, flag=3, string = 'RATEA')
    
    # Se calcula la admitancia a partir de la impoedancia
    
    yarray=np.zeros(len(zarray[0]),dtype=complex) 
    zarray = np.round(zarray,6)
    
    # yarray=1/zarray
    for i in range(len(zarray[0])):
        a=zarray[0][i]
        b=(1+0j)
        yarray[i]=b/a
    
    z_imaginary=np.imag(zarray[0])
    z_real=np.real(zarray[0])
    
    y_imaginary=np.imag(yarray)
    y_real=np.real(yarray)
    
    datos={
        'ID':name_branch[0],
        'FROMNUMBER':fromnumber[0],
        'TONUMBER':tonumber[0],
        'FROMNAME':fromname[0],
        'TONAME':toname[0],
        'TYPE':type_linea[0],
        'R '+"(pu)":z_real,
        'X '+"(pu)":z_imaginary,
        'G '+"(pu)":y_real,
        'B '+"(pu)":y_imaginary,
        'B_ch '+"(pu)":b_charging[0],
        'rate':Rate[0],
    }
    
    return pd.DataFrame(data=datos)

def levantar_potencias(red):
    '''
    Funcion que levanta la potencia activa y reactiva de las cargas y los generadores 
    
    Devuelve:
    
        V_PU, V_BASE, ID_BUS, P, Q
    P y Q inyectado en cada barra (o consumido)    
    
    '''
    P=np.zeros(len(red.barras.index))
    Q=np.zeros(len(red.barras.index))
    
    ierr, S = psspy.aloadcplx(-1, 1, 'TOTALACT') #Flag = 1 cargas en servicio en buses en servicio
    ierr, bus = psspy.aloadint(-1, 1, 'NUMBER')
    ierr, id_load = psspy.aloadchar(-1, 1, 'ID')
    
    datos={
        'BUS':bus[0],	            # Posición original en la lista de barras
        'P':np.real(np.array(S[0])),
        'Q':np.imag(np.array(S[0])),
        'ID_LOAD':id_load[0]
    }
    cargas=pd.DataFrame(data=datos)
    
    ierr, S = psspy.amachcplx(-1, 1, 'PQGEN') #Flag = 1 cargas en servicio en buses en servicio
    ierr, bus = psspy.amachint(-1, 1, 'NUMBER')
    ierr, id_mach = psspy.amachchar(-1, 1, 'ID')
    
    datos={
        'BUS':bus[0],	            # Posición original en la lista de barras
        'P':np.real(np.array(S[0])),
        'Q':np.imag(np.array(S[0])),
        'ID_MACH':id_mach[0]
    }
    generacion=pd.DataFrame(data=datos)
    
    for id_carga in cargas.index:
        id_bus=cargas['BUS'][id_carga]
        index_bus=red.barras['NUMBER'][red.barras['ID']==id_bus]
        P[index_bus]-=cargas['P'][id_carga]
        Q[index_bus]-=cargas['Q'][id_carga]

    for id_mach in generacion.index:
        id_bus=generacion['BUS'][id_mach]
        index_bus=red.barras['NUMBER'][red.barras['ID']==id_bus]
        P[index_bus]+=generacion['P'][id_mach]
        Q[index_bus]+=generacion['Q'][id_mach]

    ierr, V_pu = psspy.abusreal(-1, 1, 'PU')
    ierr, V_BASE = psspy.abusreal(-1, 1, 'BASE')
    ierr, Bus = psspy.abusint(-1, 1, 'NUMBER')
    ## Aca habria que ver si los voltajes se devuleven en el mismo orden que tenemos las barras
    
    datos={
        'V_PU':V_pu[0],	#posición original en la lista de barras
        'V_BASE':V_BASE[0],
        'ID_BUS':Bus[0],
        }
    return pd.DataFrame(data=datos), pd.DataFrame(data={'P':P, 'Q':Q})
    
#levanto los datos de los transformadores de 3 arrollamientos

def levantar_datos_trafo3():


    #ierr, id_primario= psspy.atr3int(-1, flag=1, string = 'WIND1NUMBER')
    #ierr, id_secundario= psspy.atr3int(-1, flag=1, string = 'WIND2NUMBER')
    #ierr, id_terciario= psspy.atr3int(-1, flag=1, string = 'WIND3NUMBER')
    #ierr, Z12 = psspy.atr3cplx(-1, flag=1, string = 'RX1-2NOM')
    #ierr, Z23 = psspy.atr3cplx(-1, flag=1, string = 'RX2-3NOM')
    #ierr, Z31 = psspy.atr3cplx(-1, flag=1, string = 'RX3-1NOM')
    ierr, Z_trafo = psspy.awndcplx(-1, flag=1, entry=2 , string = 'RXNOM')        #Esta ya da la impedancia de cada bobinado.
    ierr, id_pri= psspy.awndint(-1, flag=1, entry=2, string = 'WIND1NUMBER')
    ierr, id_sec= psspy.awndint(-1, flag=1, entry=2, string = 'WIND2NUMBER')
    ierr, id_ter= psspy.awndint(-1, flag=1, entry=2, string = 'WIND3NUMBER')
    ierr, numero_wind = psspy.awndint(-1, flag=1, entry=2, string = 'WNDNUM')
    ierr, nombretrafo = psspy.awndchar(-1,ties=2,entry=2, flag=1,string='XFRNAME')
    ierr, nombre_wind = psspy.awndchar(-1,ties=2,entry=2, flag=1,string='WNDBUSNAME')
    ierr, rate = psspy.awndreal(-1,ties=2,entry=2, flag=1,string='RATEA')

    
    Z_primario = []
    Z_secundario = []
    Z_terciario = []
    id_primario = []
    id_secundario = []
    id_terciario = []
    nombre_trafo=[]
    nombre_primario=[]
    nombre_secundario=[]
    nombre_terciario=[]
    rate_pri=[]
    rate_sec=[]
    rate_ter=[]

    for i,num in enumerate(Z_trafo[0]):
        
        if numero_wind[0][i] == 1: 
            Z_primario.append(num)
            id_primario.append(id_pri[0][i])
            nombre_trafo.append(nombretrafo[0][i].strip())
            nombre_primario.append(nombre_wind[0][i])
            rate_pri.append(rate[0][i])
        elif numero_wind[0][i] == 2: 
            Z_secundario.append(num)
            id_secundario.append(id_sec[0][i])
            nombre_secundario.append(nombre_wind[0][i])
            rate_sec.append(rate[0][i])
        else: 
            Z_terciario.append(num)
            id_terciario.append(id_ter[0][i])
            nombre_terciario.append(nombre_wind[0][i])
            rate_ter.append(rate[0][i])
  
    #datos={
    #        'Primario':id_primario[0],
    #        'Secundario':id_secundario[0],
    #        'Terciario': id_terciario[0],
    #        'Z12': Z12[0],
    #        'Z23':Z23[0],
    #        'Z31':Z31[0],           
    #}
    
    datos={
            'Primario':id_primario,
            'Secundario':id_secundario,
            'Terciario': id_terciario,
            'Z1':Z_primario,
            'Z2':Z_secundario,
            'Z3':Z_terciario,
            'nombretrafo': nombre_trafo,
            'name_pri':nombre_primario,
            'name_sec':nombre_secundario,
            'name_ter':nombre_terciario, 
            'rate_pri':rate_pri,
            'rate_sec':rate_sec,
            'rate_ter':rate_ter,         
    }
    
    return pd.DataFrame(data=datos) 
  

def crear_modelo_T(datos_trafo,Id_init,numero):
    datos_barra = pd.DataFrame(np.empty(0, dtype=dtypes_barras))
    datos_ramas = pd.DataFrame(np.empty(0, dtype=dtype_ramas))

    id_barra_z = Id_init
    num = numero
    
    for trafo in datos_trafo.index:
        
        num += 1
        id_barra_z += 1
        
        datos={
        'NUMBER':num,	# Numero asignado por nosotros para cada barra
        'ID':id_barra_z,                 # Numero de identificacion de cada barra
        'TYPE':2,             # Tipo de barra (PV, PQ o Slack) se identifica cada tipo con un numero
        'NAME':f'AUX_TRAFO_{id_barra_z}',                 # Nombre de la barra
        'EXNAME':f'AUX_TRAFO_{id_barra_z}'               # Nombre extendido de la barra
        }
        
        datos_barra = pd.concat([datos_barra,pd.DataFrame([datos])],ignore_index = True)
        
        
        
        #z_primario   = (datos_trafo['Z12'][trafo] + datos_trafo['Z31'][trafo] - datos_trafo['Z23'][trafo])/2
        #z_secundario = (datos_trafo['Z12'][trafo] + datos_trafo['Z23'][trafo] - datos_trafo['Z31'][trafo])/2
        #z_terciario  = (datos_trafo['Z31'][trafo] + datos_trafo['Z23'][trafo] - datos_trafo['Z12'][trafo])/2
        z_primario = datos_trafo['Z1'][trafo]
        z_secundario = datos_trafo['Z2'][trafo]
        z_terciario = datos_trafo['Z3'][trafo]

        y_primario = (1+0j)/z_primario
        y_secundario = (1+0j)/z_secundario
        y_terciario = (1+0j)/z_terciario
        
        datos={
        'ID':1,'FROMNUMBER':datos_trafo['Primario'][trafo],'TONUMBER':id_barra_z,
        'FROMNAME':datos_trafo['name_pri'][trafo],'TONAME':f"AUX {datos_trafo['nombretrafo'][trafo]}",'TYPE':18,
        'R '+"(pu)":np.real(z_primario),
        'X '+"(pu)":np.imag(z_primario),
        'G '+"(pu)":np.real(y_primario),
        'B '+"(pu)":np.imag(y_primario),
        'B_ch '+"(pu)":0,
        'rate':datos_trafo['rate_pri'][trafo]
        }

        datos_ramas = pd.concat([datos_ramas,pd.DataFrame([datos])],ignore_index = True)
        
        datos={
        'ID':1,'FROMNUMBER':datos_trafo['Secundario'][trafo],'TONUMBER':id_barra_z,
        'FROMNAME':datos_trafo['name_sec'][trafo],'TONAME':f"AUX {datos_trafo['nombretrafo'][trafo]}",'TYPE':18,
        'R '+"(pu)":np.real(z_secundario),
        'X '+"(pu)":np.imag(z_secundario),
        'G '+"(pu)":np.real(y_secundario),
        'B '+"(pu)":np.imag(y_secundario),
        'B_ch '+"(pu)":0,
        'rate':datos_trafo['rate_sec'][trafo]
        }

        datos_ramas = pd.concat([datos_ramas,pd.DataFrame([datos])],ignore_index = True)

        datos={
        'ID':1,'FROMNUMBER':datos_trafo['Terciario'][trafo],'TONUMBER':id_barra_z,
        'FROMNAME':datos_trafo['name_ter'][trafo],'TONAME':f"AUX {datos_trafo['nombretrafo'][trafo]}",'TYPE':18,
        'R '+"(pu)":np.real(z_terciario),
        'X '+"(pu)":np.imag(z_terciario),
        'G '+"(pu)":np.real(y_terciario),
        'B '+"(pu)":np.imag(y_terciario),
        'B_ch '+"(pu)":0,
        'rate':datos_trafo['rate_ter'][trafo]
        }

        datos_ramas = pd.concat([datos_ramas,pd.DataFrame([datos])],ignore_index = True)
        
    return datos_ramas, datos_barra

def max_barra(barras):
    '''Se extrae el máximo valor de ID y NUMBER de barra para no reescribir al modelar los trafos de 3 bobinados'''

    max_id = barras['ID'].max()
    max_number = barras['NUMBER'].max()

    return max_id, max_number

def filtrar_ramas():
    #Se filtran las ramas type 18 que son las creadas para considerar los trafos de 3 bobinados

    return