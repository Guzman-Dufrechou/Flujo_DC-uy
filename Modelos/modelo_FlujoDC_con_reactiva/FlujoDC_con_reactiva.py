from Modelos.modelo_FlujoDC_con_reactiva.herramientas import generar_Ymodif,calcular_m,generar_H,generar_L,generar_PvQ,generar_delta_modif,calcular_flujo,reordenar_y_guardar_barras,reordenar_PQV

class FlujoDC_con_reactiva():
    '''
    Ejemplo:
    
    import psse 35
    from Modelos.modelo_red.red import Red
    from Modelos.modelo_FlujoDC_con_reactiva.FlujoDC_con_reactiva import FlujoDC_con_reactiva  
    from Modelos.herramientas import cargar_archivo_sav
     
    cargar_archivo_sav(archivoSav)
    
    Red=red() #defino la red 
    
    Red.fit()
    
    modelo=FlujoDC_con_reactiva()
    
    modelo.fit(Red)
    
    flujo = modelo.predict(Red.Potencia) 
    
    '''

    def fit(self,red,lambda1=0.96):
        
        self.barras, self.ramas = reordenar_y_guardar_barras(red)
        self.lambda1=lambda1
        self.G, self.B, self.contador = generar_Ymodif(self,red,lambda1)
        self.m = calcular_m(red)    # m es el indice de la ultima barra de generación
        self.H = generar_H(self.G,self.B,self.m+1)
        self.L = generar_L(self.G,self.B,self.m+1)
        self.numero_ramas=red.numero_ramas
        
        
    def predict(self,Potencia,Voltaje):
        P_aux,Q_aux,V_aux = reordenar_PQV(self,Potencia['P'],Potencia['Q'],Voltaje['V_PU'])
        PvQ = generar_PvQ(self.L,Q_aux,V_aux,self.m+1)
        delta_modif = generar_delta_modif(self.H,P_aux,PvQ)  
        self.flujo= calcular_flujo(self,delta_modif,self.G,self.B,self.lambda1)
        
        return self.flujo
    

