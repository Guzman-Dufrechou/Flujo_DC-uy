from Modelos.modelo_PTDF_psse_modificado.herramientas import modificar_X_en_red, cargar_X
from Modelos.modelo_PTDF_psse.herramientas import calculo_de_otdf,signos_de_ptdf,calculo_de_ptdf


class PTDF_psse_modificado():
    '''
    Ejemplo:
    
    import psse 35
    from Modelos.modelo_red.red import Red
    from Modelos.modelo_PTDF_psse_modificado.PTDF_psse_modificado import PTDF_psse_modificado  
    from Modelos.herramientas import cargar_archivo_sav
     
    cargar_archivo_sav(archivoSav)
    
    Red=red() #defino la red 
    
    Red.fit()
    
    modelo=PTDF_psse_modificado()
    
    modelo.fit(Red)
    
    flujo = modelo.predict(Red.Potencia) 
    
    '''
    def fit(self, red, archivoCon, archivoDfx):
        """
        Los archivos sub, con y dfax se crean desde el pss.
        """
        # Se modifica el valor de X en la red
        modificar_X_en_red(red) 
        # Modifica B de las ramas
        # Se calculan los factores de distribucion en modulo ya que no tienen convencion de signos
        otdf = calculo_de_otdf(red,archivoDfx)
        
        # Se genera el vector de signos dependiendo si la contingencia 
        # que se usa para calcular el otdf es de generacion o demanda
        signosFactores = signos_de_ptdf(otdf,archivoCon)
        
        #Se calcula el PTDF propiamente dicho 
        self.ptdf = calculo_de_ptdf(red,otdf,signosFactores)
        # Se regresa el valor de X a la normalidad
        cargar_X(red,red.ramas['X (pu)'])
        self.numero=red.numero_barras

    def predict(self,power):
        flujo=self.ptdf @ power['P'][:self.numero+1]
       
        return flujo
