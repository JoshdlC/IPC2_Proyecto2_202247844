class TiempoEnLinea:
    def __init__(self, linea):
        self.linea = linea
        self.tiempo = 0
        self.data = 0
        
    def incrementarT(self):
        self.tiempo += 1