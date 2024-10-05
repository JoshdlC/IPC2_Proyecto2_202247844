from listaEnlazada import ListaEnlazada

class Producto:
    def __init__(self, nombre):
        self.nombre = nombre
        self.componentes = ListaEnlazada()
        self.tiempoTotal = 0

    def agregarComponentes(self, linea, numero):
        componente = Componente(linea, numero)
        self.componentes.append(componente)
    

class Componente:
    def __init__(self, linea, numero):
        self.linea = linea
        self.numero = numero
        
    
    