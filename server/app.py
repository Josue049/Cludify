import sqlite3
import hashlib
import os
import random
from flask import Flask, render_template, url_for, jsonify, request, redirect, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Genera una clave secreta aleatoria


# Rutas de las carpetas
VIDEO_FOLDER = os.path.join("static", "videosFinal")
ANUNCIOS_FOLDER = os.path.join("static", "anuncios")
LINKS_FOLDER = os.path.join("static", "links")

# Generar una lista de números en orden aleatorio
video_indices = list(range(1, 51))
random.shuffle(video_indices)

# Control de los videos y anuncios ya enviados
videos_enviados = []

def obtener_videos_anuncios_links():
    """Obtiene videos, anuncios y una lista de links aleatorios."""
    all_videos = sorted([video for video in os.listdir(VIDEO_FOLDER) if video.endswith(".mp4")])
    all_anuncios = sorted([anuncio for anuncio in os.listdir(ANUNCIOS_FOLDER) if anuncio.endswith(".txt")])
    all_links = sorted([link for link in os.listdir(LINKS_FOLDER) if link.endswith(".txt")])

    num_available = min(3, len(all_videos), len(all_anuncios), len(all_links))
    if num_available == 0:
        return [], [], []

    selected_videos = [all_videos[i % len(all_videos)] for i in video_indices[:num_available]]
    selected_anuncios = [all_anuncios[i % len(all_anuncios)] for i in video_indices[:num_available]]
    selected_links_files = [all_links[i % len(all_links)] for i in video_indices[:num_available]]

    videos_enviados.extend(selected_videos)

    video_urls = [url_for("static", filename=f"videosFinal/{video}") for video in selected_videos]
    
    anuncios = []
    for anuncio in selected_anuncios:
        with open(os.path.join(ANUNCIOS_FOLDER, anuncio), "r", encoding="utf-8") as file:
            lines = file.readlines()
            if lines:
                title = lines[0].strip()
                description = "".join(lines[1:]).strip()
                anuncios.append({"title": title, "description": description})
    
    links_list = []
    for link_file in selected_links_files:
        with open(os.path.join(LINKS_FOLDER, link_file), "r", encoding="utf-8") as file:
            links = [line.strip() for line in file.readlines() if line.strip()]
            links_list.append(links)
    
    return video_urls, anuncios, links_list

@app.route("/")
def home():
    """Carga la página principal home.html."""
    return render_template("home.html")

@app.route("/index")
def index():
    """Carga index.html con los videos, anuncios y links aleatorios."""
    video_urls, anuncios, links_list = obtener_videos_anuncios_links()
    return render_template("index.html", video_urls=video_urls, anuncios=anuncios, links_list=links_list)

@app.route("/nuevo_video")
def nuevo_video():
    """Devuelve un nuevo video en orden, su anuncio correspondiente y una lista de links."""
    all_videos = sorted([video for video in os.listdir(VIDEO_FOLDER) if video.endswith(".mp4")])
    all_anuncios = sorted([anuncio for anuncio in os.listdir(ANUNCIOS_FOLDER) if anuncio.endswith(".txt")])
    all_links = sorted([link for link in os.listdir(LINKS_FOLDER) if link.endswith(".txt")])

    if not all_videos or not all_anuncios or not all_links:
        return jsonify({"error": "No hay videos, anuncios o links disponibles"}), 404

    siguiente_indice = len(videos_enviados) % len(all_videos)
    nuevo_video = all_videos[video_indices[siguiente_indice] % len(all_videos)]
    nuevo_anuncio = all_anuncios[video_indices[siguiente_indice] % len(all_anuncios)]
    nuevo_link_file = all_links[video_indices[siguiente_indice] % len(all_links)]
    
    videos_enviados.append(nuevo_video)
    
    video_url = url_for("static", filename=f"videosFinal/{nuevo_video}")
    
    with open(os.path.join(ANUNCIOS_FOLDER, nuevo_anuncio), "r", encoding="utf-8") as file:
        lines = file.readlines()
        if lines:
            title = lines[0].strip()
            description = "".join(lines[1:]).strip()
            anuncio = {"title": title, "description": description}
        else:
            anuncio = {"title": "", "description": ""}
    
    with open(os.path.join(LINKS_FOLDER, nuevo_link_file), "r", encoding="utf-8") as file:
        links = [line.strip() for line in file.readlines() if line.strip()]
    
    return jsonify({"video_url": video_url, "anuncio": anuncio, "links": links})

# Función para conectar con la base de datos
def conectar_bd():
    return sqlite3.connect('includify.db')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        repetir_contraseña = request.form['repetir_contraseña']

        # Validación: Las contraseñas deben coincidir
        if contraseña != repetir_contraseña:
            flash("Las contraseñas no coinciden", "error")
            
            return render_template('registrarse.html')

        # Encriptar la contraseña con SHA256
        contraseña_encriptada = hashlib.sha256(contraseña.encode()).hexdigest()

        try:
            # Guardar en SQLite
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, correo, contraseña) VALUES (?, ?, ?)",
                           (nombre, correo, contraseña_encriptada))
            conn.commit()
            conn.close()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return render_template('iniciarsesion.html')
        except sqlite3.IntegrityError:
            flash("El correo ya está registrado.", "error")
            return render_template('registrarse.html')

    return render_template('registrarse.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        # Encriptar la contraseña ingresada
        contraseña_encriptada = hashlib.sha256(contraseña.encode()).hexdigest()

        # Verificar credenciales en la base de datos
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = ? AND contraseña = ?", (correo, contraseña_encriptada))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('home'))  # Redirige a la página principal
        else:
            flash("Correo o contraseña incorrectos.", "error")

    return render_template('iniciarsesion.html')

if __name__ == "__main__":
    app.run(debug=True)
