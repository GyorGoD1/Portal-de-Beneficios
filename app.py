from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import pandas as pd

# Configuración inicial
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configurar la base de datos
def init_db():
    conn = sqlite3.connect('gimnasio.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut_completo TEXT UNIQUE,
            nombre TEXT,
            paterno TEXT,
            materno TEXT,
            fecha_nacimiento TEXT,
            edad INTEGER,
            direccion TEXT,
            tipo_vecino TEXT
        )
    ''')
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS beneficios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condicion TEXT,
            descripcion TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Cargar datos desde el archivo Excel a la base de datos
def cargar_datos_excel():
    archivo_excel = 'datos/Datos prueba.xlsx'
    # Cargar la hoja de usuarios
    df_usuarios = pd.read_excel(archivo_excel, sheet_name='usuarios')  # Verifica que la hoja se llame 'usuarios'

    # Verifica los nombres de las columnas antes de usar los valores
    print(df_usuarios.columns)  # Esto imprimirá las columnas para que puedas ver sus nombres reales

    # Convierte las fechas a formato adecuado
    df_usuarios['fecha_nacimiento'] = pd.to_datetime(df_usuarios['fecha_nacimiento'], errors='coerce').dt.strftime('%Y-%m-%d')

    conn = sqlite3.connect('gimnasio.db')
    cursor = conn.cursor()

    # Insertar datos de usuarios
    for _, row in df_usuarios.iterrows():
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (rut_completo, nombre, paterno, materno, fecha_nacimiento, edad, direccion, tipo_vecino)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['rut_completo'], row['nombre'], row['paterno'], row['materno'], row['fecha_nacimiento'], row['edad'], row['direccion'], row['tipo_vecino']))

    conn.commit()
    conn.close()

# Ruta principal para verificar beneficios
@app.route('/')
def index():
    return render_template('index.html')

# API para validar datos y mostrar beneficios
@app.route('/validar', methods=['POST'])
def validar():
    rut = request.form['rut']
    conn = sqlite3.connect('gimnasio.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE rut_completo = ?", (rut,))
    usuario = cursor.fetchone()

    if usuario:
        # Aplicar lógica de beneficios según criterios de edad y tipo de vecino
        edad = usuario[6]  # Columna 'edad' de la tabla usuarios
        tipo_vecino = usuario[8]  # Columna 'tipo_vecino'

        # Aquí deberías implementar la lógica para verificar los beneficios
        # A continuación, un ejemplo básico de cómo podrías hacerlo

        beneficios_aplicables = []

        if edad >= 65:
            beneficios_aplicables.append("1 semana gratis al mes")
        if tipo_vecino == 'Vitacura':
            beneficios_aplicables.append("2 semanas gratis al mes y 1 bebida isotónica")

        # Puedes añadir más lógica de beneficios según los criterios definidos

        conn.close()
        return jsonify({"estado": "ok", "beneficios": beneficios_aplicables})
    else:
        conn.close()
        return jsonify({"estado": "error", "mensaje": "RUT no encontrado"})

# API para registrar nuevos usuarios
@app.route('/registrar', methods=['POST'])
def registrar():
    # Recibir los datos desde el formulario (sin archivos)
    rut = request.form['rut']
    nombre = request.form['nombre']
    paterno = request.form['paterno']
    materno = request.form['materno']
    fecha_nacimiento = request.form['fecha_nacimiento']
    edad = request.form['edad']
    direccion = request.form['direccion']
    tipo_vecino = request.form['tipo_vecino']

    # Insertar los datos del nuevo usuario en la base de datos
    try:
        conn = sqlite3.connect('gimnasio.db')
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO usuarios (rut_completo, nombre, paterno, materno, fecha_nacimiento, edad, direccion, tipo_vecino)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (rut, nombre, paterno, materno, fecha_nacimiento, edad, direccion, tipo_vecino))
        conn.commit()
        conn.close()
        return jsonify({"estado": "ok", "mensaje": "Usuario registrado exitosamente"})
    except sqlite3.IntegrityError:
        return jsonify({"estado": "error", "mensaje": "RUT ya registrado"})

# Inicializar base de datos si no existe
if __name__ == '__main__':
    init_db()
    cargar_datos_excel()
    app.run(debug=True)
