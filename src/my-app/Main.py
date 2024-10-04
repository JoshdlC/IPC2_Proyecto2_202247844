from flask import Flask, render_template, url_for, request, redirect, session
import xml.etree.ElementTree as ET
import os
from werkzeug.utils import secure_filename

from listaEnlazada import ListaEnlazada
from Maquina import Maquina
from Producto import Producto
from Resultado import ResultadoP, ResultadoM, Resultado


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
            
            

def simularProducto(maquina, producto, tiempo):
    # resultados = ListaEnlazada() 
    # cantidadLineas = 0
    # tiempoTotal = 0
    
    # for maquinas in maquinasGlobal:
    #     if maquinas.nombre == maquina:
    instrucciones = ListaEnlazada()
    cantidadLineas = 0
    tiempoTotal = 0
    
    resultados = ListaEnlazada()
    
    xml_content = session['xml_content']
    root = ET.fromstring(xml_content)
        
    for maquinas in root.findall('Maquina'):
        nombre_maquina = maquinas.find('NombreMaquina').text
        if nombre_maquina == maquina:
            num_lineas = int(maquinas.find('CantidadLineasProduccion').text)
            tiempoTotal = int(maquinas.find('TiempoEnsamblaje').text)
            print(f"Máquina encontrada: {nombre_maquina} con {num_lineas} líneas de producción.")
            print(f"Tiempo de ensamblaje: {tiempoTotal}")

            for productos in maquinas.find('ListadoProductos').findall('Producto'):
                nombre_producto = productos.find('nombre').text
                if nombre_producto == producto:
                    elaboracion = productos.find('elaboracion').text.strip()
                    print(f"Producto encontrado: {nombre_producto} con elaboración: {elaboracion}")
                    # print(f"componentes: {productos.componentes}")
                    
                    
                    
                    instrucciones = ListaEnlazada()
                    step = ""
                    for char in elaboracion:
                        if char.isspace():
                            if step:
                                instrucciones.append(step)
                                step = ""                  
                        else:
                            step += char
                    if step:
                        instrucciones.append(step)
                        
                    brazo = ListaEnlazada()
                    
                    for _ in range(cantidadLineas):
                        brazo.append(0)
                        
                    segundo = 1
                    ensamblarLineas = ListaEnlazada()
                    
                    for _ in range(cantidadLineas):
                        ensamblarLineas.append(0)
                        
                    while True:
                        tiempoFila = Resultado(f"{segundo}", ListaEnlazada())
                        
                        for _ in range(cantidadLineas):
                            tiempoFila.lineas.append("No hacer nada")
                            
                        ensamblajeRealizado = False
                        ensamble = False
                        
                        for i in range(ensamblarLineas.longitud()):
                            if ensamblarLineas.obtener(i).data > 0:
                                ensamble = True
                                break
                            
                        for linea in range(cantidadLineas):
                            if ensamblarLineas.obtener(linea).data > 0:
                                tiempoFila.lineas.actualizar(linea, f"Ensamblar componente {brazo.obtener(linea).data}")
                                ensamblarLineas.obtener(linea).data -= 1
                                ensamble = True
                            else:
                                currentInstruction = None
                                
                                for i in range(instrucciones.longitud()):
                                    if instrucciones.obtener(i).data != "COMPLETED":
                                        data = instrucciones.obtener(i).data
                                        
                                        lineaInstruccion = " "
                                        compInstruccion = " "
                                        found_C = False
                                        #* Recorre la instrucción para obtener la línea y el componente
                                        for char in data[1: ]:
                                            if char == "C":
                                                found_C = True
                                            elif not found_C:
                                                lineaInstruccion += char
                                            else:
                                                compInstruccion += char 
                                                
                                        #* Convierte a entero
                                        lineaInstruccion = int(lineaInstruccion)
                                        compInstruccion = int(compInstruccion)
                                        
                                        #* Verifica si la línea es igual a la de la máquina
                                        if lineaInstruccion -1 == linea:
                                            currentInstruction = instrucciones.obtener(i)
                                            indexInstruction = i
                                            break
                                    
                                #* Si hay una instrucción    
                                if currentInstruction:
                                    data = currentInstruction.data
                                    componenteActual = " "
                                    found_C = False
                                    
                                    for char in data[1: ]:
                                        if char == "C":
                                            found_C = True
                                        elif not found_C:
                                            componenteActual += char
                                    #* Convierte a entero
                                    componenteActual = int(componenteActual)

                                    brazoActual = brazo.obtener(linea).data
                                    
                                    if ensamble and brazoActual == componenteActual:
                                        tiempoFila.lineas.actualizar(linea, "No hace nada")
                                    elif brazoActual < componenteActual:
                                        brazoActual += 1
                                        tiempoFila.lineas.actualizar(linea, f"Mover brazo - componente {brazoActual}")
                                        brazo.obtener(linea).data = brazoActual
                                        
                                    elif brazoActual > componenteActual:
                                        tiempoFila.lineas.actualizar(linea, f"No hace nada")
                                        
                                    elif brazoActual == componenteActual and not ensamblajeRealizado and not ensamble:
                                        #* verifica el turno
                                        canAssemble = True
                                        for j in range(indexInstruction):
                                            if instrucciones.obtener(j).data != "COMPLETED":
                                                canAssemble = False
                                                break
                                        
                                        if canAssemble:
                                            tiempoFila.lineas.actualizar(linea, f"Ensamblar componente {componenteActual}")
                                            instrucciones.obtener(indexInstruction).data = "COMPLETED"
                                            ensamblajeRealizado = True #* marca que se ensamblo
                                            ensamble = True #* marca que se esta ensamblando
                                            ensamblarLineas.obtener(linea).data = tiempoTotal - 1 #* establece el tiempo
                        
                        #* actualiza las lineas
                        if ensamblarLineas:
                            for linea in range(cantidadLineas):
                                if tiempoFila.lineas.obtener(linea).data == "No hacer nada":
                                    tiempoFila.lineas.actualizar(linea, "No hacer nada")
                                    
                        resultados.append(tiempoFila)
                        
                        allCompleted = True
                        for i in range(instrucciones.longitud()):
                            if instrucciones.obtener(i)!= "COMPLETED":
                                allCompleted = False
                                break
                        if allCompleted:
                            break
                        
                        if tiempo is not None and segundo >= tiempo:
                            break
                        
                        segundo += 1 #* incrementa el tiempo en 1 s
                    
                    #* se asegura q el últmo ensamblaje se haya registrado
                    if ensamblajeRealizado:
                        for linea in range(cantidadLineas):
                            if ensamblarLineas.obtener(linea).data == 0 and tiempoFila.lineas.obtener(linea).data.startswith("Ensamblar componente"):
                                ensamblarLineas.obtener(linea).data = tiempoTotal - 1
                        
                                    
                                    
                    
    tablasEnsamblaje.append((producto, resultados))  
    
    # session['resultados'] =
                    
    return instrucciones  # Retorna las instrucciones                    
                    
                    



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
                instrucciones = simularProducto(maquinaSeleccionada, producto.nombre, productoTiempo)

    return render_template(
        'reportes.html', 
        maquinas=maquinasGlobal, 
        productos=productos, 
        maquinaSeleccionada = maquinaSeleccionada, 
        instrucciones = instrucciones, 
        tablasEnsamblaje = tablasEnsamblaje
    )

@app.route('/producto_seleccionado', methods=['POST'])
def producto_seleccionado():
    productoMaquina = request.form.get('maquina')
    productoNombre = request.form.get('producto')
    productoTiempo = request.form.get('tiempo')
    
    #* valida el tiempo 
    if productoTiempo and productoTiempo.isdigit():
        productoTiempo = int(productoTiempo)
        session['productoTiempo'] = productoTiempo
    else:
        productoTiempo = None
    print(f"Nombre maquina: {productoMaquina}")
    print("si aparece nombre de maquina arriba ^^^^^, esta bien")
    #* crea lista de resultados
    
    instrucciones = ListaEnlazada()
    
    # print(f"Producto seleccionado: {productoNombre}")
    # print(f"Tiempo seleccionado: {productoTiempo}")
    
    # simularProducto(productoMaquina, productoNombre, productoTiempo)

        
    #* Crea lista de resultados
    if productoNombre and productoMaquina:
        print(f"Producto seleccionado: {productoNombre}")
        print(f"Tiempo seleccionado: {productoTiempo}")
        instrucciones = simularProducto(productoMaquina, productoNombre, productoTiempo)
    else:
        print("Faltan datos necesarios para simular el producto.")
        
    if instrucciones:
        tablasEnsamblaje.append((productoNombre, instrucciones))
    
    return redirect(url_for('reportes'))  # Redirigir después de procesar
    
@app.route('/reporte-html/<producto>', methods=['GET'])
def reporteEnHtml(producto):
    for tabla in tablasEnsamblaje:
        if tabla[0] == producto:
            return render_template('reporte.html', producto = producto, instrucciones = tabla[1])
    
    return redirect(url_for('reportes'))


    
    