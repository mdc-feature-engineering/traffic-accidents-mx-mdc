"""Dashboard Dash: accidentes de tránsito en calles en mal estado (México, 2015)."""

from __future__ import annotations

import os

from dash import Dash, Input, Output, html
import pandas as pd

from dashboard import figures as F
from dashboard.data import BUENO, filter_base, load_data, select_group
from dashboard.layout import build_layout

DF = load_data()

app = Dash(__name__, title="Accidentes en calles en mal estado · México 2015")
app.layout = build_layout()
server = app.server


def _tasa(df: pd.DataFrame) -> float:
    return df["ES_FATAL"].mean() * 100 if len(df) else 0.0


def hallazgos(base_all: pd.DataFrame, base: pd.DataFrame, grupo: str) -> list[html.Li]:
    sel = select_group(base, grupo)
    sel_all = select_group(base_all, grupo)
    bueno_all = base_all[base_all["CONDICION_CALLE"] == BUENO]
    if sel.empty:
        return [html.Li("No hay accidentes para los filtros seleccionados.")]

    items = []
    t_sel, t_bueno = _tasa(sel_all), _tasa(bueno_all)
    if t_bueno:
        r = t_sel / t_bueno
        comparacion = (
            f"{r:.1f} veces más probable que un choque sea fatal"
            if r >= 1
            else f"la probabilidad de que un choque sea fatal es {(1 - r) * 100:.0f}% menor"
        )
        items.append(
            f"Letalidad de {t_sel:.1f}% en «{grupo}» frente a {t_bueno:.1f}% en buen estado: "
            f"{comparacion}."
        )

    tipos = sel["TIPACCID"].value_counts(normalize=True) * 100
    items.append(f"El tipo de choque más común es «{tipos.index[0]}» ({tipos.iloc[0]:.0f}% del grupo).")

    bueno = base[base["CONDICION_CALLE"] == BUENO]
    if not bueno.empty:
        p_bueno = bueno["TIPACCID"].value_counts(normalize=True) * 100
        ratio = (tipos / p_bueno).dropna()
        ratio = ratio[sel["TIPACCID"].value_counts().reindex(ratio.index) >= 20]
        if not ratio.empty:
            top = ratio.idxmax()
            items.append(
                f"«{top}» está sobrerrepresentado: {tipos[top]:.1f}% en el grupo vs. "
                f"{p_bueno[top]:.1f}% en buen estado (×{ratio[top]:.1f})."
            )

    zonas = sel_all.groupby("ZONA_VIAL")["ES_FATAL"].agg(["mean", "size"])
    zonas = zonas[(zonas["size"] >= 30) & (zonas.index != "No especificada")]
    if not zonas.empty:
        z = zonas["mean"].idxmax()
        items.append(
            f"La vía más letal es «{z}»: {zonas.loc[z, 'mean'] * 100:.1f}% de "
            f"{int(zonas.loc[z, 'size']):,} accidentes fueron fatales."
        )

    horas = sel["HORA"].dropna()
    if not horas.empty:
        noche = horas.between(18, 23).mean() * 100
        pico = int(horas.mode().iloc[0])
        finde = sel["DIASEMANA"].isin(["Sábado", "Domingo"]).mean() * 100
        items.append(
            f"Hora pico: {pico:02d}:00. El {noche:.0f}% de los choques ocurre entre 18:00 y 23:59, "
            f"y el {finde:.0f}% en sábado o domingo."
        )

    victimas = int(sel["TOTAL_MUERTOS"].sum()), int(sel["TOTAL_HERIDOS"].sum())
    items.append(f"{victimas[0]:,} personas muertas y {victimas[1]:,} heridas en el grupo seleccionado.")
    return [html.Li(t) for t in items]


@app.callback(
    Output("kpi-total", "children"),
    Output("kpi-mal", "children"),
    Output("kpi-muertos", "children"),
    Output("kpi-heridos", "children"),
    Output("kpi-letalidad", "children"),
    Output("g-definicion", "figure"),
    Output("g-top-tipos", "figure"),
    Output("g-tipos-vs", "figure"),
    Output("g-veh-suburbana", "figure"),
    Output("g-veh-urbana", "figure"),
    Output("g-superficie", "figure"),
    Output("g-gravedad", "figure"),
    Output("g-letalidad-zona", "figure"),
    Output("g-victimas", "figure"),
    Output("g-causas", "figure"),
    Output("g-horas", "figure"),
    Output("g-franja", "figure"),
    Output("g-mensual", "figure"),
    Output("lista-hallazgos", "children"),
    Input("f-grupo", "value"),
    Input("f-entidad", "value"),
    Input("f-gravedad", "value"),
)
def actualizar(grupo, entidades, gravedades):
    base_all = filter_base(DF, entidades)
    base = filter_base(DF, entidades, gravedades or [])
    if not gravedades:
        base = base.iloc[0:0]
    sel = select_group(base, grupo)
    color = F.COLORES[grupo]

    mal = base[base["MAL_ESTADO"]]
    pct_mal = len(mal) / len(base) * 100 if len(base) else 0
    t_mal = _tasa(base_all[base_all["MAL_ESTADO"]])
    t_bueno = _tasa(base_all[base_all["CONDICION_CALLE"] == BUENO])

    return (
        f"{len(base):,}",
        html.Span([f"{len(mal):,} ", html.Small(f"({pct_mal:.1f}%)")]),
        f"{int(mal['TOTAL_MUERTOS'].sum()):,}",
        f"{int(mal['TOTAL_HERIDOS'].sum()):,}",
        html.Span([f"{t_mal:.1f}% ", html.Small(f"vs {t_bueno:.1f}%")]),
        F.fig_definicion(base),
        F.fig_top_tipos(sel, color),
        F.fig_tipos_vs_bueno(base, sel, grupo),
        F.fig_vehiculos(sel, "SUBURBANA"),
        F.fig_vehiculos(sel, "URBANA"),
        F.fig_superficie_suburbana(base),
        F.fig_gravedad(base_all),
        F.fig_letalidad_zona(base_all, select_group(base_all, grupo), grupo),
        F.fig_victimas(sel),
        F.fig_causas(base),
        F.fig_horas(base),
        F.fig_franja_letalidad(base_all),
        F.fig_mensual(base),
        hallazgos(base_all, base, grupo),
    )


@app.callback(
    Output("g-heatmap", "figure"),
    Input("f-grupo", "value"),
    Input("f-entidad", "value"),
    Input("f-gravedad", "value"),
    Input("f-heatmap", "value"),
)
def actualizar_heatmap(grupo, entidades, gravedades, modo):
    base = filter_base(DF, entidades, gravedades or [])
    if not gravedades:
        base = base.iloc[0:0]
    return F.fig_heatmap(select_group(base, grupo), modo == "fatales")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 8050)),
        debug=os.environ.get("DASH_DEBUG", "1") == "1",
    )
