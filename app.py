# -*- coding: utf-8 -*-


import streamlit as st
import pandas as pd
import altair as alt
import google.generativeai as genai
import os  # Para acceder a variables de entorno (útil en desarrollo local)

# --- Configuración de la API de Gemini ---
try:
    gemini_api_key = st.secrets["gemini_api_key"]
except AttributeError:
    gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error(
        "Error: La clave de API de Gemini no ha sido configurada. "
        "Asegúrate de establecer 'gemini_api_key' en Streamlit Secrets para el despliegue "
        "o como variable de entorno (GEMINI_API_KEY) para desarrollo local."
    )
    st.stop()

genai.configure(api_key=gemini_api_key)
# Inicializa el modelo con nombre explícito según versión recomendada
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# --- Definiciones Globales ---
conceptos = [
    "FC_DEFINICION",
    "FC_ROLES",
    "FC_TECNOLOGIA",
    "FC_APLICACION",
    "FC_BENEFICIOS",
]

nivel_map = {
    0.25: "Básico",
    0.55: "Intermedio",
    0.85: "Avanzado",
}

# Diccionario para nombres legibles de conceptos
conceptos_legibles = {
    "FC_DEFINICION": "la definición de Flipped Classroom",
    "FC_ROLES": "los roles del estudiante y el docente en Flipped Classroom",
    "FC_TECNOLOGIA": "la tecnología usada en Flipped Classroom",
    "FC_APLICACION": "cómo aplicar Flipped Classroom",
    "FC_BENEFICIOS": "los beneficios de Flipped Classroom",
}

# Cargar datos de estudiantes
estudiantes_df = pd.read_csv("estudiantes.csv")


def nota_a_nivel(nota):
    if nota >= 85:
        return 0.85
    elif nota >= 55:
        return 0.55
    else:
        return 0.25


def actualizar_niveles_desde_csv_examen(estudiantes_df_local, uploaded_file):
    if uploaded_file is not None:
        try:
            exam_results_df = pd.read_csv(uploaded_file)
            st.subheader("Resultados del Examen Subido (Últimas Entradas):")
            st.dataframe(exam_results_df.tail(5))

            for index, row in exam_results_df.iterrows():
                estudiante_id = row.get("ID de Estudiante", None)
                nota_examen_general = row.get("Puntuación total", None)

                if pd.notna(estudiante_id) and pd.notna(nota_examen_general):
                    estudiante_id = int(estudiante_id)
                    nota_examen_general = int(nota_examen_general)

                    nuevo_nivel_general = nota_a_nivel(nota_examen_general)
                    idx = estudiantes_df_local[estudiantes_df_local["id"] == estudiante_id].index
                    if not idx.empty:
                        for concepto in conceptos:
                            estudiantes_df_local.loc[idx, concepto] = nuevo_nivel_general
                        st.write(
                            f"Nivel de estudiante **{estudiante_id}** actualizado a **{nivel_map[nuevo_nivel_general]}** basado en examen."
                        )
                    else:
                        st.warning(
                            f"Estudiante con ID **{estudiante_id}** del examen no encontrado en la base de datos local."
                        )
                else:
                    st.warning(
                        f"Fila {index+1} del examen subido: Faltan 'ID de Estudiante' o 'Puntuación total'."
                    )

            estudiantes_df_local.to_csv("estudiantes.csv", index=False)
            st.success(
                "Niveles de conocimiento actualizados desde el examen subido. Por favor, recarga la aplicación si deseas ver los cambios de inmediato."
            )
            return estudiantes_df_local
        except Exception as e:
            st.error(f"Error al procesar el archivo CSV de examen: {e}")
            st.info(
                "Asegúrate de que el archivo es un CSV válido y que las columnas 'ID de Estudiante' y 'Puntuación total' existen."
            )
    return estudiantes_df_local


@st.cache_data(show_spinner=False)
def obtener_contenido_gemini(estudiante_id, concepto_id, nivel_dificultad_texto):
    nombre_concepto = conceptos_legibles.get(concepto_id, concepto_id)
    prompt = f"""
Eres un tutor educativo experto en la metodología Flipped Classroom.
El estudiante con ID {estudiante_id} requiere contenido sobre **{nombre_concepto}**.
El nivel de conocimiento del estudiante es **{nivel_dificultad_texto}**.

Por favor, proporciona el contenido con estas instrucciones:
1. Explica el concepto de manera clara, adaptada al nivel {nivel_dificultad_texto}.
2. Incluye al menos dos ejemplos prácticos o escenarios relevantes.
3. Usa un tono informativo y motivador.
4. Formatea la respuesta en Markdown con encabezados y listas si es necesario.
5. El contenido debe ser útil y directamente aplicable para un estudiante que está aprendiendo.
"""

    try:
        with st.spinner(f"Generando contenido para '{nombre_concepto}' (Nivel: {nivel_dificultad_texto})..."):
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        st.error(
            f"Error al generar contenido con Gemini para '{nombre_concepto}': {e}. Por favor, inténtalo de nuevo más tarde."
        )
        return f"No se pudo generar contenido dinámico para **{nombre_concepto}**."


# --- Interfaz Streamlit ---

st.set_page_config(layout="wide", page_title="Sistema de Aprendizaje Personalizado-Contenido básico creado por IA")
st.title("Sistema de Aprendizaje Personalizado - Flipped Classroom")

st.subheader("1. Actualizar Niveles con Resultados de Examen (CSV)")
st.info(
    "Descarga el CSV de respuestas de tu Google Form y súbelo aquí para actualizar los niveles de conocimiento de los estudiantes."
)
uploaded_file = st.file_uploader("Sube el archivo CSV de respuestas del examen", type=["csv"])
if uploaded_file is not None:
    estudiantes_df = actualizar_niveles_desde_csv_examen(estudiantes_df.copy(), uploaded_file)

st.subheader("2. Consulta tu Contenido Personalizado")
estudiante_id = st.number_input("Ingresa tu ID de estudiante", min_value=1, step=1)

if estudiante_id:
    estudiante = estudiantes_df[estudiantes_df["id"] == estudiante_id]
    if not estudiante.empty:
        st.write(f"**Nombre del estudiante**: {estudiante['nombre'].iloc[0]}")

        st.subheader("Tu Nivel de Conocimiento Actual:")
        niveles_para_grafico = []
        for concepto in conceptos:
            nivel_num = estudiante[concepto].iloc[0]
            nivel_texto = nivel_map.get(nivel_num, "Desconocido")
            niveles_para_grafico.append(
                {"Concepto": concepto, "Nivel": nivel_texto, "Valor": nivel_num}
            )

        niveles_df_chart = pd.DataFrame(niveles_para_grafico)

        chart = (
            alt.Chart(niveles_df_chart)
            .mark_bar()
            .encode(
                x=alt.X("Concepto:N", title="Concepto", sort=conceptos),
                y=alt.Y("Valor:Q", title="Nivel de Conocimiento", scale=alt.Scale(domain=[0, 1])),
                color=alt.Color(
                    "Nivel:N",
                    scale=alt.Scale(
                        domain=["Básico", "Intermedio", "Avanzado"],
                        range=["#ff9999", "#66b3ff", "#99ff99"],
                    ),
                ),
                tooltip=["Concepto", "Nivel", "Valor"],
            )
            .properties(width="container", height=300, title="Niveles de Conocimiento por Concepto")
            .configure_title(dy=-10)
        )

        st.altair_chart(chart, use_container_width=True)
        st.markdown("---")

        st.subheader("Contenido Personalizado para Ti:")
        for concepto in conceptos:
            nivel_num = estudiante[concepto].iloc[0]
            nivel_dificultad_texto = nivel_map.get(nivel_num, "Básico")
            with st.expander(f"Contenido para {concepto} (Nivel: {nivel_dificultad_texto})"):
                st.markdown(obtener_contenido_gemini(estudiante_id, concepto, nivel_dificultad_texto))
    else:
        st.error("ID de estudiante no encontrado. Por favor, verifica el ID.")

st.subheader("3. Actualizar Nivel de Conocimiento Manualmente (Administrador)")
with st.form("actualizar_conocimiento_manual"):
    estudiante_id_update = st.number_input(
        "ID del estudiante a actualizar", min_value=1, step=1, key="manual_update_id"
    )
    concepto_update = st.selectbox("Concepto a actualizar", conceptos, key="manual_update_concept")
    nuevo_nivel = st.selectbox(
        "Nuevo nivel", [0.25, 0.55, 0.85], format_func=lambda x: nivel_map[x], key="manual_update_level"
    )
    submit = st.form_submit_button("Actualizar Nivel")

    if submit:
        idx = estudiantes_df[estudiantes_df["id"] == estudiante_id_update].index
        if not idx.empty:
            estudiantes_df.loc[idx, concepto_update] = nuevo_nivel
            estudiantes_df.to_csv("estudiantes.csv", index=False)
            st.success(
                f"Nivel de conocimiento para **{concepto_update}** actualizado a **{nivel_map[nuevo_nivel]}** para el estudiante ID {estudiante_id_update}."
            )
        else:
            st.error("ID de estudiante no encontrado. No se pudo actualizar el nivel.")
