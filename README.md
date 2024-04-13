# Guía de Instalación del Proyecto

Este proyecto es una aplicación Flask que utiliza MySQL para las operaciones de base de datos. Sigue los pasos a continuación para configurar el proyecto en tu máquina local.

## Prerrequisitos

- Python 3.7 o superior
- pip (instalador de paquetes de Python)
- Servidor MySQL

## Pasos

1. Clona el repositorio en tu máquina local.

2. Navega al directorio del proyecto en tu terminal e importa la base de datos en Workbench.

3. Configura un entorno virtual:

```sh
python -m venv env
```

4. Activa el entorno virtual:
```sh
.\env\Scripts\activate
```

5. Instala los paquetes de Python requeridos (importante!): 
```sh
pip install -r requirements.txt
```

6. Actualiza los detalles de conexión a la base de datos en ´catalogo_peliculas.py´
```sh
db_connection = mysql.connector.connect(
    host="localhost",
    user="tu_usuario",              // por lo general es root
    password="tu_contraseña",
    database="tu_base_de_datos"     // el nombre de tu schema en Workbench
)
```

7. Ejecuta la aplicación de Flask, hooray!
```sh
flask --app catalogo_peliculas.py run
```

8. Ingresa a la base de datos poniendo "admin" como usuario y "admin" como contraseña
