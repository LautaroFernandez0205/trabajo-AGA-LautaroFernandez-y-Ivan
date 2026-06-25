import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds

st.set_page_config(
    page_title="Optimización Wi-Fi",
    page_icon="📶",
    layout="wide"
)

st.title("📶 Optimización de Cobertura Wi-Fi del Campus")

st.markdown("""
### Objetivo

Determinar la cantidad óptima de:

- Antenas Tipo A
- Antenas Tipo B
- Repetidores
- Baterías

para maximizar la cobertura Wi-Fi respetando las restricciones de presupuesto,
energía, espacio y requisitos mínimos.
""")

# ==========================
# ESTILO
# ==========================

st.markdown("""
<style>
.stApp {
    background-color: #0A1931;
}

h1, h2, h3, h4, h5, h6, p, label, div {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# PARÁMETROS
# ==========================

st.subheader("⚙️ Parámetros del Problema")

col1, col2 = st.columns(2)

with col1:
    presupuesto = st.number_input(
        "Presupuesto máximo ($)",
        min_value=0,
        value=7000
    )

    energia_max = st.number_input(
        "Energía máxima",
        min_value=0,
        value=220
    )

    espacio_max = st.number_input(
        "Espacio máximo",
        min_value=0,
        value=300
    )

with col2:
    min_baterias = st.number_input(
        "Mínimo de baterías",
        min_value=0,
        value=5
    )

    min_antenas = st.number_input(
        "Mínimo de antenas",
        min_value=0,
        value=2
    )

# ==========================
# TABLA EDITABLE
# ==========================

st.subheader("📋 Datos de los Equipos")

datos = pd.DataFrame({
    "Equipo": [
        "Antena Tipo A",
        "Antena Tipo B",
        "Repetidor",
        "Batería"
    ],
    "Usuarios cubiertos": [120, 200, 80, 20],
    "Precio": [300, 500, 150, 100],
    "Energía": [8, 15, 4, 2],
    "Espacio": [10, 12, 1, 1]
})

datos = st.data_editor(
    datos,
    use_container_width=True,
    num_rows="fixed"
)

cov_A = datos.iloc[0]["Usuarios cubiertos"]
precio_A = datos.iloc[0]["Precio"]
energia_A = datos.iloc[0]["Energía"]
espacio_A = datos.iloc[0]["Espacio"]

cov_B = datos.iloc[1]["Usuarios cubiertos"]
precio_B = datos.iloc[1]["Precio"]
energia_B = datos.iloc[1]["Energía"]
espacio_B = datos.iloc[1]["Espacio"]

cov_R = datos.iloc[2]["Usuarios cubiertos"]
precio_R = datos.iloc[2]["Precio"]
energia_R = datos.iloc[2]["Energía"]
espacio_R = datos.iloc[2]["Espacio"]

cov_Bat = datos.iloc[3]["Usuarios cubiertos"]
precio_Bat = datos.iloc[3]["Precio"]
energia_Bat = datos.iloc[3]["Energía"]
espacio_Bat = datos.iloc[3]["Espacio"]

# ==========================
# BOTÓN
# ==========================

if st.button("🚀 Ejecutar Optimización"):

    c = [
        -cov_A,
        -cov_B,
        -cov_R,
        -cov_Bat
    ]

    A = [
        [precio_A, precio_B, precio_R, precio_Bat],
        [energia_A, energia_B, energia_R, energia_Bat],
        [espacio_A, espacio_B, espacio_R, espacio_Bat],
        [0, 0, 0, 1],
        [1, 1, 0, 0]
    ]

    bu = [
        presupuesto,
        energia_max,
        espacio_max,
        np.inf,
        np.inf
    ]

    bl = [
        -np.inf,
        -np.inf,
        -np.inf,
        min_baterias,
        min_antenas
    ]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds(
        [0, 0, 0, 0],
        [np.inf, np.inf, np.inf, np.inf]
    )

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=[1, 1, 1, 1]
    )

    st.subheader("Resultado")

    if res.success:

        antena_a = int(res.x[0])
        antena_b = int(res.x[1])
        repetidor = int(res.x[2])
        bateria = int(res.x[3])

        cobertura = int(-res.fun)

        costo = (
            precio_A * antena_a +
            precio_B * antena_b +
            precio_R * repetidor +
            precio_Bat * bateria
        )

        energia = (
            energia_A * antena_a +
            energia_B * antena_b +
            energia_R * repetidor +
            energia_Bat * bateria
        )

        espacio = (
            espacio_A * antena_a +
            espacio_B * antena_b +
            espacio_R * repetidor +
            espacio_Bat * bateria
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Usuarios cubiertos", cobertura)
        col2.metric("Costo utilizado", f"${costo}")
        col3.metric("Energía utilizada", energia)
        col4.metric("Espacio utilizado", espacio)

        resultados = pd.DataFrame({
            "Equipo": [
                "Antena Tipo A",
                "Antena Tipo B",
                "Repetidor",
                "Batería"
            ],
            "Cantidad óptima": [
                antena_a,
                antena_b,
                repetidor,
                bateria
            ]
        })

        st.subheader("Cantidad óptima de equipos")
        st.dataframe(resultados, use_container_width=True)

        st.subheader("Gráfico")
        st.bar_chart(resultados.set_index("Equipo"))

        st.success("Optimización completada correctamente")

    else:
        st.error("No existe una solución factible para los parámetros ingresados.")
