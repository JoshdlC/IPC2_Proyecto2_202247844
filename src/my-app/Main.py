from flask import Flask, render_template, url_for, request
import xml.etree.ElementTree as ET
import os
from werkzeug.utils import secure_filename

from listaEnlazada import ListaEnlazada
from Maquina import Maquina
from Producto import Producto


app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY = 'dev'
)

maquinasGlobal = ListaEnlazada()

def cargarArchivo(filePath):
    arbol = ET.parse(filePath)
    root = arbol.getroot()
    print("Se cargo el archivo")            
    

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

                



    return render_template('archivo.html', maquinas = maquinasGlobal, mensaje = mensaje)