from flask import Flask, render_template, url_for, request


app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY = 'dev'
)

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
    friends = ['Juan', 'Pedro', 'Luis', 'Carlos', 'Ana']	
    name = 'Josh'
    date = datetime.now()
    return render_template(
        'index.html', 
        name = name, 
        friends = friends, 
        date =date,
    )


#string
#int
#float
#path
#uuid
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