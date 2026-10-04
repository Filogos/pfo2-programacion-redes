from pathlib import Path
import secrets
import sqlite3

from flask import Flask, jsonify, request, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

BASE_DATOS = Path(__file__).resolve().parent / "usuarios.db"


def conectar():
    conexion = sqlite3.connect(BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():
    with conectar() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)


@app.post("/registro")
def registro():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify(error="Debés enviar un objeto JSON."), 400

    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")

    if not isinstance(usuario, str) or not isinstance(contraseña, str):
        return jsonify(error="Usuario y contraseña deben ser textos."), 400

    usuario = usuario.strip()

    if not usuario or not contraseña.strip():
        return jsonify(error="Usuario y contraseña son obligatorios."), 400

    password_hash = generate_password_hash(contraseña)

    try:
        with conectar() as conexion:
            conexion.execute(
                "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
                (usuario, password_hash)
            )
    except sqlite3.IntegrityError:
        return jsonify(error="El usuario ya existe."), 409

    return jsonify(mensaje="Usuario registrado correctamente."), 201


@app.post("/login")
def login():
    # Evita conservar una sesión anterior si el nuevo login falla.
    session.clear()
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify(error="Debés enviar un objeto JSON."), 400

    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")

    if not isinstance(usuario, str) or not isinstance(contraseña, str):
        return jsonify(error="Usuario y contraseña deben ser textos."), 400

    with conectar() as conexion:
        registrado = conexion.execute(
            "SELECT * FROM usuarios WHERE usuario = ?",
            (usuario.strip(),)
        ).fetchone()

    if registrado is None or not check_password_hash(
        registrado["password_hash"], contraseña
    ):
        return jsonify(error="Usuario o contraseña incorrectos."), 401

    session["usuario"] = registrado["usuario"]
    return jsonify(mensaje="Inicio de sesión exitoso."), 200


@app.get("/tareas")
def tareas():
    if "usuario" not in session:
        return jsonify(error="Primero debés iniciar sesión."), 401

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Sistema de gestión de tareas</title>
        </head>
        <body>
            <h1>Bienvenido/a, {{ usuario }}</h1>
            <p>Accediste correctamente al sistema de gestión de tareas.</p>
        </body>
        </html>
    """, usuario=session["usuario"])


crear_tablas()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)