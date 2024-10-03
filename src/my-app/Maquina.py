from listaEnlazada import ListaEnlazada

class Maquina:
    def __init__(self, nombre, lineas):
        self.nombre = nombre
        self.lineas = lineas
    
    def agregarProducto(self, producto):
        self.lineas.append(producto)
    