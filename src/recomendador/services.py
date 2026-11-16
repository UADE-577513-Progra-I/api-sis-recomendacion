# ============================================================
# services.py — Lógica de la relación rating
# ============================================================
#
# Funciones "puras": reciben listas por parámetro y retornan
# resultados. No leen archivos, no usan print() ni input()
# y no dependen de variables globales.
#
# Convención: usuarios y temas se ordenan siempre por id, de modo
# que la fila i de una matriz es el usuario i y la columna j es el
# tema j de esas listas ordenadas.
# ============================================================

import random

from recomendador.utils import validar_fecha, validar_rating

# Cantidad de recomendaciones por usuario que se exportan
TOP_K = 5


# ── Utilidades ───────────────────────────────────────────────────


def buscar_por_id(lista, campo_id, valor_id):
    """
    Busca en 'lista' el diccionario cuyo campo 'campo_id' vale 'valor_id'.
    Retorna el diccionario o None si no existe.

    Ejemplo: buscar_por_id(temas, "id_tema", 3)
    """
    coincidencias = [elemento for elemento in lista if elemento[campo_id] == valor_id]
    return coincidencias[0] if coincidencias else None


def ordenar_por_id(lista, campo_id):
    """Retorna una copia de la lista ordenada por el campo id indicado."""
    return sorted(lista, key=lambda elemento: elemento[campo_id])


def filtrar_ratings_validos(ratings):
    """
    Descarta los ratings con valor fuera de 1-5 o fecha mal formada.
    Retorna una tupla (ratings_validos, cantidad_descartados).
    """
    validos = [
        r for r in ratings
        if validar_rating(r["rating"]) and validar_fecha(r["fecha"])
    ]
    return validos, len(ratings) - len(validos)


# ── Ratings con datos de usuario y tema ("JOIN" manual) ──────────


def detallar_rating(rating, usuarios, temas):
    """
    A partir de un rating (que solo tiene ids) arma un diccionario
    con username, nombre del tema y autor.
    """
    usuario = buscar_por_id(usuarios, "id_usuario", rating["id_usuario"])
    tema = buscar_por_id(temas, "id_tema", rating["id_tema"])

    return {
        "id_rating": rating["id_rating"],
        "username": usuario["username"] if usuario else "desconocido",
        "tema": tema["nombre"] if tema else "desconocido",
        "autor": tema["autor"] if tema else "desconocido",
        "rating": rating["rating"],
        "fecha": rating["fecha"],
    }


def obtener_ratings_detallados(ratings, usuarios, temas):
    """Retorna la lista de ratings con los datos de usuario y tema."""
    return [detallar_rating(rating, usuarios, temas) for rating in ratings]


# ── Matrices ─────────────────────────────────────────────────────


def obtener_rating(ratings, id_usuario, id_tema):
    """Retorna el rating del usuario para ese tema, o 0 si no lo calificó."""
    valores = [
        r["rating"] for r in ratings
        if r["id_usuario"] == id_usuario and r["id_tema"] == id_tema
    ]
    return valores[0] if valores else 0


def construir_matriz_ratings(ratings, usuarios_ord, temas_ord):
    """
    Construye la matriz usuarios x temas.
        matriz[i][j] = rating del usuario i al tema j (0 si no lo calificó)
    """
    return [
        [obtener_rating(ratings, u["id_usuario"], t["id_tema"]) for t in temas_ord]
        for u in usuarios_ord
    ]


def generar_predicciones_random(matriz_ratings):
    """
    Genera una matriz de predicciones del mismo tamaño que la de ratings.
    - Tema no calificado (0): score aleatorio entre 1 y 5.
    - Tema ya calificado: 0, porque no necesita predicción.
    """
    return [
        [random.randint(1, 5) if rating == 0 else 0 for rating in fila]
        for fila in matriz_ratings
    ]


# ── Recomendaciones ──────────────────────────────────────────────


def recomendar_usuario(fila_ratings, fila_predicciones, temas_ord, k=TOP_K):
    """
    Arma el ranking de un usuario: los temas que NO calificó,
    ordenados por score predicho de mayor a menor.
    Retorna hasta k pares [id_tema, score].
    """
    candidatos = [
        [temas_ord[j]["id_tema"], fila_predicciones[j]]
        for j in range(len(temas_ord))
        if fila_ratings[j] == 0
    ]
    candidatos.sort(key=lambda candidato: candidato[1], reverse=True)
    return candidatos[:k]


def generar_recomendaciones(matriz_ratings, matriz_predicciones, temas_ord, k=TOP_K):
    """
    Retorna la matriz de recomendaciones: una fila por usuario,
    cada una con hasta k pares [id_tema, score] ordenados por score.
    """
    return [
        recomendar_usuario(matriz_ratings[i], matriz_predicciones[i], temas_ord, k)
        for i in range(len(matriz_ratings))
    ]


def preparar_filas_kaggle(recomendaciones, usuarios_ord):
    """
    Convierte la matriz de recomendaciones al formato largo de Kaggle:
        id,rating
        1_3,5
        1_7,4
    donde id = "<id_usuario>_<id_tema>". Una fila por par recomendado.
    """
    return [
        [f"{usuarios_ord[i]['id_usuario']}_{id_tema}", score]
        for i in range(len(recomendaciones))
        for id_tema, score in recomendaciones[i]
    ]
