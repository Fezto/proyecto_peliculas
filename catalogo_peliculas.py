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
    password="tu_contraseña",
    database="tu_db"
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


def agregar_pelicula(pelicula, duracion, año):
    consulta = "INSERT INTO peliculas (nombre, duracion, año) VALUES (%s, %s, %s)"
    datos_pelicula = (pelicula, duracion, año)
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

@app.route("/", methods=['POST', 'GET'])
def home():
    if (is_user_logged_in()):
        peliculas = obtener_peliculas()
        return render_template('dashboard.html', peliculas=peliculas, total_peliculas=len(peliculas))
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_user(request.form['username'])
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)


@app.route("/registro", methods=["POST", "GET"])
def registro_usuario():
    error = None
    if request.method == 'POST':
        if registro(request.form['usuario'], request.form['contraseña']):
            return redirect(url_for('home'))
        else:
            error = 'Error al registrar usuario'
    return render_template('registro.html', error=error)


@app.route("/agregar_pelicula", methods=['POST', 'GET'])
def agregarPelicula():
    if (not is_user_logged_in()):
        abort(403)
    if request.method == 'GET':
        pelicula = {}  # Define your pelicula object here
        return render_template('agregarPelicula.html', pelicula=pelicula)
    if request.method == 'POST':
        agregar_pelicula(
            request.form['pelicula'], request.form['duracion'], request.form['año'])
    return redirect(url_for('home'))


@app.route("/editar_pelicula/<id_pelicula>", methods=['POST', 'GET'])
def editarPelicula(id_pelicula):
    if request.method == 'GET':
        # Buscar la película en la base de datos
        cursor.execute(
            "SELECT * FROM peliculas WHERE id_pelicula = %s", (id_pelicula,))
        pelicula = cursor.fetchone()
        if pelicula is None:
            abort(404)  # Si no se encuentra la película, devolver un error 404
        # Renderizar la plantilla, pasando la película como un argumento
        return render_template('editarPelicula.html', pelicula=pelicula)
    if request.method == 'POST':
        # Tomar los datos del formulario de la solicitud
        nuevo_nombre = request.form['pelicula']
        nueva_duracion = request.form['duracion']
        nuevo_año = request.form['año']
        # Actualizar la película en la base de datos
        cursor.execute("UPDATE peliculas SET nombre = %s, duracion = %s, año = %s WHERE id_pelicula = %s",
                       (nuevo_nombre, nueva_duracion, nuevo_año, id_pelicula))
        db_connection.commit()
        # Redirigir al usuario a la página de inicio
        return redirect(url_for('home'))


@app.route("/eliminar_pelicula", methods=['POST'])
def eliminarPelicula():
    if not is_user_logged_in():
        abort(403)
    id_pelicula = request.form['id_pelicula']
    eliminar_pelicula(id_pelicula)
    return redirect(url_for('home'))

#! Funciones para checar las credenciales del login


def log_user(username):
    resp = make_response(redirect(url_for('home')))
    maxAge = 60 * 60
    resp.set_cookie('session_token', '123', max_age=maxAge)
    return resp


def is_user_logged_in():
    return request.cookies.get('session_token')


def valid_login(username, password):
    return username == "admin" and password == "admin"
