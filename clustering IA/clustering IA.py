import pandas as pd
import sqlite3
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Conexión a la base de datos SQLite3
conn = sqlite3.connect('registros.db')

# Función para obtener los datos de la tabla EmpleadoModelo y Usuarios
def obtener_datos_de_tablas():
    # Consulta para obtener los datos de la tabla EmpleadoModelo
    query_empleado_modelo = "SELECT * FROM EmpleadoModelo"
    empleado_modelo_df = pd.read_sql(query_empleado_modelo, conn)

    # Consulta para obtener los datos de la tabla Usuarios
    query_usuarios = "SELECT * FROM Usuarios"
    usuarios_df = pd.read_sql(query_usuarios, conn)

    # Concatenar ambos DataFrames en uno solo
    datos_combinados = pd.concat([empleado_modelo_df, usuarios_df], ignore_index=True)

    return datos_combinados

# Obtener los datos
datos = obtener_datos_de_tablas()

# Normalizar los datos
escalador = MinMaxScaler().fit(datos.values)
datos_normalizados = pd.DataFrame(escalador.transform(datos.values), columns=datos.columns)

# Función para obtener grupo y orden de puntos
def obtener_grupo_y_orden(data, punto_referencia, n_clusters):
    """
    Agrupa los datos en n_clusters y encuentra los puntos en el mismo grupo que el punto de referencia,
    ordenados por distancia.
    """
    # Crear una copia del DataFrame para evitar modificar el original
    data_copia = data.copy()

    # Aplicar KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(data_copia)
    data_copia['cluster'] = kmeans.labels_

    # Convertir el punto de referencia a un DataFrame
    punto_df = pd.DataFrame([punto_referencia], columns=data.columns)

    # Identificar el cluster del punto de referencia
    cluster_referencia = kmeans.predict(punto_df)[0]

    # Filtrar puntos del mismo grupo
    puntos_mismo_grupo = data_copia[data_copia['cluster'] == cluster_referencia].drop(columns=['cluster'])

    # Calcular distancias al punto de referencia
    puntos_mismo_grupo['distancia'] = puntos_mismo_grupo.apply(
        lambda fila: np.linalg.norm(fila.values - punto_referencia), axis=1
    )

    # Ordenar por distancia
    puntos_ordenados = puntos_mismo_grupo.sort_values(by='distancia')

    return cluster_referencia, puntos_ordenados

# Función jerarquia
def jerarquia(n_clusters_inicial):
    """
    Realiza el proceso iterativo de jerarquía y muestra los resultados.
    """
    # Seleccionar el segundo punto como punto de referencia
    punto_referencia = datos_normalizados.iloc[1].values

    # Inicializar una lista para almacenar los resultados
    resultados_por_nivel = []

    for n_clusters in range(n_clusters_inicial, 0, -1):
        cluster_referencia, puntos_ordenados = obtener_grupo_y_orden(datos_normalizados, punto_referencia, n_clusters)

        resultados_por_nivel.append({
            'clusters': n_clusters,
            'cluster_referencia': cluster_referencia,
            'puntos_ordenados': puntos_ordenados
        })

    # Inicializar una lista para almacenar los índices ya mostrados
    indices_mostrados = []

    # Imprimir resultados
    for resultado in resultados_por_nivel:
        print(f"\nNúmero de clusters: {resultado['clusters']}")
        print(f"Grupo del punto de referencia: {resultado['cluster_referencia']}")
        print("Puntos en el mismo grupo ordenados por distancia:")

        # Filtrar los puntos que no hayan sido mostrados en niveles anteriores
        puntos_no_mostrados = resultado['puntos_ordenados'].index[~resultado['puntos_ordenados'].index.isin(indices_mostrados)]

        # Agregar los índices mostrados en este nivel a la lista de mostrados
        indices_mostrados.extend(puntos_no_mostrados.tolist())

        # Convertir los índices en una cadena separada por comas
        indices_ordenados = ', '.join(map(str, puntos_no_mostrados.tolist()))

        # Imprimir los índices de los puntos sin repetir
        print(indices_ordenados)

# Llamada a la función jerarquia con el número de clusters inicial
jerarquia(6)

def conjunto(n_clusters):
    """
    Muestra los elementos que están en el mismo grupo según el número de clusters proporcionado.
    """
    # Seleccionar el segundo punto como punto de referencia
    punto_referencia = datos_normalizados.iloc[1].values

    # Obtener los puntos del mismo grupo
    cluster_referencia, puntos_ordenados = obtener_grupo_y_orden(datos_normalizados, punto_referencia, n_clusters)

    print(f"\nNúmero de clusters: {n_clusters}")
    print(f"Grupo del punto de referencia: {cluster_referencia}")
    print("Puntos en el mismo grupo ordenados por distancia:")

    # Imprimir todos los puntos en el mismo grupo
    print(', '.join(map(str, puntos_ordenados.index.tolist())))

# Llamada a la función conjunto con el número de grupos
conjunto(5)

# Graficar la inercia para determinar el número óptimo de clusters
inercias = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k).fit(datos.values)
    inercias.append(kmeans.inertia_)

plt.figure(figsize=(6, 5), dpi=100)
plt.scatter(range(2, 10), inercias, marker="o", s=180, color="purple")
plt.xlabel("Número de Clusters", fontsize=25)
plt.ylabel("Inercia", fontsize=25)
plt.show()

# Cerrar la conexión a la base de datos
conn.close()

