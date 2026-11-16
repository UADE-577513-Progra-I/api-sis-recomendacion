# ============================================================
# api.py — API web del sistema de recomendación (Flask)
# ============================================================
#
# Reemplaza a interface.py: en lugar de input() y print(),
# cada opción del menú es una URL que devuelve JSON.
# storage, services y utils se usan SIN cambios.
#
# Ejecutar localmente (desde la carpeta src, o con el paquete instalado):
#     python -m recomendador.api
# y abrir en el navegador:
#     http://127.0.0.1:5000/
# ============================================================

import random

from flask import Flask, jsonify, request, send_file

from recomendador import services, storage
from recomendador.utils import validar_entero

app = Flask(__name__)
app.json.ensure_ascii = False  # muestra tildes y ñ tal cual
app.json.sort_keys = False     # respeta el orden de los campos


# ── Funciones auxiliares ─────────────────────────────────────────


def cargar():
    """
    Lee los JSON en cada petición: si se edita un archivo,
    la API lo refleja sin reiniciar.
    Retorna (usuarios_ord, temas_ord, ratings_validos).
    """
    usuarios, temas, ratings = storage.cargar_datos()
    ratings, _ = services.filtrar_ratings_validos(ratings)
    return (
        services.ordenar_por_id(usuarios, "id_usuario"),
        services.ordenar_por_id(temas, "id_tema"),
        ratings,
    )


def aplicar_semilla():
    """
    Si la URL trae ?seed=<número>, fija la semilla para que las
    recomendaciones sean reproducibles. Sin seed, son al azar.
    Retorna un mensaje de error o None si todo está bien.
    """
    seed = request.args.get("seed")

    if seed is None:
        random.seed()
        return None

    if not validar_entero(seed):
        return "El parámetro seed debe ser un número entero positivo."

    random.seed(int(seed))
    return None


def calcular_recomendaciones(usuarios_ord, temas_ord, ratings):
    """Arma las matrices y retorna la matriz de recomendaciones."""
    matriz_ratings = services.construir_matriz_ratings(ratings, usuarios_ord, temas_ord)
    matriz_predicciones = services.generar_predicciones_random(matriz_ratings)
    return services.generar_recomendaciones(matriz_ratings, matriz_predicciones, temas_ord)


def formatear_usuario(usuario, fila, temas):
    """Convierte una fila de recomendaciones [id_tema, score] a JSON legible."""
    return {
        "id_usuario": usuario["id_usuario"],
        "username": usuario["username"],
        "recomendaciones": [
            {
                "posicion": posicion,
                "id_tema": id_tema,
                "nombre": services.buscar_por_id(temas, "id_tema", id_tema)["nombre"],
                "autor": services.buscar_por_id(temas, "id_tema", id_tema)["autor"],
                "score": score,
            }
            for posicion, (id_tema, score) in enumerate(fila, start=1)
        ],
    }


def error(mensaje, codigo):
    return jsonify({"error": mensaje}), codigo


# URL inexistente (o /recomendaciones/abc): 404 en JSON, no en HTML
@app.errorhandler(404)
def manejar_no_encontrado(_):
    return error("Recurso no encontrado. Ver /docs.", 404)


# Si falla la lectura de un archivo, storage lanza RuntimeError:
# la API responde 500 con el mensaje en JSON en lugar de una página de error.
@app.errorhandler(RuntimeError)
def manejar_error_archivos(excepcion):
    return error(str(excepcion), 500)


# ── Endpoints ────────────────────────────────────────────────────


# ── Documentación (Swagger UI) ───────────────────────────────────
# La especificación está en static/openapi.yaml (Flask sirve la
# carpeta static automáticamente). Swagger UI se carga desde un CDN.

PAGINA_DOCS = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Recomendador — API</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: "/static/openapi.yaml", dom_id: "#swagger-ui" });
  </script>
</body>
</html>"""


@app.get("/docs")
def docs():
    return PAGINA_DOCS


# ── Endpoints ────────────────────────────────────────────────────


@app.get("/")
def inicio():
    """Lista los endpoints disponibles."""
    return jsonify({
        "api": "Sistema de Recomendación Musical",
        "documentacion": "/docs",
        "endpoints": [
            "/usuarios",
            "/temas",
            "/ratings",
            "/recomendaciones",
            "/recomendaciones/<id_usuario>",
            "/recomendaciones.csv",
        ],
        "parametros": {"seed": "opcional, ej: /recomendaciones?seed=42"},
    })


@app.get("/usuarios")
def get_usuarios():
    usuarios, _, _ = cargar()
    return jsonify(usuarios)


@app.get("/temas")
def get_temas():
    _, temas, _ = cargar()
    return jsonify(temas)


@app.get("/ratings")
def get_ratings():
    usuarios, temas, ratings = cargar()
    return jsonify(services.obtener_ratings_detallados(ratings, usuarios, temas))


@app.get("/recomendaciones")
def get_recomendaciones():
    mensaje = aplicar_semilla()
    if mensaje:
        return error(mensaje, 400)

    usuarios, temas, ratings = cargar()
    recomendaciones = calcular_recomendaciones(usuarios, temas, ratings)

    return jsonify([
        formatear_usuario(usuarios[i], recomendaciones[i], temas)
        for i in range(len(usuarios))
    ])


@app.get("/recomendaciones/<int:id_usuario>")
def get_recomendaciones_usuario(id_usuario):
    mensaje = aplicar_semilla()
    if mensaje:
        return error(mensaje, 400)

    usuarios, temas, ratings = cargar()

    # Índice del usuario en la lista ordenada (fila de la matriz)
    indices = [i for i, u in enumerate(usuarios) if u["id_usuario"] == id_usuario]
    if not indices:
        return error(f"No existe el usuario con id {id_usuario}.", 404)

    recomendaciones = calcular_recomendaciones(usuarios, temas, ratings)
    i = indices[0]
    return jsonify(formatear_usuario(usuarios[i], recomendaciones[i], temas))


@app.get("/recomendaciones.csv")
def get_recomendaciones_csv():
    """Genera el CSV para Kaggle con storage y lo devuelve como descarga."""
    mensaje = aplicar_semilla()
    if mensaje:
        return error(mensaje, 400)

    usuarios, temas, ratings = cargar()
    recomendaciones = calcular_recomendaciones(usuarios, temas, ratings)
    filas = services.preparar_filas_kaggle(recomendaciones, usuarios)

    ruta = storage.escribir_csv(["id", "rating"], filas)
    return send_file(ruta, mimetype="text/csv", as_attachment=True,
                     download_name="recomendacion.csv")


if __name__ == "__main__":
    app.run(debug=True)
