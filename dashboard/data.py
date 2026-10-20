"""Carga, limpieza y feature engineering del dataset de accidentes para el dashboard."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "traffic_accidents_mx.xlsx"
SHEET_NAME = "Sheet 1 - atus_tr_cifra_2015"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "accidentes_dashboard.parquet"

NO_PAV = "No pavimentada"
PAV_MAL = "Pavimentada en mal estado"
BUENO = "Buen estado"
MAL_ESTADO = "Todas en mal estado"
CONDICIONES = [NO_PAV, PAV_MAL, BUENO]
GRUPOS = [MAL_ESTADO, NO_PAV, PAV_MAL]

CAUSA_MALA = "Mala condición del camino"
SIN_ZONA = "Sin accidente en esta zona"

GRAVEDADES = ["Fatal", "No fatal", "Sólo Daños"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
FRANJAS = ["Madrugada (0-5)", "Mañana (6-11)", "Tarde (12-17)", "Noche (18-23)"]

VEHICULOS = {
    "AUTOMOVIL": "Automóvil",
    "CAMPASAJ": "Camioneta de pasajeros",
    "MICROBUS": "Microbús",
    "PASCAMION": "Camión de pasajeros",
    "OMNIBUS": "Ómnibus",
    "TRANVIA": "Tranvía",
    "CAMIONETA": "Camioneta de carga",
    "CAMION": "Camión de carga",
    "TRACTOR": "Tractor",
    "FERROCARRI": "Ferrocarril",
    "MOTOCICLET": "Motocicleta",
    "BICICLETA": "Bicicleta",
    "OTROVEHIC": "Otro vehículo",
}

VICTIMAS = {
    "Conductor": ("CONDMUERTO", "CONDHERIDO"),
    "Pasajero": ("PASAMUERTO", "PASAHERIDO"),
    "Peatón": ("PEATMUERTO", "PEATHERIDO"),
    "Ciclista": ("CICLMUERTO", "CICLHERIDO"),
    "Otro": ("OTROMUERTO", "OTROHERIDO"),
    "No especificado": ("NEMUERTO", "NEHERIDO"),
}

ENTIDADES = {
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
}

ZONAS = {
    "Accidente en carretera estatal": "Suburbana: carretera estatal",
    "Accidente en camino rural": "Suburbana: camino rural",
    "Accidentes en otro camino": "Suburbana: otro camino",
    "Accidente en intersección": "Urbana: intersección",
    "Accidente en no intersección": "Urbana: no intersección",
}


def build_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Aplica las transformaciones descritas en la sección 'Estrategia' del dashboard."""
    df = raw.drop(columns=["COBERTURA", "ESTATUS"], errors="ignore").copy()

    no_pav = df["CAPAROD"].eq("No Pavimentada")
    causa_mala = df["CAUSAACCI"].eq(CAUSA_MALA)
    df["CONDICION_CALLE"] = pd.Categorical(
        np.select([no_pav, causa_mala], [NO_PAV, PAV_MAL], default=BUENO),
        categories=CONDICIONES,
    )
    df["MAL_ESTADO"] = no_pav | causa_mala

    df["MES"] = pd.Categorical(df["MES"], categories=MESES, ordered=True)
    df["MES_NUM"] = df["MES"].cat.codes + 1
    df["FECHA"] = pd.to_datetime(
        dict(year=df["ANIO"], month=df["MES_NUM"], day=df["ID_DIA"]), errors="coerce"
    )
    df["DIASEMANA"] = pd.Categorical(df["DIASEMANA"], categories=DIAS, ordered=True)

    df["HORA"] = df["ID_HORA"].where(df["ID_HORA"].between(0, 23))
    df["FRANJA_HORARIA"] = pd.cut(df["HORA"], bins=[-1, 5, 11, 17, 23], labels=FRANJAS)
    df["EDAD"] = df["ID_EDAD"].where(df["ID_EDAD"].between(12, 98))

    muertos = [m for m, _ in VICTIMAS.values()]
    heridos = [h for _, h in VICTIMAS.values()]
    df["TOTAL_MUERTOS"] = df[muertos].sum(axis=1)
    df["TOTAL_HERIDOS"] = df[heridos].sum(axis=1)
    df["ES_FATAL"] = df["CLASACC"].eq("Fatal")
    df["TOTAL_VEHICULOS"] = df[list(VEHICULOS)].sum(axis=1)

    df["ENTIDAD"] = df["ID_ENTIDAD"].map(ENTIDADES)
    zona = df["SUBURBANA"].where(df["SUBURBANA"].ne(SIN_ZONA), df["URBANA"])
    df["ZONA_VIAL"] = zona.map(ZONAS).fillna("No especificada")
    return df


def load_data() -> pd.DataFrame:
    """Lee la caché parquet; si no existe la genera a partir del Excel original."""
    if PROCESSED_PATH.exists():
        return pd.read_parquet(PROCESSED_PATH)
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en {RAW_PATH}. Ejecuta `make data` antes de iniciar."
        )
    print(f"Generando {PROCESSED_PATH.name} a partir del Excel (tarda ~1 minuto)...", flush=True)
    df = build_features(pd.read_excel(RAW_PATH, sheet_name=SHEET_NAME))
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)
    return df


def filter_base(df: pd.DataFrame, entidades: list | None, gravedades: list | None = None):
    """Filtros globales que aplican a todas las condiciones de calle."""
    mask = pd.Series(True, index=df.index)
    if entidades:
        mask &= df["ID_ENTIDAD"].isin(entidades)
    if gravedades:
        mask &= df["CLASACC"].isin(gravedades)
    return df[mask]


def select_group(df: pd.DataFrame, grupo: str) -> pd.DataFrame:
    """Subconjunto de calles en mal estado según el grupo elegido."""
    if grupo == MAL_ESTADO:
        return df[df["MAL_ESTADO"]]
    return df[df["CONDICION_CALLE"] == grupo]
