# ============================================================
# preparar_kaggle.py — Archivos para armar la competencia (DOCENTE)
# ============================================================
#
# Genera, a partir de data/ratings.json y data/ground_truth.json:
#
#   solution.csv           -> ratings reales de los pares NO calificados.
#                             Se sube como "solution file". NO se comparte.
#   sample_submission.csv  -> ejemplo del formato que deben subir los
#                             alumnos. Se publica junto con los datos.
#
# Ejecutar desde la raíz del proyecto:
#     python kaggle/preparar_kaggle.py
# ============================================================

import csv
import json
import os

CARPETA_KAGGLE = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATA = os.path.join(os.path.dirname(CARPETA_KAGGLE), "data")

# Usuarios cuyas filas se usan en el leaderboard público.
# El resto queda para el privado (se ve recién al cerrar la competencia).
# Se separa POR USUARIO para que el NDCG de cada uno se calcule completo.
USUARIOS_PUBLICOS = [1, 2]


def leer_json(nombre):
    with open(os.path.join(CARPETA_DATA, nombre), encoding="utf-8") as archivo:
        return json.load(archivo)


def escribir_csv(nombre, encabezado, filas):
    with open(os.path.join(CARPETA_KAGGLE, nombre), "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezado)
        escritor.writerows(filas)
    print(f"{nombre}: {len(filas)} filas")


def main():
    ratings = leer_json("ratings.json")
    ground_truth = leer_json("ground_truth.json")

    calificados = [(r["id_usuario"], r["id_tema"]) for r in ratings]

    # Solo se evalúan los pares que el alumno NO conoce
    a_predecir = [
        g for g in ground_truth
        if (g["id_usuario"], g["id_tema"]) not in calificados
    ]

    solution = [
        [
            f"{g['id_usuario']}_{g['id_tema']}",
            g["rating"],
            "Public" if g["id_usuario"] in USUARIOS_PUBLICOS else "Private",
        ]
        for g in a_predecir
    ]
    sample = [[fila[0], 3] for fila in solution]

    escribir_csv("solution.csv", ["id", "rating", "Usage"], solution)
    escribir_csv("sample_submission.csv", ["id", "rating"], sample)


if __name__ == "__main__":
    main()
