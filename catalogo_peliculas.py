from flask import Flask
from flask import render_template
from flask import request
from flask import abort, redirect, url_for
from flask import make_response
import mysql.connector

#! Ingreso a la base de datos

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Spongebob400!",
    database="pelis"
)

#! Creación de un cursor, un "apuntador" que sirve para ejecutar los
#! comandos de SQL

cursor = db_connection.cursor(dictionary=True)

app = Flask(__name__)

#! Funciones que hacen las propias consultas SQL.


def registro(usuario, contraseña):

    cuenta = "INSERT INTO usuarios (Nombre_usuario, Contraseña) VALUES (%s, %s)"
    datos_usuario = (usuario, contraseña)
    cursor.execute(cuenta, datos_usuario)
    db_connection.commit()
    return True


def obtener_peliculas():
    cursor.execute("SELECT * FROM peliculas")
    peliculas = cursor.fetchall()
    return peliculas


def agregar_pelicula(nombre, duracion, año):
    consulta = "INSERT INTO peliculas (nombre, duracion, año) VALUES (%s, %s, %s)"
    datos_pelicula = (nombre, duracion, año)
    cursor.execute(consulta, datos_pelicula)
    db_connection.commit()
    return True


def editar_pelicula(id_pelicula, nuevo_nombre, nueva_duracion, nuevo_año):
    consulta = "UPDATE peliculas SET nombre = %s, duracion = %s, año = %s WHERE id_pelicula = %s"
    datos_pelicula = (nuevo_nombre, nueva_duracion, nuevo_año, id_pelicula)
    cursor.execute(consulta, datos_pelicula)
    db_connection.commit()
    return True


def eliminar_pelicula(id_pelicula):
    borrar = "DELETE FROM peliculas WHERE id_pelicula=%s"
    datos_pelicula = (id_pelicula, )
    cursor.execute(borrar, datos_pelicula)
    db_connection.commit()
    return True


#! Definición de rutas. Esto es lo que se llama directamente desde los botones
#! dentro de dashboard.html y es lo que abre las páginas para la inserción de datos

# * Esta es la ruta base, por lo que es el cual está la página por defecto. En si es el dashboard.

@app.route("/", methods=['POST', 'GET'])
def home():
    error = None
    # Tráeme el dashboard, por favor
    if request.method == 'GET':
        if (is_user_logged_in()):
            peliculas = obtener_peliculas()
            return render_template('dashboard.html', peliculas=peliculas, total_peliculas=len(peliculas))
        else:
            error = "¡No existe un usuario logeado!"
            return render_template('login.html', error=error)

    # Hey, te estoy enviando mis credenciales antes de acceder para iniciar sesión ¿Son correctas?
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            return log_user()
        else:
            error = '¡Username o contraseña inválido!'
            return render_template('login.html', error=error)


# * Esta es la ruta que atende al login.

@app.route("/registro", methods=["POST", "GET"])
def registro_usuario():
    error = None

    # Tráeme la página de registro, 0 restricciones, 0 miedo!
    if request.method == 'GET':
        return render_template('registro.html', error=error)
    
    # Ya te envie mis datos de registro de nuvo usuario, generalo!
    if request.method == 'POST':
        if registro(request.form['usuario'], request.form['contraseña']):
            return redirect(url_for('home'))
        else:
            error = 'Error al registrar usuario'


#* Esta es la ruta que se encarga propiamete de agregar películas

@app.route("/agregar_pelicula", methods=['POST', 'GET'])
def agregarPelicula():
    if (not is_user_logged_in()):
        abort(403)

    # Enviame a la página de inserción de una nueva película!
    if request.method == 'GET':
        pelicula = {}  
        return render_template('agregarPelicula.html', pelicula=pelicula)
    
    # Una vez insertados los datos, crea una nueva película, insértala y redirígeme de vuelta al dashboard
    if request.method == 'POST':
        agregar_pelicula(request.form['pelicula'], request.form['duracion'], request.form['año'])
        return redirect(url_for('home'))


@app.route("/editar_pelicula/<id_pelicula>", methods=['POST', 'GET'])
def editarPelicula(id_pelicula):

    # Quiero acceder a la ventana de edición! Busca la película y luego muestra la página.
    if request.method == 'GET':
        cursor.execute(
            "SELECT * FROM peliculas WHERE id_pelicula = %s", (id_pelicula,))
        pelicula = cursor.fetchone()    #
        if pelicula is None:
            abort(404)
        return render_template('editarPelicula.html', pelicula=pelicula)
    
    # Ya que termine de insertar los datos de edición, edita la película existente
    if request.method == 'POST':
        editar_pelicula(id_pelicula, request.form['pelicula'], request.form['duracion'], request.form['año'])
        return redirect(url_for('home'))


@app.route("/eliminar_pelicula", methods=['POST'])
def eliminarPelicula():
    if not is_user_logged_in():
        abort(403)
    id_pelicula = request.form['id_pelicula']
    eliminar_pelicula(id_pelicula)
    return redirect(url_for('home'))


#! Funciones para checar las credenciales del login

# * Finaliza el proceso de ingreso del usuario y establece una cookie
def log_user():
    resp = make_response(redirect(url_for('home')))
    maxAge = 60 * 60
    resp.set_cookie('session_token', '123', max_age=maxAge)
    return resp

# * Verifica si el usuario sigue estando logeado dentro de su sesión


def is_user_logged_in():
    return request.cookies.get('session_token')

# * Verifica si el usuario y la contraseña proporcionadas son correctas


def valid_login(username, password):
    return username == "admin" and password == "admin"
