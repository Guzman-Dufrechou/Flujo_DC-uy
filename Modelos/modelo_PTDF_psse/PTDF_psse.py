from Modelos.modelo_PTDF_psse.herramientas import calculo_de_ptdf, signos_de_ptdf, calculo_de_otdf

class PTDF_psse():
    '''
    Ejemplo:
    
    import psse 35
    from Modelos.modelo_red.red import Red
    from Modelos.modelo_PTDF_psse.PTDF_psse import PTDF_psse  
    from Modelos.herramientas import cargar_archivo_sav
     
    cargar_archivo_sav(archivoSav)
    
    Red=red() #defino la red 
    
    Red.fit()
    
    modelo=PTDF_psse()
    
    modelo.fit(Red)
    
    flujo = modelo.predict(Red.Potencia) 
    
    '''
    
    def fit(self, red, archivoCon, archivoDfx):
        # Se calculan los factores de distribucion en modulo ya que no tienen convencion de signos
        otdf = calculo_de_otdf(red,archivoDfx)
        
        # Se genera el vector de signos dependiendo si la contingencia 
        # que se usa para calcular el otdf es de generacion o demanda
        signosFactores = signos_de_ptdf(otdf,archivoCon)
        
        #Se calcula el PTDF propiamente dicho 
        self.ptdf = calculo_de_ptdf(red,otdf,signosFactores)
        self.numero_barras=red.numero_barras
        return
    
    def predict(self,power):
        flujo=self.ptdf @ power['P'][0:self.numero_barras+1]
        return flujo
