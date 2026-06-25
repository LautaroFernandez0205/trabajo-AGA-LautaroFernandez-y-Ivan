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

# ------------------------
# Datos del problema
# ------------------------

datos = pd.DataFrame({
    "Equipo": ["Antena Tipo A", "Antena Tipo B", "Repetidor", "Batería"],
    "Cobertura": [120, 200, 80, 20],
    "Precio": [300, 500, 150, 100],
    "Energía": [8, 15, 4, 2],
    "Espacio": [10, 12, 1, 1]
})

st.subheader("Datos del problema")
st.dataframe(datos, use_container_width=True)

# ------------------------
# Modelo MILP
# ------------------------

c = [-120, -200, -80, -20]

A = [
    [300, 500, 150, 100],  # presupuesto
    [8, 15, 4, 2],         # energía
    [10, 12, 1, 1],        # espacio
    [0, 0, 0, 1],          # mínimo 5 baterías
    [1, 1, 0, 0]           # mínimo 2 antenas
]

bu = [7000, 220, 300, np.inf, np.inf]
bl = [-np.inf, -np.inf, -np.inf, 5, 2]

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

# ------------------------
# Resultados
# ------------------------

st.subheader("Resultado de la Optimización")

if res.success:

    antena_a = int(res.x[0])
    antena_b = int(res.x[1])
    repetidor = int(res.x[2])
    bateria = int(res.x[3])

    cobertura = int(-res.fun)

    costo = (
        300 * antena_a +
        500 * antena_b +
        150 * repetidor +
        100 * bateria
    )

    energia = (
        8 * antena_a +
        15 * antena_b +
        4 * repetidor +
        2 * bateria
    )

    espacio = (
        10 * antena_a +
        12 * antena_b +
        repetidor +
        bateria
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Cobertura Máxima", cobertura)
    col2.metric("Costo Utilizado", f"${costo}")
    col3.metric("Energía Utilizada", energia)
    col4.metric("Espacio Utilizado", espacio)

    resultados = pd.DataFrame({
        "Equipo": [
            "Antena Tipo A",
            "Antena Tipo B",
            "Repetidor",
            "Batería"
        ],
        "Cantidad Óptima": [
            antena_a,
            antena_b,
            repetidor,
            bateria
        ]
    })

    st.subheader("Cantidad Óptima de Equipos")
    st.dataframe(resultados, use_container_width=True)

    st.subheader("Gráfico")
    st.bar_chart(resultados.set_index("Equipo"))

    st.success(res.message)

else:
    st.error("No se encontró una solución factible.")

# ------------------------
# Modelo matemático
# ------------------------

st.subheader("Modelo Matemático")

st.latex(
    r"Max \; Z = 120A + 200B + 80R + 20Bat"
)

st.markdown("Sujeto a:")

st.latex(
    r"300A + 500B + 150R + 100Bat \leq 7000"
)

st.latex(
    r"8A + 15B + 4R + 2Bat \leq 220"
)

st.latex(
    r"10A + 12B + R + Bat \leq 300"
)

st.latex(
    r"Bat \geq 5"
)

st.latex(
    r"A + B \geq 2"
)

st.latex(
    r"A,B,R,Bat \in \mathbb{Z}_{\geq 0}"
)
st.latex(
r"A,B,R,Bat \in \mathbb{Z}_{\geq 0}"
)
