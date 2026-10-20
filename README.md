# Accidentes de tránsito en calles en mal estado · México 2015

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Estudio de los accidentes de tránsito ocurridos en **calles no pavimentadas y calles pavimentadas
en mal estado** en México, con datos de INEGI (ATUS 2015). El proyecto se presenta como una
página web interactiva construida con Dash/Plotly.

Proyecto de equipo para la materia de Ingeniería de Características, Maestría en Ciencia de
Datos, Universidad de Sonora.

---

## Planteamiento

| | |
|---|---|
| **¿Para quién es?** | Secretaría de Desarrollo Agrario, Territorial y Urbano (**SEDATU**). |
| **¿Qué decisiones se tomarán?** | Impulsar el mejoramiento y tratamiento de las calles a nivel **federal**: dónde invertir primero y qué tipo de intervención realizar. |
| **¿Qué buscamos?** | Los factores que influyen en los choques en calles en mal estado. |
| **¿Por qué es importante?** | Una calle en mal estado es un riesgo evitable; cuantificarlo ayuda a reducir los riesgos para la población en general. |

### ¿Qué es una «calle en mal estado»?

Se unen dos criterios del registro:

- **No pavimentada**: `CAPAROD = "No Pavimentada"` (2,385 accidentes).
- **Pavimentada en mal estado**: pavimentada con `CAUSAACCI = "Mala condición del camino"` (2,403 accidentes).

En total son **4,788 accidentes** (2.7% del registro). El resto se usa como grupo de referencia, **«Buen estado»**.

### Preguntas

1. ¿Qué tipos de choque ocurren en calles en mal estado? (top 5)
2. ¿Qué tipos de vehículos tienen más accidentes y en qué tipo de calles suburbanas?
3. ¿Hay un patrón claro en la hora del día en que ocurren estos choques?

Además se analizan la **gravedad y la letalidad** (% de accidentes con al menos una víctima mortal).

---

## Hallazgos principales

- **Las calles no pavimentadas son más letales**: el 2.9% de sus accidentes son fatales, contra
  1.0% en calles en buen estado. Se descarta la hipótesis de que en terracería los choques son
  menos graves porque se maneja más lento.
- **Las calles pavimentadas en mal estado son menos letales** (0.5%); más del 70% de sus
  choques son contra un objeto fijo.
- La vía más letal es la **carretera estatal sin pavimentar**: el 13.3% de sus accidentes son fatales.
- En calles no pavimentadas las **volcaduras** son 4.7 veces más frecuentes que en calles en buen estado.
- Los choques se concentran en la **noche** (la hora pico es alrededor de las 21:00) y, en calles
  no pavimentadas, en **fin de semana** (43%).
- Solo el 2.1% de los choques en calles no pavimentadas se atribuye a «mala condición del camino»:
  esta causa probablemente está **subregistrada**.

---

## Dashboard

La página web está en `dashboard/` y se presenta directamente desde el navegador. Secciones:
planteamiento, estrategia de análisis, tipos de choque, vehículos y zonas, gravedad,
patrón horario y hallazgos. Tiene filtros por **grupo** (no pavimentada / pavimentada en
mal estado), **entidad** y **gravedad**.

### Cómo ejecutarlo

1. Descarga el dataset (no se versiona en Git):

   ```bash
   make data
   ```

2. Inicia el dashboard con Docker:

   ```bash
   docker compose up --build   # o: make docker-dashboard
   ```

   O sin Docker:

   ```bash
   pip install -r requirements-dashboard.txt
   python -m dashboard.app     # o: make dashboard
   ```

3. Abre http://localhost:8050.

La primera ejecución convierte el Excel a `data/processed/accidentes_dashboard.parquet` (~1 minuto);
las siguientes usan ese archivo. Para detener el contenedor: `docker compose down`.

---

## Datos

- **Fuente:** INEGI, Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas (ATUS), año 2015.
- **Tamaño:** 180,066 accidentes y 45 variables (ubicación, fecha y hora, tipo de choque,
  vehículos, causa, superficie, conductor y víctimas).
- **Cobertura:** municipal, 16 entidades (claves INEGI 1–16).
- **Diccionario de datos:** [`docs/docs/data_dictionary.md`](docs/docs/data_dictionary.md).

### Descarga

`make data` descarga el archivo desde el enlace compartido de OneDrive y lo guarda como
`data/raw/traffic_accidents_mx.xlsx`. También puede ejecutarse con
`python3 scripts/download_dataset.py`; usa `--output ruta/al/archivo.xlsx` para guardarlo en otra ruta.

El vínculo debe permitir la descarga sin iniciar sesión. Si el comando informa un error de
acceso, cambia el permiso del archivo a «Cualquier persona con el vínculo» y reemplaza la
constante `SHARE_URL` del script por el vínculo nuevo.

### Transformaciones principales

| Nueva variable | Origen | Transformación |
|---|---|---|
| `CONDICION_CALLE`, `MAL_ESTADO` | `CAPAROD`, `CAUSAACCI` | No pavimentada / Pavimentada en mal estado / Buen estado |
| `HORA`, `FRANJA_HORARIA` | `ID_HORA` | 99 (no especificado) → nulo; 4 franjas horarias |
| `EDAD` | `ID_EDAD` | 99 (no especificado) y 0 (conductor se fugó) → nulo |
| `DIASEMANA`, `MES`, `FECHA` | texto, `ANIO`, `ID_DIA` | Categorías ordenadas y fecha completa |
| `TOTAL_MUERTOS`, `TOTAL_HERIDOS`, `ES_FATAL` | columnas de víctimas, `CLASACC` | Agregados de gravedad |
| `TOTAL_VEHICULOS` | 13 columnas de vehículos | Suma de unidades involucradas |
| `ZONA_VIAL` | `SUBURBANA`, `URBANA` | Una sola variable de tipo de vía |
| `ENTIDAD` | `ID_ENTIDAD` | Clave INEGI → nombre del estado |

### Limitaciones

- Un solo año (2015) y 16 de las 32 entidades.
- La causa la asigna la autoridad en el lugar del accidente; la mala condición del camino probablemente está subregistrada.
- No hay datos de exposición (km de calles, aforo vehicular), por lo que no se pueden calcular tasas por km o por habitante.
- Hay pocos accidentes fatales en calles en mal estado (79), así que algunos cruces tienen muestras pequeñas.

---

## Estructura del proyecto

```
├── Makefile                   <- Comandos: make data, make dashboard, make docker-dashboard
├── README.md
├── Dockerfile                 <- Imagen del dashboard (Python 3.12 + gunicorn)
├── docker-compose.yml         <- Levanta el dashboard en el puerto 8050 y monta ./data
├── requirements.txt           <- Entorno de los notebooks
├── requirements-dashboard.txt <- Dependencias del dashboard
├── pyproject.toml
│
├── dashboard                  <- Página web Dash/Plotly
│   ├── app.py                 <- Aplicación, filtros (callbacks) y hallazgos
│   ├── data.py                <- Carga de datos, transformaciones y caché parquet
│   ├── figures.py             <- Gráficas
│   ├── layout.py              <- Textos y estructura de la página
│   └── assets/style.css       <- Estilos
│
├── data                       <- No se versiona en Git
│   ├── raw                    <- Excel original (make data)
│   └── processed              <- Caché parquet que genera el dashboard
│
├── docs                       <- Documentación mkdocs y diccionario de datos
├── notebooks
│   ├── data_analysis.ipynb        <- Exploración inicial
│   └── data_analysis_table.ipynb  <- Análisis de calles en mal estado (base del dashboard)
├── reports/figures            <- Figuras exportadas del análisis
├── scripts/download_dataset.py <- Descarga del dataset
└── traffic_accidents          <- Paquete del template Cookiecutter Data Science
```

### Comandos `make`

| Comando | Qué hace |
|---|---|
| `make data` | Descarga el dataset a `data/raw/` |
| `make dashboard` | Ejecuta el dashboard localmente |
| `make docker-dashboard` | Construye y ejecuta el dashboard en Docker |
| `make requirements` | Instala el entorno de los notebooks |
| `make lint` / `make format` | Revisa o formatea el código con ruff |
