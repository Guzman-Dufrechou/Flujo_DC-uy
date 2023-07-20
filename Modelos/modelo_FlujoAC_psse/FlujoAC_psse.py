from Modelos.modelo_FlujoAC_psse.herramientas import resolver_flujo_ac, levantar_resultado

class FlujoAC_psse():
    '''
    Ejemplo:
    
    import psse 35
    from Modelos.modelo_red.red import Red
    from Modelos.modelo_FlujoAC_psse.FlujoAC_psse import FlujoAC_psse  
    from Modelos.herramientas import cargar_archivo_sav
     
    cargar_archivo_sav(archivoSav)
    
    Red=red() #defino la red 
    
    Red.fit()
    
    modelo=FlujoAC_psse()
    
    modelo.predict() #se considera que la potencia ya esta cargada en el .sav
    
    print(modelo.p_branches)
    '''
    def predict(self):
        # Se resuelve el flujo AC para la red previamente cargada en psse
        resolver_flujo_ac()
        # Luego de resolver el flujo ac se consulta los resultados y se guarda la potencia en las ramas
        self.resultado_ac = levantar_resultado()
       
        return
