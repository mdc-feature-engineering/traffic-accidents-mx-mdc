# traffic-accidents-mx-mdc

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

# Estudio de accidentes de tráfico en México con enfoque en pavimentación de las calles.

## ¿Para quién es?
Secretaría de Desarrollo Agrario, Territorial y Urbano (SEDATU).

## ¿Qué preguntas puedo responder?
El enfoque es la mala condición de las calles: calles no pavimentadas y calles pavimentadas en mal estado.
* ¿Qué tipo de choques hay en calles en mal estado? (top 5 tipos de accidente)
* ¿Qué tipo de vehículos tienden a tener más accidentes? ¿En qué tipo de calles suburbanas?
* ¿Hay un patrón claro en la hora del día en que ocurren estos choques?

## ¿Qué gráficas?
Tipos de choque, vehículos por zona, gravedad/letalidad, mapas de calor hora × día (ver el dashboard).

## ¿Qué decisiones se tomarán con los resultados?
Impulsar el mejoramiento/tratamiento de las calles a nivel FEDERAL.

## ¿Qué buscamos? ¿Por qué es importante?
Identificar los factores que influyen en los choques. Es importante para reducir los riesgos de la población en general.


# Dashboard (Dash/Plotly)

Página web de presentación en `dashboard/`. Requiere el dataset en `data/raw/` (`make data`).
La primera ejecución convierte el Excel a `data/processed/accidentes_dashboard.parquet` (~1 minuto).

Con Docker:

```bash
docker compose up --build   # o: make docker-dashboard
```

Sin Docker:

```bash
pip install -r requirements-dashboard.txt
python -m dashboard.app     # o: make dashboard
```

Abrir http://localhost:8050.


# Descarga de datos

El dataset no se versiona en Git. Descárgalo desde el enlace compartido de OneDrive con:

```bash
make data
```

El archivo se guarda como `data/raw/traffic_accidents_mx.xlsx`. También puede ejecutarse
directamente con `python3 scripts/download_dataset.py` o indicarse otra salida con
`--output ruta/al/archivo.xlsx`.

El vínculo de OneDrive debe permitir la descarga sin autenticación. Si el comando informa
un error de acceso, actualiza el permiso del recurso a "Cualquier persona con el vínculo"
y reemplaza la constante `SHARE_URL` en el script por el vínculo nuevo.


## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         traffic-accidents and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── traffic-accidents   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes traffic-accidents a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

