from Modelos.modelo_PTDF_clasico.herramientas import generar_matriz_A_B, CalculoDePTDF

class PTDF_clasico():
    '''
    Ejemplo:
    
    import psse 35
    from Modelos.modelo_red.red import Red
    from Modelos.modelo_PTDF_clasico.PTDF_clasico import PTDF_clasico  
    from Modelos.herramientas import cargar_archivo_sav
     
    cargar_archivo_sav(archivoSav)
    
    Red=red() #defino la red 
    
    Red.fit()
    
    modelo=PTDF_clasico()
    
    modelo.fit(Red)
    
    flujo, deltas = modelo.predict(Red.Potencia) 
    
    '''
    
    def fit(self,red):
        self.A, self.B = generar_matriz_A_B(red)
        self.i=red.barras['NUMBER'][red.barras['TYPE']==3]
        self.ptdf, self.fdelta = CalculoDePTDF(self.A,self.B,self.i)
        self.numero_barras=red.numero_barras
        self.numero_ramas=red.numero_ramas
    
    def predict(self,power):
        flujo=self.ptdf @ power['P']
        deltas=self.fdelta @ power['P']
        return flujo, deltas