class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class ListaEnlazada:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            actual = self.head
            while actual.next:
                actual = actual.next
            actual.next = new_node

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
        current = self.head
        contador = 0
        while current:
            contador += 1
            current = current.next
        return contador
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next

    def largo(self):
        if not self.head:
            return 0
        
        largo = 0
        current = self.head
        
        while True:
            largo += 1
            current = current.next
            if current == self.head:
                break
            
        return largo
    def actualizar(self, index, data):
        current = self.head
        contador = 0
        while current:
            if contador == index:
                current.data = data
                return
            contador += 1
            current = current.next

