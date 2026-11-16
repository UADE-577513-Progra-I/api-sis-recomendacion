# ============================================================
# storage.py — Manejo de archivos
# ============================================================
#
# - Lectura de archivos JSON (usuarios, temas, ratings)
# - Escritura del archivo CSV de recomendaciones (para Kaggle)
#
# Este módulo NO usa print() ni input(): si algo falla, captura la
# excepción concreta y la relanza como RuntimeError con un mensaje
# claro. Quien llama (el programa principal) decide cómo mostrarlo.
# ============================================================

import csv
import json
import os

# ── Rutas ────────────────────────────────────────────────────────
# Las rutas se calculan a partir de la ubicación de ESTE archivo,
# no desde la carpeta donde se ejecuta el programa.
#
#   .../sistema_recomendacion/src/recomendador/storage.py
#   dirname x1 -> .../src/recomendador
#   dirname x2 -> .../src
#   dirname x3 -> .../sistema_recomendacion   (raíz del proyecto)

RUTA_ESTE_ARCHIVO = os.path.abspath(__file__)
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(RUTA_ESTE_ARCHIVO)))

CARPETA_DATA = os.path.join(RAIZ_PROYECTO, "data")
CARPETA_OUTPUT = os.path.join(RAIZ_PROYECTO, "output")

ARCHIVO_USUARIOS = "usuarios.json"
ARCHIVO_TEMAS = "temas.json"
ARCHIVO_RATINGS = "ratings.json"
ARCHIVO_RECOMENDACION = "recomendacion.csv"


# ── Lectura ──────────────────────────────────────────────────────


def leer_json(nombre_archivo):
    """
    Lee un archivo JSON de la carpeta data y retorna su contenido.

    Se espera que el archivo contenga una lista de diccionarios.
    Lanza RuntimeError si el archivo no existe, no se puede leer
    o no tiene un JSON válido.
    """
    ruta = os.path.join(CARPETA_DATA, nombre_archivo)

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

    except FileNotFoundError:
        raise RuntimeError(f"No se encontró el archivo: {ruta}")

    except PermissionError:
        raise RuntimeError(f"No hay permisos para leer el archivo: {ruta}")

    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"El archivo {nombre_archivo} no tiene un JSON válido "
            f"(línea {error.lineno}, columna {error.colno})."
        )

    if not isinstance(datos, list):
        raise RuntimeError(f"El archivo {nombre_archivo} debe contener una lista.")

    return datos


def cargar_datos():
    """
    Lee los tres archivos JSON del sistema.
    Retorna una tupla (usuarios, temas, ratings).
    """
    usuarios = leer_json(ARCHIVO_USUARIOS)
    temas = leer_json(ARCHIVO_TEMAS)
    ratings = leer_json(ARCHIVO_RATINGS)
    return usuarios, temas, ratings


# ── Escritura ────────────────────────────────────────────────────


def escribir_csv(encabezado, filas, nombre_archivo=ARCHIVO_RECOMENDACION):
    """
    Escribe un archivo CSV en la carpeta output.

    encabezado: lista con los nombres de las columnas
    filas:      lista de listas, una por registro

    Retorna la ruta completa del archivo generado.
    Lanza RuntimeError si no se pudo escribir.
    """
    ruta = os.path.join(CARPETA_OUTPUT, nombre_archivo)

    try:
        # Crea la carpeta output si todavía no existe
        os.makedirs(CARPETA_OUTPUT, exist_ok=True)

        # newline="" evita líneas en blanco entre filas en Windows
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(encabezado)
            escritor.writerows(filas)

    except PermissionError:
        # Caso típico: el CSV está abierto en Excel
        raise RuntimeError(
            f"No se pudo escribir {ruta}. ¿Está abierto en otro programa?"
        )

    except OSError as error:
        raise RuntimeError(f"Error al escribir {ruta}: {error}")

    return ruta
