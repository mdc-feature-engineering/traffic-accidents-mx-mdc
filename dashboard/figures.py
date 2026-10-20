"""Constructores de figuras Plotly: cada función recibe DataFrames ya filtrados."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.data import (
    BUENO,
    CONDICIONES,
    DIAS,
    FRANJAS,
    GRAVEDADES,
    MAL_ESTADO,
    MESES,
    NO_PAV,
    PAV_MAL,
    SIN_ZONA,
    VEHICULOS,
    VICTIMAS,
)

COLORES = {NO_PAV: "#a0522d", PAV_MAL: "#c0392b", BUENO: "#95a5a6", MAL_ESTADO: "#c0392b"}
COLORES_GRAVEDAD = {"Fatal": "#641e16", "No fatal": "#e67e22", "Sólo Daños": "#d5d8dc"}
PALETA = px.colors.qualitative.Safe
FUENTE = "Inter, Segoe UI, Helvetica, Arial, sans-serif"


def _style(fig: go.Figure, height: int = 420, **layout) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(family=FUENTE, size=13, color="#2c3e50"),
        margin=dict(l=10, r=20, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
        hoverlabel=dict(font_family=FUENTE),
    )
    fig.update_layout(**layout)
    return fig


def _vacia(mensaje: str = "Sin datos para los filtros seleccionados") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=mensaje, showarrow=False, font=dict(size=15, color="#7f8c8d"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _style(fig, height=300)


def _pct(series: pd.Series) -> pd.Series:
    total = series.sum()
    return series / total * 100 if total else series * 0


def fig_definicion(base: pd.DataFrame) -> go.Figure:
    conteo = base["CONDICION_CALLE"].value_counts().reindex([NO_PAV, PAV_MAL], fill_value=0)
    total = len(base)
    fig = go.Figure(
        go.Bar(
            x=conteo.values,
            y=conteo.index,
            orientation="h",
            marker_color=[COLORES[c] for c in conteo.index],
            text=[f"{v:,} ({v / total * 100:.1f}% del total)" if total else "" for v in conteo],
            textposition="auto",
            hovertemplate="%{y}: %{x:,} accidentes<extra></extra>",
        )
    )
    fig.update_xaxes(title="Accidentes")
    return _style(fig, height=220, showlegend=False)


def fig_top_tipos(sel: pd.DataFrame, color: str, n: int = 5) -> go.Figure:
    if sel.empty:
        return _vacia()
    pct = _pct(sel["TIPACCID"].value_counts())
    conteo = sel["TIPACCID"].value_counts().head(n)[::-1]
    fig = go.Figure(
        go.Bar(
            x=conteo.values,
            y=conteo.index,
            orientation="h",
            marker_color=color,
            text=[f"{v:,} ({pct[k]:.1f}%)" for k, v in conteo.items()],
            textposition="auto",
            hovertemplate="%{y}<br>%{x:,} accidentes<extra></extra>",
        )
    )
    fig.update_xaxes(title="Número de accidentes")
    return _style(fig, height=380, showlegend=False)


def fig_tipos_vs_bueno(base: pd.DataFrame, sel: pd.DataFrame, etiqueta: str, n: int = 8):
    bueno = base[base["CONDICION_CALLE"] == BUENO]
    if sel.empty or bueno.empty:
        return _vacia()
    p_sel = _pct(sel["TIPACCID"].value_counts())
    p_bueno = _pct(bueno["TIPACCID"].value_counts()).reindex(p_sel.index, fill_value=0)
    tipos = p_sel.head(n).index[::-1]
    ratio = (p_sel / p_bueno.replace(0, float("nan"))).reindex(tipos)
    fig = go.Figure(
        [
            go.Bar(
                name=BUENO,
                y=tipos,
                x=p_bueno[tipos],
                orientation="h",
                marker_color=COLORES[BUENO],
                hovertemplate="%{y}<br>Buen estado: %{x:.1f}%<extra></extra>",
            ),
            go.Bar(
                name=etiqueta,
                y=tipos,
                x=p_sel[tipos],
                orientation="h",
                marker_color=COLORES.get(etiqueta, COLORES[MAL_ESTADO]),
                text=[f"×{r:.1f}" if pd.notna(r) else "" for r in ratio],
                textposition="outside",
                hovertemplate="%{y}<br>" + etiqueta + ": %{x:.1f}%<extra></extra>",
            ),
        ]
    )
    fig.update_xaxes(title="% de los accidentes de cada grupo", ticksuffix="%")
    return _style(fig, height=440, barmode="group")


def fig_vehiculos(sel: pd.DataFrame, columna: str, top: int = 6) -> go.Figure:
    datos = sel[sel[columna] != SIN_ZONA]
    if datos.empty:
        return _vacia("Sin accidentes en este tipo de zona para los filtros seleccionados")
    tabla = datos.groupby(columna)[list(VEHICULOS)].sum().T.rename(index=VEHICULOS)
    tabla = tabla.loc[tabla.sum(axis=1).sort_values(ascending=False).index[:top]]
    fig = go.Figure(
        [
            go.Bar(
                name=zona,
                x=tabla.index,
                y=tabla[zona],
                marker_color=PALETA[i % len(PALETA)],
                hovertemplate="%{x}<br>" + zona + ": %{y:,} vehículos<extra></extra>",
            )
            for i, zona in enumerate(tabla.columns)
        ]
    )
    fig.update_yaxes(title="Vehículos involucrados")
    return _style(fig, barmode="stack")


def fig_superficie_suburbana(base: pd.DataFrame) -> go.Figure:
    datos = base[base["SUBURBANA"] != SIN_ZONA]
    if datos.empty:
        return _vacia()
    tabla = pd.crosstab(datos["CONDICION_CALLE"], datos["SUBURBANA"], normalize="index") * 100
    n = datos["CONDICION_CALLE"].value_counts()
    tabla = tabla.reindex([c for c in CONDICIONES if c in tabla.index])
    etiquetas = [f"{c} (n={n.get(c, 0):,})" for c in tabla.index]
    fig = go.Figure(
        [
            go.Bar(
                name=zona,
                y=etiquetas,
                x=tabla[zona],
                orientation="h",
                marker_color=PALETA[i % len(PALETA)],
                text=[f"{v:.0f}%" if v >= 6 else "" for v in tabla[zona]],
                textposition="inside",
                hovertemplate="%{y}<br>" + zona + ": %{x:.1f}%<extra></extra>",
            )
            for i, zona in enumerate(tabla.columns)
        ]
    )
    fig.update_xaxes(title="% de accidentes suburbanos", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(autorange="reversed")
    return _style(fig, height=320, barmode="stack")


def fig_gravedad(base: pd.DataFrame) -> go.Figure:
    if base.empty:
        return _vacia()
    tabla = pd.crosstab(base["CONDICION_CALLE"], base["CLASACC"], normalize="index") * 100
    tabla = tabla.reindex(columns=GRAVEDADES, fill_value=0)
    tabla = tabla.reindex([c for c in CONDICIONES if c in tabla.index])
    etiquetas = [f"{c} (letalidad {tabla.loc[c, 'Fatal']:.1f}%)" for c in tabla.index]
    fig = go.Figure(
        [
            go.Bar(
                name=g,
                y=etiquetas,
                x=tabla[g],
                orientation="h",
                marker_color=COLORES_GRAVEDAD[g],
                text=[f"{v:.1f}%" if v >= 2 else "" for v in tabla[g]],
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate="%{y}<br>" + g + ": %{x:.2f}%<extra></extra>",
            )
            for g in GRAVEDADES
        ]
    )
    fig.update_xaxes(title="% de accidentes", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(autorange="reversed")
    return _style(fig, height=300, barmode="stack")


def fig_letalidad_zona(base: pd.DataFrame, sel: pd.DataFrame, etiqueta: str) -> go.Figure:
    bueno = base[base["CONDICION_CALLE"] == BUENO]
    if sel.empty:
        return _vacia()
    trazas = []
    for nombre, datos in [(BUENO, bueno), (etiqueta, sel)]:
        g = datos.groupby("ZONA_VIAL")["ES_FATAL"].agg(["mean", "size", "sum"])
        g = g.drop(index="No especificada", errors="ignore").sort_index()
        trazas.append(
            go.Bar(
                name=nombre,
                x=g.index,
                y=g["mean"] * 100,
                marker_color=COLORES.get(nombre, COLORES[MAL_ESTADO]),
                text=[f"{v * 100:.1f}%" for v in g["mean"]],
                textposition="outside",
                customdata=g[["sum", "size"]].values,
                hovertemplate="%{x}<br>Letalidad: %{y:.2f}%"
                "<br>%{customdata[0]:,} fatales de %{customdata[1]:,}<extra>"
                + nombre
                + "</extra>",
            )
        )
    fig = go.Figure(trazas)
    fig.update_yaxes(title="% de accidentes fatales", ticksuffix="%")
    return _style(fig, barmode="group")


def fig_victimas(sel: pd.DataFrame) -> go.Figure:
    if sel.empty:
        return _vacia()
    filas = {k: (sel[m].sum(), sel[h].sum()) for k, (m, h) in VICTIMAS.items()}
    tabla = pd.DataFrame(filas, index=["Muertos", "Heridos"]).T
    tabla = tabla[tabla.sum(axis=1) > 0].sort_values("Heridos")
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=("Muertos", "Heridos"))
    for i, (col, color) in enumerate([("Muertos", "#641e16"), ("Heridos", "#e67e22")], start=1):
        fig.add_trace(
            go.Bar(
                x=tabla[col],
                y=tabla.index,
                orientation="h",
                marker_color=color,
                text=tabla[col].astype(int),
                textposition="auto",
                name=col,
                hovertemplate="%{y}: %{x:,}<extra>" + col + "</extra>",
            ),
            row=1,
            col=i,
        )
    return _style(fig, height=340, showlegend=False)


def fig_causas(base: pd.DataFrame) -> go.Figure:
    if base.empty:
        return _vacia()
    tabla = pd.crosstab(base["CAPAROD"], base["CAUSAACCI"], normalize="index") * 100
    conductor = tabla.pop("Conductor") if "Conductor" in tabla else None
    colores = {"No Pavimentada": COLORES[NO_PAV], "Pavimentada": COLORES[BUENO]}
    fig = go.Figure(
        [
            go.Bar(
                name=superficie,
                x=tabla.columns,
                y=tabla.loc[superficie],
                marker_color=colores.get(superficie),
                text=[f"{v:.1f}%" for v in tabla.loc[superficie]],
                textposition="outside",
                hovertemplate="%{x}: %{y:.2f}%<extra>" + superficie + "</extra>",
            )
            for superficie in tabla.index
        ]
    )
    if conductor is not None:
        nota = " · ".join(f"{s}: {v:.1f}%" for s, v in conductor.items())
        fig.add_annotation(
            text=f"Causa 'Conductor' (no graficada): {nota}",
            xref="paper", yref="paper", x=0, y=1.12, yanchor="bottom",
            showarrow=False, font=dict(size=12, color="#7f8c8d"),
        )
    fig.update_yaxes(title="% de accidentes por tipo de superficie", ticksuffix="%")
    return _style(fig, barmode="group", margin=dict(l=10, r=20, t=70, b=10))


def fig_heatmap(sel: pd.DataFrame, solo_fatales: bool) -> go.Figure:
    datos = sel[sel["ES_FATAL"]] if solo_fatales else sel
    datos = datos.dropna(subset=["HORA", "DIASEMANA"])
    if datos.empty:
        return _vacia()
    tabla = (
        pd.crosstab(datos["HORA"].astype(int), datos["DIASEMANA"])
        .reindex(index=range(24), columns=DIAS, fill_value=0)
    )
    fig = go.Figure(
        go.Heatmap(
            z=tabla.values,
            x=tabla.columns,
            y=[f"{h:02d}:00" for h in tabla.index],
            colorscale="Reds",
            colorbar=dict(title="Accidentes"),
            hovertemplate="%{x} %{y}<br>%{z} accidentes<extra></extra>",
            xgap=1,
            ygap=1,
        )
    )
    fig.update_yaxes(autorange="reversed", dtick=2)
    return _style(fig, height=560)


def fig_horas(base: pd.DataFrame) -> go.Figure:
    datos = base.dropna(subset=["HORA"])
    if datos.empty:
        return _vacia()
    fig = go.Figure()
    for cond in CONDICIONES:
        sub = datos[datos["CONDICION_CALLE"] == cond]
        serie = _pct(sub["HORA"].astype(int).value_counts()).reindex(range(24), fill_value=0)
        fig.add_trace(
            go.Scatter(
                x=serie.index,
                y=serie.values,
                mode="lines+markers",
                name=f"{cond} (n={len(sub):,})",
                line=dict(color=COLORES[cond], width=3 if cond != BUENO else 2,
                          dash="dot" if cond == BUENO else "solid"),
                hovertemplate="%{x}:00 → %{y:.1f}%<extra>" + cond + "</extra>",
            )
        )
    fig.update_xaxes(title="Hora del día", dtick=2)
    fig.update_yaxes(title="% de accidentes del grupo", ticksuffix="%")
    return _style(fig)


def fig_franja_letalidad(base: pd.DataFrame) -> go.Figure:
    datos = base.dropna(subset=["FRANJA_HORARIA"])
    if datos.empty:
        return _vacia()
    grupo = datos["MAL_ESTADO"].map({True: MAL_ESTADO, False: BUENO})
    tabla = datos.groupby([grupo, "FRANJA_HORARIA"], observed=False)["ES_FATAL"].agg(
        ["mean", "sum", "size"]
    )
    fig = go.Figure()
    for nombre in [BUENO, MAL_ESTADO]:
        if nombre not in tabla.index.get_level_values(0):
            continue
        t = tabla.loc[nombre].reindex(FRANJAS)
        fig.add_trace(
            go.Bar(
                name=nombre,
                x=t.index,
                y=t["mean"] * 100,
                marker_color=COLORES[nombre],
                text=[f"{v * 100:.1f}%" for v in t["mean"].fillna(0)],
                textposition="outside",
                customdata=t[["sum", "size"]].fillna(0).values,
                hovertemplate="%{x}<br>Letalidad: %{y:.2f}%"
                "<br>%{customdata[0]:,.0f} fatales de %{customdata[1]:,.0f}<extra>"
                + nombre
                + "</extra>",
            )
        )
    fig.update_yaxes(title="% de accidentes fatales", ticksuffix="%")
    return _style(fig, barmode="group")


def fig_mensual(base: pd.DataFrame) -> go.Figure:
    if base.empty:
        return _vacia()
    fig = go.Figure()
    for cond in CONDICIONES:
        sub = base[base["CONDICION_CALLE"] == cond]
        serie = _pct(sub["MES"].value_counts()).reindex(MESES, fill_value=0)
        fig.add_trace(
            go.Scatter(
                x=[m[:3] for m in serie.index],
                y=serie.values,
                mode="lines+markers",
                name=cond,
                line=dict(color=COLORES[cond], dash="dot" if cond == BUENO else "solid"),
                hovertemplate="%{x}: %{y:.1f}%<extra>" + cond + "</extra>",
            )
        )
    fig.update_yaxes(title="% de accidentes anuales del grupo", ticksuffix="%")
    return _style(fig, height=360)
