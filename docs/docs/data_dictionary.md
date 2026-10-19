# Diccionario de Datos: Estudio de Accidentes de Tránsito en México

Este diccionario detalla las variables clave del conjunto de datos utilizadas en el prototipo de análisis (EDA) enfocado en pavimentación y gobiernos municipales.

## 1. Variables de Infraestructura y Entorno

* **`CAPAROD`** (Tipo: Texto / Categórica)
  * **Descripción:** Característica o condición de la superficie de rodamiento donde ocurrió el accidente.
  * **Valores principales:** "Pavimentada", "No Pavimentada".
  * **Uso analítico:** Variable central del estudio para comparar la siniestralidad, tipos de choques y gravedad entre vías pavimentadas y de terracería.

* **`SUBURBANA`** (Tipo: Texto / Categórica)
  * **Descripción:** Clasificación del entorno suburbano o rural donde se registra el incidente.
  * **Valores principales:** "Accidente en carretera estatal", "Accidente en camino rural", "Accidentes en otro camino", "Sin accidente en esta zona".
  * **Uso analítico:** Permite aislar y analizar los accidentes ocurridos específicamente en las periferias y caminos rurales municipales.

* **`URBANA`** (Tipo: Texto / Categórica)
  * **Descripción:** Clasificación del entorno urbano del incidente (intersecciones, no intersecciones).

## 2. Variables de Siniestralidad y Gravedad

* **`TIPACCID`** (Tipo: Texto / Categórica)
  * **Descripción:** Tipo específico del choque o accidente de tránsito.
  * **Ejemplos de valores:** "Colisión con vehículo automotor", "Colisión con objeto fijo", "Volcadura", "Salida del camino", "Colisión con peatón (atropellamiento)", etc.
  * **Uso analítico:** Identifica qué dinámicas de accidentes predominan según el tipo de infraestructura vial.

* **`CLASACC`** (Tipo: Texto / Categórica)
  * **Descripción:** Clase o gravedad global del accidente de tránsito.
  * **Valores principales:** "Fatal", "No fatal", "Sólo Daños".
  * **Uso analítico:** Permite evaluar y contrastar el nivel de riesgo y la hipótesis de letalidad en calles pavimentadas frente a no pavimentadas.

* **`CAUSAACCI`** (Tipo: Texto / Categórica)
  * **Descripción:** Causa principal atribuida al accidente.
  * **Ejemplos de valores:** "Conductor", "Mala condición del camino", "Falla del vehículo", "Peatón o pasajero".
  * **Uso analítico:** Evalúa el impacto de la infraestructura deficiente (como baches o pavimentos descuidados) frente a otros factores.

## 3. Variables de Parque Vehicular

* **`AUTOMOVIL`**, **`CAMIONETA`**, **`MOTOCICLET`**, **`CAMION`**, **`TRACTOR`**, **`BICICLETA`**, etc. (Tipo: Numérico / Conteo)
  * **Descripción:** Cantidad de unidades de cada tipo de vehículo involucradas directamente en el accidente.
  * **Uso analítico:** Determina qué tipo de transporte concentra mayor siniestralidad en los diferentes tipos de caminos suburbanos y rurales.

## 4. Variables Geográficas y Temporales

* **`ID_ENTIDAD`** (Tipo: Numérico / Categórico): Código de identificación de la entidad federativa (estado).
* **`ID_MUNICIPIO`** (Tipo: Numérico / Categórico): Código de identificación del municipio.
* **`ANIO`** (Tipo: Numérico): Año en el que ocurrió el registro del accidente.
* **`MES`** (Tipo: Numérico / Categórico): Mes del incidente.
* **`ID_HORA` / `ID_MINUTO`** (Tipo: Numérico): Hora y minuto en que se reportó el evento.