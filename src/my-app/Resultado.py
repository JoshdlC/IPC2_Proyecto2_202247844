from listaEnlazada import ListaEnlazada

class ResultadoM:
    def __init__(self, nombre, cantidadLineas):
        self.nombre = nombre
        self.cantidadLineas = cantidadLineas
        self.productos = ListaEnlazada()
        
    def agregarProducto(self, producto):
        self.productos.append(producto)
        
        
class ResultadoP:
    def __init__(self, nombre, cantidadComponentes, tiempoTotal):
        self.nombre = nombre
        self.cantidadComponentes = cantidadComponentes
        self.tiempoTotal = tiempoTotal
        

        
class Resultado:
    def __init__(self, data, lineas):
        self.data = data
        self.lineas = lineas
        
    def longitud(self):
        return len(self.lineas)
    
    def __str__(self):
        return self.dato + " " + str(self.lineas)
    
    def __repr__(self):
        return self.__str__()
    
    def obtenerInstrucciones(self):
        pendientes = ListaEnlazada()
        
        current = self.lineas.head
        while current:
            if current.data != "COMPLETED":
                pendientes.append(current.data)
            current = current.next
        return pendientes