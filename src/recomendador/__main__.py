# ============================================================
# Sistema de Recomendación Musical — Manejo de archivos
# Programación I | UADE
# ============================================================
#
# Punto de entrada del programa. Se ejecuta con:
#     python -m recomendador
#
# Coordina los módulos:
#   storage   -> lee los JSON y escribe el CSV
#   services  -> procesa los ratings y genera recomendaciones
#   interface -> muestra resultados y pide opciones
# ============================================================

from recomendador import interface, services, storage


def opcion_mostrar_ratings(usuarios, temas, ratings):
    detallados = services.obtener_ratings_detallados(ratings, usuarios, temas)
    interface.mostrar_ratings(detallados)


def opcion_generar_recomendaciones(usuarios_ord, temas_ord, ratings):
    """Genera y muestra las matrices. Retorna la matriz de recomendaciones."""
    matriz_ratings = services.construir_matriz_ratings(ratings, usuarios_ord, temas_ord)
    matriz_predicciones = services.generar_predicciones_random(matriz_ratings)
    recomendaciones = services.generar_recomendaciones(
        matriz_ratings, matriz_predicciones, temas_ord
    )

    interface.mostrar_matriz("Matriz de ratings", matriz_ratings, usuarios_ord, temas_ord)
    interface.mostrar_matriz(
        "Matriz de predicciones (random)", matriz_predicciones, usuarios_ord, temas_ord
    )
    interface.mostrar_referencia_temas(temas_ord)
    interface.mostrar_recomendaciones(recomendaciones, usuarios_ord, temas_ord)

    return recomendaciones


def opcion_exportar_csv(recomendaciones, usuarios_ord):
    if recomendaciones is None:
        interface.mostrar_error("Primero generá las recomendaciones (opción 2).")
        return

    filas = services.preparar_filas_kaggle(recomendaciones, usuarios_ord)

    try:
        ruta = storage.escribir_csv(["id", "rating"], filas)
    except RuntimeError as error:
        interface.mostrar_error(error)
        return

    interface.mostrar_mensaje(f"Se exportaron {len(filas)} filas a: {ruta}")


def main():
    # 1. Cargar datos desde los archivos JSON
    try:
        usuarios, temas, ratings = storage.cargar_datos()
    except RuntimeError as error:
        interface.mostrar_error(error)
        interface.mostrar_mensaje("No se puede continuar sin los datos.")
        return

    # 2. Validar ratings y ordenar entidades por id
    ratings, descartados = services.filtrar_ratings_validos(ratings)
    if descartados > 0:
        interface.mostrar_mensaje(f"Se descartaron {descartados} ratings inválidos.")

    usuarios_ord = services.ordenar_por_id(usuarios, "id_usuario")
    temas_ord = services.ordenar_por_id(temas, "id_tema")

    # 3. Menú. Las recomendaciones se guardan para poder exportarlas.
    recomendaciones = None

    while True:
        interface.mostrar_menu()
        opcion = interface.pedir_opcion()

        if opcion == "1":
            opcion_mostrar_ratings(usuarios, temas, ratings)
        elif opcion == "2":
            recomendaciones = opcion_generar_recomendaciones(usuarios_ord, temas_ord, ratings)
        elif opcion == "3":
            opcion_exportar_csv(recomendaciones, usuarios_ord)
        elif opcion == "0":
            interface.mostrar_mensaje("\n¡Hasta luego! 🎵")
            break


if __name__ == "__main__":
    main()
