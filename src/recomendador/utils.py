# ============================================================
# utils.py — Validaciones con expresiones regulares
# ============================================================
#
# re.fullmatch() exige que TODO el texto coincida con el patrón.
# Ojo con re.match(): solo mira el comienzo, entonces
#   re.match(r"[0-3]", "1abc")      -> coincide (¡mal!)
#   re.fullmatch(r"[0-3]", "1abc")  -> None     (bien)
# ============================================================

import re

# Opciones válidas del menú principal: un único dígito entre 0 y 3
PATRON_OPCION_MENU = r"[0-3]"

# Rating válido: un único dígito entre 1 y 5
PATRON_RATING = r"[1-5]"

# Fecha en formato ISO: AAAA-MM-DD (mes 01-12, día 01-31)
PATRON_FECHA = r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"

# Entero positivo de hasta 9 dígitos (por ejemplo, la semilla de la API)
PATRON_ENTERO = r"\d{1,9}"


def validar_opcion_menu(opcion):
    """
    Retorna True si la opción ingresada es válida para el menú.
    Se ignoran los espacios al principio y al final.
    """
    return re.fullmatch(PATRON_OPCION_MENU, opcion.strip()) is not None


def validar_rating(valor):
    """
    Retorna True si el valor es un rating entre 1 y 5.
    Acepta int o str: se convierte a str para aplicar el patrón.
    """
    return re.fullmatch(PATRON_RATING, str(valor)) is not None


def validar_fecha(fecha):
    """Retorna True si la fecha tiene formato AAAA-MM-DD."""
    return re.fullmatch(PATRON_FECHA, str(fecha)) is not None


def validar_entero(valor):
    """Retorna True si el valor es un entero positivo (solo dígitos)."""
    return re.fullmatch(PATRON_ENTERO, str(valor)) is not None
