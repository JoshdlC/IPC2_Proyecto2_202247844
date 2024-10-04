from listaEnlazada import ListaEnlazada

class Maquina:
    def __init__(self, nombre, lineas, cantidadComponentes, tiempoProd):
        self.nombre = nombre
        self.lineas = lineas
        self.cantidadComponentes = cantidadComponentes
        self.tiempoProd = tiempoProd
        self.productos = ListaEnlazada()
    
    def agregarProducto(self, producto):
        self.productos.append(producto)
    