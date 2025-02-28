import sqlite3

# Conectar a la base de datos (se crea si no existe)
conn = sqlite3.connect('includify.db')
cursor = conn.cursor()

# Crear la tabla de usuarios si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    contraseña TEXT NOT NULL
)
''')

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("Base de datos creada con éxito.")
