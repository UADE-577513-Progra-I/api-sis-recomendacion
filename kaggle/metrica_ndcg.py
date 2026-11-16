"""
Métrica NDCG@3 para la competencia de Kaggle.

Copiar este código en un notebook de métrica de Kaggle.

Para cada usuario:
  1. Se ordenan sus temas según el 'rating' predicho (mayor a menor).
  2. Se toman los 3 primeros y se mira su rating REAL (solution).
  3. Se calcula DCG@3 y se divide por el DCG ideal (IDCG@3).
El score final es el promedio de NDCG@3 entre usuarios (0 a 1, mayor es mejor).

Empates en la predicción: se desempatan por id, para que el resultado
sea determinístico.
"""

import math

import pandas as pd
import pandas.api.types


class ParticipantVisibleError(Exception):
    """Errores cuyo mensaje se le muestra al participante."""
    pass


K = 3


def _dcg(relevancias):
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevancias))


def score(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name: str) -> float:
    """
    NDCG@3 promedio por usuario.

    >>> sol = pd.DataFrame({"id": ["1_1", "1_2", "1_3"], "rating": [5, 3, 1]})
    >>> sub = pd.DataFrame({"id": ["1_1", "1_2", "1_3"], "rating": [3, 2, 1]})
    >>> score(sol, sub, "id")
    1.0
    """
    solution = solution.drop(columns=["Usage"], errors="ignore")

    if "rating" not in submission.columns:
        raise ParticipantVisibleError("Falta la columna 'rating' en el submission.")

    if not pandas.api.types.is_numeric_dtype(submission["rating"]):
        raise ParticipantVisibleError("La columna 'rating' debe ser numérica.")

    if submission[row_id_column_name].duplicated().any():
        raise ParticipantVisibleError("Hay ids repetidos en el submission.")

    datos = solution.merge(
        submission[[row_id_column_name, "rating"]],
        on=row_id_column_name,
        suffixes=("_real", "_pred"),
        how="left",
    )

    if datos["rating_pred"].isna().any():
        faltantes = datos.loc[datos["rating_pred"].isna(), row_id_column_name].head(5).tolist()
        raise ParticipantVisibleError(f"Faltan predicciones para los ids: {faltantes}")

    datos["usuario"] = datos[row_id_column_name].astype(str).str.split("_").str[0]

    ndcgs = []
    for _, grupo in datos.groupby("usuario"):
        ranking = grupo.sort_values(
            ["rating_pred", row_id_column_name], ascending=[False, True]
        )
        dcg = _dcg(ranking["rating_real"].head(K).tolist())
        idcg = _dcg(sorted(grupo["rating_real"], reverse=True)[:K])
        ndcgs.append(dcg / idcg if idcg > 0 else 0.0)

    return float(sum(ndcgs) / len(ndcgs))
