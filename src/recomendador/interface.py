# ============================================================
# interface.py — Ingreso y salida de datos
# ============================================================
#
# Único módulo que usa input() y print().
# No calcula nada: recibe los datos ya procesados y los muestra.
# ============================================================

from recomendador.services import buscar_por_id
from recomendador.utils import validar_opcion_menu

ANCHO = 60


# ── Menú ─────────────────────────────────────────────────────────


def mostrar_menu():
    """Muestra las opciones del menú principal."""
    print("\n" + "=" * ANCHO)
    print("   Sistema de Recomendación Musical")
    print("=" * ANCHO)
    print("1. Mostrar ratings")
    print("2. Generar matriz de recomendaciones (random)")
    print("3. Exportar recomendaciones a CSV (Kaggle)")
    print("0. Salir")


def pedir_opcion():
    """
    Pide una opción hasta que sea válida según la regex de utils.
    Retorna la opción como string ("0" a "3").
    """
    opcion = input("\nOpción: ").strip()
    while not validar_opcion_menu(opcion):
        print("Opción inválida. Ingresá un número entre 0 y 3.")
        opcion = input("Opción: ").strip()
    return opcion


# ── Mensajes ─────────────────────────────────────────────────────


def mostrar_titulo(titulo):
    print(f"\n--- {titulo} ---")


def mostrar_mensaje(mensaje):
    print(mensaje)


def mostrar_error(mensaje):
    print(f"[ERROR] {mensaje}")


# ── Ratings ──────────────────────────────────────────────────────


def mostrar_ratings(ratings_detallados):
    """Muestra los ratings con username, tema y autor."""
    mostrar_titulo("Ratings registrados")

    if not ratings_detallados:
        print("No hay ratings registrados.")
        return

    print(f"{'ID':>3}  {'Usuario':<12} {'Tema':<22} {'Autor':<22} {'Rating':>6}  Fecha")
    print("-" * 85)
    for r in ratings_detallados:
        print(
            f"{r['id_rating']:>3}  {r['username']:<12} {r['tema']:<22} "
            f"{r['autor']:<22} {r['rating']:>6}  {r['fecha']}"
        )


# ── Matrices ─────────────────────────────────────────────────────


def mostrar_matriz(titulo, matriz, usuarios_ord, temas_ord):
    """
    Muestra una matriz usuarios x temas.
    Las columnas se identifican por id de tema (T1, T2, ...).
    """
    mostrar_titulo(titulo)

    encabezado = "".join([f"{'T' + str(t['id_tema']):>5}" for t in temas_ord])
    print(f"{'Usuario':<12}{encabezado}")

    for i, fila in enumerate(matriz):
        valores = "".join([f"{valor:>5}" for valor in fila])
        print(f"{usuarios_ord[i]['username']:<12}{valores}")


def mostrar_referencia_temas(temas_ord):
    """Muestra a qué tema corresponde cada columna T1, T2, ..."""
    print("\nReferencias:")
    for t in temas_ord:
        print(f"  T{t['id_tema']:<3} {t['nombre']} — {t['autor']}")


def mostrar_recomendaciones(recomendaciones, usuarios_ord, temas):
    """Muestra el ranking de temas recomendados para cada usuario."""
    mostrar_titulo("Recomendaciones (ordenadas por score)")

    for i, fila in enumerate(recomendaciones):
        print(f"\n{usuarios_ord[i]['username']}:")
        for posicion, (id_tema, score) in enumerate(fila, start=1):
            tema = buscar_por_id(temas, "id_tema", id_tema)
            print(f"  {posicion}. {tema['nombre']} — {tema['autor']} (score {score})")
