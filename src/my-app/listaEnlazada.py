class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class ListaEnlazada:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.cabeza:
            self.cabeza = new_node
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = new_node
        self._longitud += 1

    def obtener(self, index):
        current = self.head
        contador = 0
        while current:
            if contador == index:
                return current.data
            contador += 1
            current = current.next

        return None
    
    def longitud(self):
        return self._longitud
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next


