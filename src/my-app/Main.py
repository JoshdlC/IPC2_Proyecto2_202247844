from flask import Flask, render_template, url_for, request, redirect, session, render_template_string, send_file, jsonify
import xml.etree.ElementTree as ET
import os
import graphviz
from werkzeug.utils import secure_filename


from listaEnlazada import ListaEnlazada
from Maquina import Maquina
from Producto import Producto
from Resultado import ResultadoP, ResultadoM, Resultado
from TiempoEnLinea import TiempoEnLinea



app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY = 'dev'
)

maquinasGlobal = ListaEnlazada()
productosGlobal = ListaEnlazada()
tablasEnsamblaje = ListaEnlazada()

def cargarArchivo(filePath):
    arbol = ET.parse(filePath)
    root = arbol.getroot()
    xml_content = ET.tostring(root).decode('utf-8')
    session['xml_content'] = xml_content
    print("Se cargo el archivo")   
    
    for maquinas in root.findall("Maquina"):
        nombreMaquina = maquinas.find("NombreMaquina").text.strip()
        cantidadLineas = int(maquinas.find("CantidadLineasProduccion").text.strip())
        cantidadComponentes = int(maquinas.find("CantidadComponentes").text.strip())
        tiempoProd = int(maquinas.find("TiempoEnsamblaje").text.strip())
        
        print(f"Nombre de la maquina: {nombreMaquina}")
        print(f"Cantidad de lineas de produccion: {cantidadLineas}")
        print(f"Cantidad de componentes: {cantidadComponentes}")
        print(f"Tiempo de ensamblaje: {tiempoProd}")
        
        #* Recorre y revisa si ya existe la maquina
        maquinaExistente = None
        nodoMaquina = maquinasGlobal.head
        while nodoMaquina != None:
            if nodoMaquina.data.nombre == nombreMaquina:
                maquinaExistente = nodoMaquina.data
                break
            nodoMaquina = nodoMaquina.next
            
        if maquinaExistente:
            maquina = maquinaExistente
        else:
            maquina = Maquina(nombreMaquina, cantidadLineas, cantidadComponentes, tiempoProd)
            maquinasGlobal.append(maquina)
        
        #* recorre los productos
        for producto in maquinas.find("ListadoProductos").findall("Producto"):
            nombreProducto = producto.find("nombre").text.strip()
        
            elaboracionProducto = producto.find("elaboracion").text.strip().split()
            print(f"Nombre del producto: {nombreProducto}")
            print(f"Elaboración de producto: {elaboracionProducto}")
            
            producto = Producto(nombreProducto)
            
            #* guarda los componentes
            for componente in elaboracionProducto:
                linea, numero = map(int, componente[1:].split('C'))
                producto.agregarComponentes(linea, numero)
                print(f"componente: {linea}, {numero}, {componente}")
                
            maquina.agregarProducto(producto)
            productosGlobal.append(producto)
            

def serializarLista(lista):
    resultado = "" 
    current = lista.head
    while current:
        resultado += current.data.data + ":"
        nodo = current.data.lineas.head
        while nodo:
            resultado += nodo.data
            if nodo.next:
                resultado += ","
                
            nodo = nodo.next
        resultado += "|"
        current = current.next
    return resultado.strip("|")

def deserializarLista(cadena):
    lista = ListaEnlazada()
    i = 0
    while i < len(cadena):
        dato = ""
        while i < len(cadena) and cadena[i] != ":": 
            dato += cadena[i]
            i += 1
        i += 1
        
        lineas = ListaEnlazada()
        linea = ""
        while i < len(cadena) and cadena[i] != "|":
            if cadena[i] == ",":
                lineas.append(linea)
                linea = ""
            else:
                linea += cadena[i]
            i += 1
         
        if linea:
            lineas.append(linea)
        i += 1
             
        resultado = Resultado(dato, lineas)
        lista.append(resultado)
    
    return lista

            


                    
def calcularTiempo(producto, cantidadLineas):
    tiempoLineas = ListaEnlazada()
    
    for i in range(cantidadLineas):
        tiempoLineas.append(TiempoEnLinea(i + 1))
        
    nodo = producto.componentes.head
    while nodo is not None:
        nodoTiempo = tiempoLineas.obtener(nodo.data.linea - 1)
        if nodoTiempo is None:
            raise ValueError("nodoTiempo is None, check the index.")
        if nodoTiempo.data is None:
            nodoTiempo.data = 0  # or some appropriate default before incrementing()
            
        nodo = nodo.next
        
    maxTiempo = 0
    nodoTiempo = tiempoLineas.head
    while nodoTiempo is not None:
        if nodoTiempo.data.tiempo > maxTiempo:
            maxTiempo = nodoTiempo.data.tiempo
        nodoTiempo = nodoTiempo.next
        
    return maxTiempo
      
def mostrarResultado(maquinas):
    resultados = ListaEnlazada()
    nodeMaquina = maquinas.head
    while nodeMaquina is not None:
        maquina = nodeMaquina.data
        maquinaInfo = ResultadoM(maquina.nombre, maquina.cantidadLineas)
        nodeProducto = maquina.productos.head
        while nodeProducto is not None:
            producto = nodeProducto.data
            tiempoTotal = calcularTiempo(producto, maquina.cantidadLineas)
            productoInfo = ResultadoP(producto.nombre, producto.componentes.longitud(), tiempoTotal)
            maquinaInfo.agregarProducto(productoInfo)
            nodeProducto = nodeProducto.next
        resultados.append(maquinaInfo)
        nodeMaquina = nodeMaquina.next
    return resultados
        
def imprimirResultado(resultados):
    nodeMaquina = resultados.head
    while nodeMaquina is not None:
        maquina = nodeMaquina.data
        print(f"Maquina: {maquina.nombre}")
        print(f"Cantidad lineas: {maquina.cantidadLineas}")
        nodeProducto = maquina.productos.head
        
        while nodeProducto is not None:
            producto = nodeProducto.data
            print(f"Producto: {producto.nombre}")
            print(f"Componentes: {producto.cantidadComponentes}")
            nodeProducto = nodeProducto.next
            
        nodeMaquina = nodeMaquina.next
    
def generarXmlSalida(maquinas):
    salidaSimulacion = ET.Element("SalidaSimulacion")
    
    #* iterar sobre las máquinas
    for maquina in maquinas:
        maquinaElement = ET.SubElement(salidaSimulacion, "Maquina")
        
        #* agrega el nombre de la maquina
        nombreElemento = ET.SubElement(maquinaElement, "Nombre")
        nombreElemento.text = maquina.nombre
        
        #* crea el listado de productos
        listadoProductosElemento = ET.SubElement(maquinaElement, "ListadoProductos")
        
        for producto in maquina.productos:
            productoElemento = ET.SubElement(listadoProductosElemento, "Producto")
            
            #* agrega el nombre del producto
            nombreProductoElemento = ET.SubElement(productoElemento, "Nombre")
            nombreProductoElemento.text = producto.nombre
            
            #* agregar tiempo 
            tiempoTotal = ET.SubElement(productoElemento, "TiempoTotal")
            tiempoTotal.text = str(producto.tiempoTotal)
            
            elaboracionElemento = ET.SubElement(productoElemento, "Elaboracion")
            
            for componente in producto.componentes:
                tiempoElemento = ET.SubElement(elaboracionElemento, "Tiempo", NoSegundo=str(componente.numero))
                lineaElemento = ET.SubElement(tiempoElemento, "LineaEnsamblaje", NoLinea=str(componente.linea))
                lineaElemento.text = f"Componente de línea {componente.linea} número {componente.numero}"

                
                

    #* Crear un árbol de ElementTree y escribirlo a un archivo
    tree = ET.ElementTree(salidaSimulacion)
    tree.write("C:\\Users\\josue\\Documents\\IPC2\\IPC2_Proyecto2_202247844\\src\\my-app\\salida.xml", encoding="utf-8", xml_declaration=True)
        
        

#* Filtros 
@app.add_template_filter
def today(date):
    return date.strftime('%d/%m/%Y')

@app.add_template_global
def repeat(text, times):
    return text * times

from datetime import datetime

@app.route('/', methods=['GET', 'POST'])
def index():
    print(url_for('index'))
    print(url_for('hello', name='Josue', age=21))
    print(url_for('code', code = 'print("Hello Worldsss")'))
    print(url_for('reportes'))

    name = None
    date = datetime.now()
    return render_template(
        'index.html', 
        name = name, 
        date =date,
        maquinas = maquinasGlobal,
        productos = productosGlobal
    )



@app.route('/hello')
@app.route('/hello/<name>')
@app.route('/hello/<name>/<int:age>')
@app.route('/hello/<name>/<int:age>/<email>')

def hello(name = None, age= None, email = None):
    my_data = {
        'name': name,
        'age': age,
        'email': email 
    }
    return render_template('hello.html', data = my_data)
    
from markupsafe import escape
@app.route('/code/<path:code>')
def code(code):
    return f'<code>El código es: {escape(code)}</code>'


#*Formulario wtf-forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Nombre de usuario: ', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña: ', validators=[DataRequired(), Length(min=6, max=30)])
    submit = SubmitField('Registrar:')


#*registrar usuario
@app.route('/auth/register', methods=['GET', 'POST'])   
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        return f"Nombre de usuario: {username}, Contraseña: {password}"
    
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    #     # email = request.form['email']
    #     if len(username) <= 25 and len(username) > 4 and len(password) >= 6 and len(password) <= 25:
    #         return f"Nombre de usuario: {username}, Contraseña: {password}"
    #     else:
    #         error = """"Nombre de usuario debe de tener entre 4 y 25 caracteres y
    #         la contraseña debe de tener entre 6 y 25 caracteres 
    #         """
    #         return render_template('auth/register.html', form = form, error=error)
    return render_template('auth/register.html', form = form)

# @app.route('/reportes')
# def reportes():
#     return render_template('reportes.html')

@app.route('/archivo', methods=['GET', 'POST'])
def archivo():
    global maquinasGlobal
    mensaje = None
    
    # * Crear carpeta para guardar los archivos
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        
        
    if request.method == 'POST':
        # Obtener los archivos cargados
        files = request.files.getlist('file')

        for file in files:
            if file:
                fileName = secure_filename(file.filename)
                filePath = os.path.join('uploads', fileName)
                file.save(filePath)
                
                cargarArchivo(filePath)
                mensaje = "Archivo cargado exitosamente."
                
                if maquinasGlobal.head != None:
                    print("Si hay maquinas")

    return render_template('archivo.html', maquinas = maquinasGlobal, mensaje = mensaje)



@app.route('/ayuda')
def ayuda():
    return render_template('ayuda.html')


@app.route('/reportes', methods=['GET', 'POST'])
def reportes():
    productos = None  #* Inicializa como None para manejar el caso de que no se seleccione ninguna máquina
    maquinaSeleccionada = None #* Inicializa como None para manejarel caso de que no se seleccione ninguna máquina
    instrucciones = ListaEnlazada()
    resultados = None
    
    
    if request.method == 'POST':
        maquina_nombre = request.form['maquina']
        maquinaSeleccionada = maquina_nombre

        #* Busca la máquina seleccionada
        nodoMaquina = maquinasGlobal.head
        while nodoMaquina is not None:
            if nodoMaquina.data.nombre == maquina_nombre:
                productos = nodoMaquina.data.productos  #* Obtener los productos de la máquina
                break
            nodoMaquina = nodoMaquina.next
            
    if 'productoTiempo' in session:
        productoTiempo = session['productoTiempo']
        
        if maquinaSeleccionada and request.method == 'POST' and productos:
            for producto in productos:
                resultados = mostrarResultado(maquinasGlobal)
                imprimirResultado(resultados)
                resultadosGlobal = resultados
                productos = productosGlobal

    
    
    return render_template(
        'reportes.html', 
        maquinas=maquinasGlobal, 
        resultados = resultados,
        productos=productos, 
        maquinaSeleccionada = maquinaSeleccionada, 
        instrucciones = instrucciones, 
        tablasEnsamblaje = tablasEnsamblaje
        
    )

@app.route('/producto_seleccionado', methods=['POST', 'GET'])
def producto_seleccionado():
    productoMaquina = request.form.get('maquina')
    productoNombre = request.form.get('producto')
    productoTiempo = request.form.get('tiempo')
    
    maquina_encontrada = None #* carga informacion de maquinas para obtener tiempo
    for maquina in maquinasGlobal: 
        if maquina.nombre == productoMaquina:
            maquina_encontrada = maquina
            break
        
    #* valida el tiempo, si no es ingresado usa el tiempo de la máquina
    if productoTiempo and productoTiempo.isdigit():
        productoTiempo = int(productoTiempo)
        session['productoTiempo'] = productoTiempo
    else:
        productoTiempo = maquina_encontrada.tiempoProd if maquina_encontrada else None
        
    if productoTiempo is None:
        return "No se ha ingresado un tiempo de simulación.", 400
        
    print(f"Nombre maquina: {productoMaquina}")
    print("si aparece nombre de maquina arriba ^^^^^, esta bien")
    #* crea lista de resultados
    resultados = ListaEnlazada()
    instrucciones = ListaEnlazada()
    
    
    xml_content = session['xml_content']
    root = ET.fromstring(xml_content)

    cantidadLineas = 0  #* Inicializar cantidadLineas
    tiempo_ensamblaje = 0  #* Inicializar tiempo de ensamblaje
    for maquina in root.findall('Maquina'):
        nombreMaquina = maquina.find('NombreMaquina').text
        if nombreMaquina == productoMaquina:
            cantidadLineas = int(maquina.find('CantidadLineasProduccion').text)
            tiempo_ensamblaje = int(maquina.find('TiempoEnsamblaje').text)
            print(f"Máquina encontrada: {nombreMaquina} con {cantidadLineas} líneas de producción.")
            print(f"Tiempo de ensamblaje: {tiempo_ensamblaje}")

            for producto in maquina.find('ListadoProductos').findall('Producto'):
                nombre_producto = producto.find('nombre').text
                if nombre_producto == productoNombre:
                    elaboracion = producto.find('elaboracion').text.strip()
                    print(f"Producto encontrado: {nombre_producto} con elaboración: {elaboracion}")
                    
                    # Extraer las instrucciones correctamente sin usar split
                    instrucciones = ListaEnlazada()
                    paso = ""
                    for char in elaboracion:
                        if char.isspace():
                            if paso:
                                instrucciones.append(paso)
                                paso = ""
                        else:
                            paso += char
                    if paso:
                        instrucciones.append(paso)
                                
                    brazo = ListaEnlazada()
                    for _ in range(cantidadLineas):
                        brazo.append(0)
                    
                    segundo = 1
                    ensamblando_lineas = ListaEnlazada()  #* se inicializa el ensamble
                    for _ in range(cantidadLineas):
                        ensamblando_lineas.append(0)
                    
                    while True:
                        filaTiempo = Resultado(f"{segundo}", ListaEnlazada())
                        for _ in range(cantidadLineas):
                            filaTiempo.lineas.append("No hacer nada")
                        
                        ensamblaje_realizado = False
                        ensamblando = False
                        for i in range(ensamblando_lineas.longitud()):
                            if ensamblando_lineas.obtener(i).data > 0:
                                ensamblando = True
                                break
                        
                        for linea in range(cantidadLineas):
                            if ensamblando_lineas.obtener(linea).data > 0:
                                filaTiempo.lineas.actualizar(linea, f"Ensamblar componente {brazo.obtener(linea).data}")
                                ensamblando_lineas.obtener(linea).data -= 1
                                ensamblando = True
                            else:
                                instruccion_actual = None
                                for i in range(instrucciones.longitud()):
                                    if instrucciones.obtener(i).data != "COMPLETED":
                                        dato = instrucciones.obtener(i).data
                                        linea_instruccion = ""
                                        componente_instruccion = ""
                                        found_C = False
                                        for char in dato[1:]:
                                            if char == 'C':
                                                found_C = True
                                            elif not found_C:
                                                linea_instruccion += char
                                            else:
                                                componente_instruccion += char
                                        linea_instruccion = int(linea_instruccion)
                                        componente_instruccion = int(componente_instruccion)
                                        if linea_instruccion - 1 == linea:
                                            instruccion_actual = instrucciones.obtener(i)
                                            instruccion_index = i
                                            break
                                
                                if instruccion_actual:
                                    dato = instruccion_actual.data
                                    componente_actual = ""
                                    found_C = False
                                    for char in dato[1:]:
                                        if char == 'C':
                                            found_C = True
                                        elif found_C:
                                            componente_actual += char
                                    componente_actual = int(componente_actual)
                                    brazoActual = brazo.obtener(linea).data
                                    
                                    if ensamblando and brazoActual == componente_actual:
                                        filaTiempo.lineas.actualizar(linea, "No hace nada")
                                    elif brazoActual < componente_actual:
                                        brazoActual += 1
                                        filaTiempo.lineas.actualizar(linea, f"Mover brazo – componente {brazoActual}")
                                        brazo.obtener(linea).data = brazoActual
                                    elif brazoActual > componente_actual:
                                        
                                        filaTiempo.lineas.actualizar(linea, "No hace nada")
                                    elif brazoActual == componente_actual and not ensamblaje_realizado and not ensamblando:
                                        #* verifica el turno de la instruccion
                                        can_assemble = True
                                        for j in range(instruccion_index):
                                            if instrucciones.obtener(j).data != "COMPLETED":
                                                can_assemble = False
                                                break
                                        
                                        if can_assemble:
                                            filaTiempo.lineas.actualizar(linea, f"Ensamblar componente {componente_actual}")
                                            instrucciones.obtener(instruccion_index).data = "COMPLETED"
                                            ensamblaje_realizado = True
                                            ensamblando = True  #* marca q una linea esta ensamblandose
                                            ensamblando_lineas.obtener(linea).data = tiempo_ensamblaje - 1  #* establece la linea
                        
                        #* si no se esta ensamblando, se marca como no hacer nada
                        if ensamblando:
                            for linea in range(cantidadLineas):
                                if filaTiempo.lineas.obtener(linea).data == "No hacer nada":
                                    filaTiempo.lineas.actualizar(linea, "No hace nada")
                        
                        resultados.append(filaTiempo)
                        
                        all_completed = True
                        for i in range(instrucciones.longitud()):
                            if instrucciones.obtener(i).data != "COMPLETED":
                                all_completed = False
                                break
                        
                        if all_completed:
                            break
                        
                        if productoTiempo is not None and segundo >= productoTiempo:
                            break
                        
                        segundo += 1  #* incrementar el tiempo en 1 segundo

                    #* Asegurarse de que el último componente también reciba el tiempo de ensamblaje
                    if ensamblaje_realizado:
                        for linea in range(cantidadLineas):
                            if ensamblando_lineas.obtener(linea).data == 0 and filaTiempo.lineas.obtener(linea).data.startswith("Ensamblar componente"):
                                ensamblando_lineas.obtener(linea).data = tiempo_ensamblaje - 1

    # # Mostrar los pasos de la simulación en la consola
    # print("Pasos de la simulación:")
    # current = resultados.head
    # while current:
    #     print(current.data)
    #     current = current.next

    # # Imprimir las instrucciones pendientes en consola
    # print("Instrucciones pendientes en cada segundo:")
    # current = resultados.head
    # while current:
    #     pendientes = ListaEnlazada()
    #     nodo_instruccion = instrucciones.head
    #     while nodo_instruccion:
    #         if nodo_instruccion.data != "COMPLETED":
    #             pendientes.append(nodo_instruccion.data)
    #         nodo_instruccion = nodo_instruccion.next
    #     if pendientes.longitud() > 0:
    #         print(f"Segundo {current.data.data}: {pendientes}")
    #     current = current.next

    #* Agregar la tabla de ensamblaje a la lista de tablas
    tablasEnsamblaje.append((productoNombre, resultados))

    #* Serializa los resultados y almacenarlos en la sesión
    session['resultados'] = serializarLista(resultados)

    print("Simulación completada. Resultados generados.")
    return render_template('reportes.html', productos=productosGlobal, resultados=resultados, maquinas=maquinasGlobal, num_lineas=cantidadLineas, tablas_ensamblaje=tablasEnsamblaje)
    
    
    
@app.route('/reporteProductos/<productoSeleccionado>', methods=['GET'])
def reporteProductos(productoSeleccionado):
    
    print(f"Producto seleccionado: {productoSeleccionado}")

    # Inicializa 'html_content' para asegurarte de que siempre esté definido
    html_content = ""

    for nombreProd, resultados in tablasEnsamblaje:
        if nombreProd == productoSeleccionado:
            # Genera el contenido HTML
            html_content = f"""
            <html>
            <head>
                <title>Reporte de Ensamblaje</title>
                <style>
                    body {{
                        font-family: 'Helvetica Neue', Arial, sans-serif;
                        background-color: #f4f7f6;
                        color: #333;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: auto;
                        margin: 0;
                    }}
                    .container {{
                        background-color: #ffffff;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        max-width: 1000px;
                        width: 100%;
                        margin: 20px;
                        height: auto;
                    }}
                    h1 {{
                        text-align: center;
                        color: #2c3e50;
                        font-size: 26px;
                        margin-top: 30px;
                        margin-bottom: 30px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                        font-size: 16px;
                    }}
                    th, td {{
                        padding: 12px 15px;
                        text-align: center;
                        border-bottom: 1px solid #e1e1e1;
                        border: 1px solid #e1e1e1;
                        
                    }}
                    th {{
                        background-color: #3498db;
                        color: white;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                    }}
                    tr:hover {{
                        background-color: #e6f7ff;
                    }}
                    td {{
                        color: #555;
                    }}
                    .no-data {{
                        text-align: center;
                        padding: 20px;
                        font-size: 18px;
                        color: #999;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Reporte de Ensamblaje para el producto: {productoSeleccionado}</h1>
                    <table>
                        <tr><th>Tiempo</th>"""

            # Si hay resultados, genera la tabla de ensamblaje
            if resultados.head:
                primeraFila = resultados.head.data
                for i in range(primeraFila.lineas.longitud()):
                    html_content += f"<th>Línea de Ensamblaje {i + 1}</th>"
                html_content += "</tr>"

                # Añadir filas de resultados del ensamblaje
                current = resultados.head
                while current:
                    html_content += f"<tr><td>{current.data.data}</td>"
                    for i in range(current.data.lineas.longitud()):
                        html_content += f"<td>{current.data.lineas.obtener(i).data}</td>"
                    html_content += "</tr>"
                    current = current.next
            else:
                # Si no hay datos disponibles, agrega un mensaje de fin de tabla
                html_content += """
                <tr>
                    <td colspan="100%">Fin de la tabla.</td>
                </tr>"""

            # Cerrar el HTML
            html_content += """
                    </table>
                </div>
            </body>
            </html>
            """
            print (html_content)
            # Devolver el HTML generado directamente
            return render_template_string(html_content)

    # Si no se encuentra el producto, mostrar una página de error
    return "<h1>Producto no encontrado</h1>", 404


@app.route('/generarTda', methods=['GET'])
def generarTda():
    productoMaquina = request.args.get('maquina')
    productoNombre = request.args.get('producto')
    
    
    
    print(f"Producto seleccionado: {productoNombre} de la máquina {productoMaquina}")
    
    xml_content = session['xml_content']
    if not xml_content:
        return "No se ha cargado un archivo XML.", 400
    
    root = ET.fromstring(xml_content)
    
    for maquina in root.findall('Maquina'):
        nombreMaquina = maquina.find('NombreMaquina').text
        if nombreMaquina == productoMaquina:
            cantidadLineas = int(maquina.find('CantidadLineasProduccion').text)
            tiempo_ensamblaje = int(maquina.find('TiempoEnsamblaje').text)
            print(f"Máquina encontrada: {nombreMaquina} con {cantidadLineas} líneas de producción.")
            print(f"Tiempo de ensamblaje: {tiempo_ensamblaje}")

            for producto in maquina.find('ListadoProductos').findall('Producto'):
                nombre_producto = producto.find('nombre').text
                if nombre_producto == productoNombre:
                    elaboracion = producto.find('elaboracion').text.strip()
                    
                    dot = graphviz.Digraph(comment='Diagrama de ensamblaje')
                    
                    #* añade los nodos
                    pasos = elaboracion.split()
                    prePasoLabel = None
                    
                    for paso in pasos:
                        if paso.startswith('L') and 'C' in paso:
                            paso_label = paso
                            dot.node(paso_label, label=paso_label)
                            if prePasoLabel:
                                dot.edge(prePasoLabel, paso_label)
                            prePasoLabel = paso_label
                        else:
                            if prePasoLabel:
                                dot.node(paso, label=paso)
                                dot.edge(prePasoLabel, paso)
                                prePasoLabel = paso
                                
                    # * genera el gráfico
                    graph_path = 'static/grafico_tda'
                    dot.render(graph_path, format='png')
                    
                    return f"Gráfico generado: <img src='/{graph_path}.png' alt='Grafico de TDA'>"
    
    return "No se encontró la máquina o el producto especificado.", 400
                    
                    
@app.route('/generarXml', methods=['GET'])
def generarXml():
    maquinas = maquinasGlobal
    
    xml_path =  os.path.join(os.getcwd(), 'C:\\Users\\josue\\Documents\\IPC2\\IPC2_Proyecto2_202247844\\src\\my-app\\salida.xml')
    generarXmlSalida(maquinas)
    
    if os.path.exists(xml_path):
        return send_file(xml_path, as_attachment=True, download_name="salida.xml")
    else:
        return jsonify({"error": "El archivo no fue encontrado"}), 404
    
    #* Devuelve el archivo XML generado ^^^^
