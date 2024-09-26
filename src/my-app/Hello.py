from flask import Flask, render_template, url_for, request
import xml.etree.ElementTree as ET
import os
from listaEnlazada import ListaEnlazada

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY = 'dev'
)

maquinas = ListaEnlazada()


#* Filtros 
@app.add_template_filter
def today(date):
    return date.strftime('%d/%m/%Y')

@app.add_template_global
def repeat(text, times):
    return text * times

# @app.add_template_global(repeat, 'repeat')



from datetime import datetime

@app.route('/')
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

@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

@app.route('/archivo', methods=['GET', 'POST'])
def archivo():
    global maquinas
    
    if request.method == 'POST':
        # Obtener los archivos cargados
        files = request.files.getlist('file')

        for file in files:
            if file:
                # Guardar el archivo en un lugar temporal
                file_path = os.path.join('uploads', file.filename)
                file.save(file_path)
                
                # Parsear el archivo XML
                arbol = ET.parse(file_path)
                root = arbol.getroot()
                
                for maquina in root.findall('Maquina'):
                    nombre_maquina = maquina.find('NombreMaquina').text
                    cantidad_lineas = int(maquina.find('CantidadLineasProduccion').text)
                    cantidad_componentes = int(maquina.find('CantidadComponentes').text)
                    tiempo_ensamblaje = int(maquina.find('TiempoEnsamblaje').text)

                    # Verificar si la máquina ya existe
                    maquina_existente = next((m for m in maquinas if m['nombre'] == nombre_maquina), None)

                    if maquina_existente:
                        # Actualizar la máquina existente
                        maquina_existente['lineas'] += cantidad_lineas
                        maquina_existente['componentes'] += cantidad_componentes
                        maquina_existente['tiempo'] = max(maquina_existente['tiempo'], tiempo_ensamblaje)
                    else:
                        # Crear una nueva máquina
                        nueva_maquina = {
                            'nombre': nombre_maquina,
                            'lineas': cantidad_lineas,
                            'componentes': cantidad_componentes,
                            'tiempo': tiempo_ensamblaje,
                            'productos': []
                        }
                        maquinas.append(nueva_maquina)

                    # Añadir productos
                    for producto in maquina.find('ListadoProductos'):
                        nombre_producto = producto.find('nombre').text
                        elaboracion = producto.find('elaboracion').text.strip()
                        nueva_maquina['productos'].append({'nombre': nombre_producto, 'elaboracion': elaboracion})



    return render_template('archivo.html', maquinas = maquinas)