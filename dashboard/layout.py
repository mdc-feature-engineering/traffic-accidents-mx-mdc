"""Estructura de la página: narrativa, controles y contenedores de gráficas."""

from __future__ import annotations

from dash import dcc, html

from dashboard.data import ENTIDADES, GRAVEDADES, GRUPOS, MAL_ESTADO

GRAPH_CONFIG = {"displaylogo": False, "responsive": True}

SECCIONES = [
    ("planteamiento", "Planteamiento"),
    ("estrategia", "Estrategia"),
    ("tipos", "Tipos de choque"),
    ("vehiculos", "Vehículos y zonas"),
    ("gravedad", "Gravedad"),
    ("tiempo", "Patrón horario"),
    ("hallazgos", "Hallazgos"),
]


def _graph(id_: str) -> dcc.Loading:
    return dcc.Loading(dcc.Graph(id=id_, config=GRAPH_CONFIG), type="dot", color="#c0392b")


def _figura(id_: str, titulo: str, nota: str | None = None) -> html.Figure:
    hijos = [html.H4(titulo, className="fig-title"), _graph(id_)]
    if nota:
        hijos.append(html.Figcaption(nota))
    return html.Figure(hijos, className="card")


def _pregunta(texto: str) -> html.P:
    return html.P(texto, className="question")


def _tabla(encabezados: list[str], filas: list[list]) -> html.Table:
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(h) for h in encabezados])),
            html.Tbody([html.Tr([html.Td(c) for c in fila]) for fila in filas]),
        ],
        className="data-table",
    )


def _kpi(id_: str, etiqueta: str) -> html.Div:
    return html.Div(
        [html.Div("–", id=id_, className="kpi-value"), html.Div(etiqueta, className="kpi-label")],
        className="kpi",
    )


def navbar() -> html.Nav:
    return html.Nav(
        [
            html.A("Calles en mal estado · MX 2015", href="#inicio", className="brand"),
            html.Div([html.A(t, href=f"#{i}") for i, t in SECCIONES], className="nav-links"),
        ],
        className="navbar",
    )


def filtros() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Grupo de calles en mal estado"),
                    dcc.Dropdown(
                        id="f-grupo",
                        options=GRUPOS,
                        value=MAL_ESTADO,
                        clearable=False,
                    ),
                ],
                className="filter",
            ),
            html.Div(
                [
                    html.Label("Entidad federativa"),
                    dcc.Dropdown(
                        id="f-entidad",
                        options=[{"label": v, "value": k} for k, v in ENTIDADES.items()],
                        multi=True,
                        placeholder="Las 16 entidades disponibles",
                    ),
                ],
                className="filter filter-wide",
            ),
            html.Div(
                [
                    html.Label("Gravedad"),
                    dcc.Checklist(
                        id="f-gravedad",
                        options=GRAVEDADES,
                        value=GRAVEDADES,
                        inline=True,
                        className="checklist",
                    ),
                ],
                className="filter",
            ),
        ],
        className="filters",
    )


def portada() -> html.Header:
    return html.Header(
        [
            html.P("Ingeniería de características · Maestría en Ciencia de Datos", className="eyebrow"),
            html.H1("Accidentes de tránsito en calles en mal estado"),
            html.P(
                "Estrategia de análisis y hallazgos preliminares sobre los accidentes en calles "
                "no pavimentadas y pavimentadas en mala condición en México (INEGI, ATUS 2015) "
                "para orientar la inversión federal en infraestructura vial.",
                className="lead",
            ),
            html.Div(
                [
                    _kpi("kpi-total", "accidentes registrados"),
                    _kpi("kpi-mal", "en calles en mal estado"),
                    _kpi("kpi-muertos", "muertos en calles en mal estado"),
                    _kpi("kpi-heridos", "heridos en calles en mal estado"),
                    _kpi("kpi-letalidad", "letalidad: mal estado vs. buen estado"),
                ],
                className="kpis",
            ),
        ],
        id="inicio",
        className="hero",
    )


def planteamiento() -> html.Section:
    tarjetas = [
        ("¿Para quién es?",
         "Secretaría de Desarrollo Agrario, Territorial y Urbano (SEDATU), responsable de la "
         "política federal de ordenamiento territorial, movilidad e infraestructura urbana."),
        ("¿Qué decisiones se tomarán?",
         "Impulsar y priorizar a nivel FEDERAL programas de pavimentación, rehabilitación y "
         "tratamiento de calles: dónde invertir primero, qué tipo de intervención y qué "
         "elementos de seguridad vial acompañan la obra."),
        ("¿Qué buscamos?",
         "Los factores asociados a los choques en calles en mal estado: tipo de choque, "
         "vehículos involucrados, tipo de vía, gravedad y momento del día."),
        ("¿Por qué es importante?",
         "Una calle en mal estado es un riesgo evitable. Cuantificarlo permite reducir muertes "
         "y lesiones de conductores, pasajeros, peatones y ciclistas con evidencia."),
    ]
    return html.Section(
        [
            html.H2("1. Planteamiento"),
            html.Div(
                [html.Div([html.H3(t), html.P(d)], className="card pitch") for t, d in tarjetas],
                className="grid-2",
            ),
            html.H3("¿Qué entendemos por «calle en mal estado»?"),
            html.P(
                [
                    "Unimos dos fuentes de evidencia del registro: ",
                    html.Strong("calles no pavimentadas"),
                    " (CAPAROD = «No Pavimentada») y ",
                    html.Strong("calles pavimentadas en mal estado"),
                    " (CAUSAACCI = «Mala condición del camino»). El resto se toma como grupo de "
                    "referencia «Buen estado».",
                ]
            ),
            _figura("g-definicion", "Composición de los accidentes en calles en mal estado"),
        ],
        id="planteamiento",
    )


def estrategia() -> html.Section:
    pasos = ["Datos ATUS 2015", "Limpieza", "Ingeniería de características", "EDA y gráficas",
             "Hallazgos", "Decisión SEDATU"]
    preguntas = [
        ["¿Qué tipos de choque ocurren en calles en mal estado?",
         "Barras top 5 y comparación de proporciones vs. buen estado", "TIPACCID, CONDICION_CALLE"],
        ["¿Qué vehículos se accidentan más y en qué calles suburbanas?",
         "Barras apiladas vehículo × zona; 100 % superficie × zona", "AUTOMOVIL…OTROVEHIC, SUBURBANA, URBANA"],
        ["¿Son más graves los choques en calles en mal estado?",
         "Gravedad 100 %, letalidad por zona, víctimas por tipo", "CLASACC, *MUERTO, *HERIDO, ZONA_VIAL"],
        ["¿Hay un patrón claro en la hora del día?",
         "Mapa de calor hora × día, curvas por hora, letalidad por franja", "HORA, DIASEMANA, FRANJA_HORARIA, MES"],
    ]
    transformaciones = [
        ["CONDICION_CALLE / MAL_ESTADO", "CAPAROD + CAUSAACCI",
         "Variable objetivo del estudio: No pavimentada, Pavimentada en mal estado, Buen estado"],
        ["HORA, FRANJA_HORARIA", "ID_HORA", "99 = no especificado → nulo; discretización en 4 franjas"],
        ["EDAD", "ID_EDAD", "0 y 99 (no especificado) → nulo"],
        ["DIASEMANA, MES", "texto", "Categorías ordenadas; «No especificado» → nulo"],
        ["FECHA, MES_NUM", "ANIO, MES, ID_DIA", "Fecha completa para series de tiempo"],
        ["TOTAL_MUERTOS, TOTAL_HERIDOS, ES_FATAL", "12 columnas de víctimas, CLASACC",
         "Agregados de gravedad por accidente"],
        ["TOTAL_VEHICULOS", "13 columnas de vehículos", "Suma de unidades involucradas"],
        ["ZONA_VIAL", "SUBURBANA + URBANA", "Una sola variable de tipo de vía"],
        ["ENTIDAD", "ID_ENTIDAD", "Clave INEGI → nombre del estado"],
    ]
    return html.Section(
        [
            html.H2("2. Estrategia de análisis"),
            html.Div(
                [html.Div(p, className="step") for p in pasos],
                className="pipeline",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Los datos"),
                            html.Ul(
                                [
                                    html.Li("180,066 accidentes registrados por INEGI (ATUS), año 2015."),
                                    html.Li("Cobertura municipal de 16 entidades (claves INEGI 1–16)."),
                                    html.Li("45 variables: ubicación, fecha y hora, tipo de choque, "
                                            "vehículos, causa, superficie, conductor y víctimas."),
                                    html.Li("Calidad: sin nulos en columnas clave, pero con códigos "
                                            "centinela (99, «No especificado», «Se ignora»)."),
                                ]
                            ),
                        ],
                        className="card",
                    ),
                    html.Div(
                        [
                            html.H3("Cómo leer esta página"),
                            html.Ul(
                                [
                                    html.Li("Usa los filtros fijos de arriba: grupo, entidad y gravedad."),
                                    html.Li("Comparamos siempre contra «Buen estado»: las proporciones "
                                            "y tasas importan más que los conteos absolutos."),
                                    html.Li("Las tasas de letalidad ignoran el filtro de gravedad."),
                                    html.Li("Pasa el cursor sobre las gráficas para ver valores exactos."),
                                ]
                            ),
                        ],
                        className="card",
                    ),
                ],
                className="grid-2",
            ),
            html.H3("Preguntas → gráficas"),
            _tabla(["Pregunta", "Gráfica", "Variables"], preguntas),
            html.H3("Transformaciones de datos (ingeniería de características)"),
            _tabla(["Nueva variable", "Origen", "Transformación"], transformaciones),
        ],
        id="estrategia",
    )


def tipos() -> html.Section:
    return html.Section(
        [
            html.H2("3. ¿Qué tipos de choque ocurren en calles en mal estado?"),
            _pregunta("Hipótesis: en terracería y baches predominan los choques contra objeto fijo, "
                      "las volcaduras y las salidas del camino, lo que indica falta de señalamiento "
                      "y de elementos de contención."),
            html.Div(
                [
                    _figura("g-top-tipos", "Top 5 tipos de choque del grupo seleccionado"),
                    _figura("g-tipos-vs", "Proporción de cada tipo de choque vs. calles en buen estado",
                            "×N = cuántas veces más frecuente es ese tipo en el grupo que en buen estado."),
                ],
                className="grid-2",
            ),
        ],
        id="tipos",
    )


def vehiculos() -> html.Section:
    return html.Section(
        [
            html.H2("4. ¿Qué vehículos se accidentan y en qué tipo de calles?"),
            _pregunta("En calles suburbanas en mal estado, ¿qué vehículos están más involucrados y "
                      "en qué tipo de camino? ¿Cómo se reparten los accidentes suburbanos según la superficie?"),
            html.Div(
                [
                    _figura("g-veh-suburbana", "Vehículos involucrados por tipo de zona suburbana"),
                    _figura("g-veh-urbana", "Vehículos involucrados por tipo de zona urbana"),
                ],
                className="grid-2",
            ),
            _figura("g-superficie", "Accidentes suburbanos por tipo de camino, según condición de la calle"),
        ],
        id="vehiculos",
    )


def gravedad() -> html.Section:
    return html.Section(
        [
            html.H2("5. Gravedad y letalidad"),
            _pregunta("Hipótesis inicial: en terracería se maneja más lento y los choques son menos "
                      "graves. ¿Lo confirman los datos?"),
            _figura("g-gravedad", "Distribución de la gravedad por condición de la calle"),
            html.Div(
                [
                    _figura("g-letalidad-zona", "Letalidad por tipo de vía",
                            "Letalidad = % de accidentes con al menos una víctima mortal."),
                    _figura("g-victimas", "Víctimas en el grupo seleccionado por tipo de usuario"),
                ],
                className="grid-2",
            ),
            _figura("g-causas", "Causa atribuida al accidente: no pavimentada vs. pavimentada",
                    "Reproduce la tabla de causas del notebook (sin filtro de grupo)."),
        ],
        id="gravedad",
    )


def tiempo() -> html.Section:
    return html.Section(
        [
            html.H2("6. ¿Hay un patrón claro en la hora del día?"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H4("Concentración por hora y día de la semana", className="fig-title"),
                                    dcc.RadioItems(
                                        id="f-heatmap",
                                        options=[
                                            {"label": "Todos los accidentes", "value": "todos"},
                                            {"label": "Solo fatales", "value": "fatales"},
                                        ],
                                        value="todos",
                                        inline=True,
                                        className="radio",
                                    ),
                                ],
                                className="fig-header",
                            ),
                            _graph("g-heatmap"),
                            html.Figcaption("Con «Solo fatales» las celdas tienen pocos casos: "
                                            "leer como tendencia, no como cifra exacta."),
                        ],
                        className="card",
                    ),
                    html.Div(
                        [
                            _figura("g-horas", "Distribución horaria por condición de la calle"),
                            _figura("g-franja", "Letalidad por franja horaria"),
                        ],
                    ),
                ],
                className="grid-2",
            ),
            _figura("g-mensual", "Estacionalidad mensual por condición de la calle"),
        ],
        id="tiempo",
    )


def hallazgos() -> html.Section:
    return html.Section(
        [
            html.H2("7. Hallazgos, recomendaciones y siguientes pasos"),
            html.Div(
                [
                    html.Div([html.H3("Hallazgos (se recalculan con los filtros)"),
                              html.Ul(id="lista-hallazgos")], className="card"),
                    html.Div(
                        [
                            html.H3("Recomendaciones para SEDATU"),
                            html.Ul(
                                [
                                    html.Li("Priorizar la pavimentación de caminos rurales y tramos de "
                                            "carretera estatal sin pavimento, donde la letalidad es mayor."),
                                    html.Li("Acompañar la obra con señalamiento, iluminación y barreras de "
                                            "contención, por el peso de los choques contra objeto fijo y volcaduras."),
                                    html.Li("Programas de bacheo en zonas urbanas: la mayoría de los choques "
                                            "por mala condición del camino ocurren en vías pavimentadas."),
                                    html.Li("Iluminación y operativos en horario nocturno y fines de semana."),
                                ]
                            ),
                        ],
                        className="card",
                    ),
                ],
                className="grid-2",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Limitaciones"),
                            html.Ul(
                                [
                                    html.Li("Un solo año (2015) y 16 de 32 entidades."),
                                    html.Li("La causa la asigna la autoridad en el lugar; la mala "
                                            "condición del camino probablemente está subregistrada."),
                                    html.Li("Sin datos de exposición (km de calles, aforo vehicular): "
                                            "no se pueden calcular tasas por km o por habitante."),
                                    html.Li("Pocos accidentes fatales en mal estado: celdas pequeñas."),
                                ]
                            ),
                        ],
                        className="card",
                    ),
                    html.Div(
                        [
                            html.H3("Siguientes pasos"),
                            html.Ul(
                                [
                                    html.Li("Agregar más años de ATUS y las 32 entidades."),
                                    html.Li("Cruzar con la Red Nacional de Caminos (INEGI) e índice de "
                                            "marginación (CONAPO) a nivel municipal."),
                                    html.Li("Calcular tasas normalizadas y mapas municipales de riesgo."),
                                    html.Li("Modelo de clasificación de gravedad para cuantificar el efecto "
                                            "de la condición de la calle controlando por otros factores."),
                                ]
                            ),
                        ],
                        className="card",
                    ),
                ],
                className="grid-2",
            ),
        ],
        id="hallazgos",
    )


def footer() -> html.Footer:
    return html.Footer(
        html.P(
            [
                "Fuente: INEGI, Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas "
                "(ATUS) 2015. Análisis: ",
                html.Code("notebooks/data_analysis_table.ipynb"),
                ". Universidad de Sonora.",
            ]
        )
    )


def build_layout() -> html.Div:
    return html.Div(
        [
            navbar(),
            html.Div(filtros(), className="filters-bar"),
            html.Main(
                [portada(), planteamiento(), estrategia(), tipos(), vehiculos(), gravedad(),
                 tiempo(), hallazgos(), footer()],
                className="container",
            ),
        ]
    )
