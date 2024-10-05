from listaEnlazada import ListaEnlazada

class Maquina:
    def __init__(self, nombre, cantidadLineas, cantidadComponentes, tiempoProd):
        self.nombre = nombre
        self.cantidadLineas = cantidadLineas
        self.cantidadComponentes = cantidadComponentes
        self.tiempoProd = tiempoProd
        self.productos = ListaEnlazada()
    
    def agregarProducto(self, producto):
        self.productos.append(producto)
    