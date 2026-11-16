# Sistema de Recomendación Musical — Manejo de archivos

Programación I | UADE

Lee usuarios, temas y ratings desde archivos JSON, genera recomendaciones
con predicciones aleatorias y las exporta a un CSV listo para subir a Kaggle.

## Estructura

```
sistema_recomendacion/
├── pyproject.toml
├── README.md
├── data/
│   ├── usuarios.json      # id_usuario, username
│   ├── temas.json         # id_tema, nombre, autor
│   ├── ratings.json       # id_rating, id_usuario, id_tema, rating, fecha
│   └── ground_truth.json  # (docente) ratings reales de los 50 pares
├── output/                # se crea al exportar: recomendacion.csv
└── src/
    └── recomendador/
        ├── __init__.py
        ├── __main__.py    # punto de entrada y menú
        ├── interface.py   # input() / print()
        ├── services.py    # lógica de ratings y recomendaciones
        ├── storage.py     # lectura de JSON y escritura de CSV
        └── utils.py       # validaciones con regex
```

## Cómo ejecutarlo

Desde la carpeta `sistema_recomendacion`:

```bash
pip install -e .
python -m recomendador
```

`pip install -e .` se hace una sola vez. Registra el paquete en modo
"editable": los cambios en el código se ven sin reinstalar.

Sin instalar, también funciona así:

```bash
cd src
python -m recomendador
```

> No ejecutes `python src/recomendador/__main__.py`: los imports
> `from recomendador import ...` fallan porque Python no encuentra el paquete.

## Formato del CSV (Kaggle)

```
id,rating
1_3,5
1_7,4
...
```

`id` es `<id_usuario>_<id_tema>` y `rating` es el score predicho.
Se exportan las 5 recomendaciones de cada usuario (25 filas).

## API (Flask)

Instalar dependencias (una vez) y levantar el servidor:

```bash
pip install -e .
python -m recomendador.api
```

Abrir en el navegador `http://127.0.0.1:5000/`. Endpoints:

| URL | Devuelve |
|---|---|
| `/usuarios` | Lista de usuarios |
| `/temas` | Lista de temas |
| `/ratings` | Ratings con username, tema y autor |
| `/recomendaciones` | Recomendaciones random de todos los usuarios |
| `/recomendaciones/<id_usuario>` | Recomendaciones de un usuario |
| `/recomendaciones.csv` | Descarga el CSV para Kaggle |

Parámetro opcional `?seed=42` para resultados reproducibles.

### Documentación y pruebas

- **Swagger UI:** `http://127.0.0.1:5000/docs`. Documenta cada endpoint y permite
  probarlo con *Try it out*. La especificación está en `src/recomendador/static/openapi.yaml`.
- **Postman:** importar `pruebas_api/recomendador.postman_collection.json`
  (File → Import) y ejecutar la colección con *Run collection*: cada petición trae tests.
- **VS Code:** abrir `pruebas_api/pruebas.http` con la extensión REST Client.

Para probar en PythonAnywhere, cambiar la variable `baseUrl` (Postman) o `@baseUrl` (.http).
Para cortar el servidor: `Ctrl + C`.
