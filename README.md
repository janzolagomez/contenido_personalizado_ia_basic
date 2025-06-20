# 📚 Sistema de Aprendizaje Personalizado - Flipped Classroom

Esta aplicación implementa un sistema inteligente de aprendizaje personalizado basado en la metodología **Flipped Classroom**, utilizando:

- 📊 Visualización de niveles de conocimiento por concepto.
- 🤖 Generación de contenido adaptado con **Gemini (Google Generative AI)**.
- 🧠 Gestión automática y manual de niveles de conocimiento.
- 📂 Integración con resultados de exámenes exportados desde Google Forms (CSV).

---

## 🚀 Características principales

- **Carga de resultados de exámenes en CSV** para actualizar los niveles de los estudiantes automáticamente.
- **Visualización gráfica** de los niveles por concepto clave.
- **Generación dinámica de contenido educativo personalizado** según el nivel de cada estudiante.
- **Interfaz amigable para estudiantes y administradores.**

---

## 🛠️ Requisitos

Antes de ejecutar la app, asegúrate de tener instalado:

- Python 3.9 o superior
- Las dependencias listadas en [`requirements.txt`](./requirements.txt)

Instalación de dependencias:

```bash
pip install -r requirements.txt
🔐 Configuración de la API de Gemini
Necesitas una clave de API válida de Google Generative AI. Configúrala de una de las siguientes formas:

Opción 1: En desarrollo local
Crea una variable de entorno en tu sistema:

bash
Copiar
Editar
export GEMINI_API_KEY="tu_clave_api_aquí"
Opción 2: En despliegue con Streamlit Cloud
Agrega tu clave a Secrets en https://share.streamlit.io/:

toml
Copiar
Editar
# .streamlit/secrets.toml
gemini_api_key = "tu_clave_api_aquí"
📁 Estructura esperada de archivos
Asegúrate de tener un archivo estudiantes.csv con la siguiente estructura mínima:

csv
Copiar
Editar
id,nombre,FC_DEFINICION,FC_ROLES,FC_TECNOLOGIA,FC_APLICACION,FC_BENEFICIOS
1,Andrea,0.55,0.55,0.25,0.25,0.55
2,Luis,0.85,0.85,0.55,0.55,0.85
Los valores deben estar en formato numérico: 0.25 (básico), 0.55 (intermedio), 0.85 (avanzado).

📊 Estructura del CSV de resultados del examen
El archivo CSV de resultados del examen (Google Forms) debe tener al menos estas columnas:

ID de Estudiante

Puntuación total

Ejemplo:

csv
Copiar
Editar
ID de Estudiante,Puntuación total
1,90
2,45
▶️ Ejecutar la aplicación
En tu terminal:

bash
Copiar
Editar
streamlit run app.py
Luego abre en tu navegador: http://localhost:8501

🧠 Créditos y Licencia
Desarrollado por [Tu Nombre o Institución].
Inspirado en prácticas de aprendizaje activo y metodologías centradas en el estudiante.

Licencia: MIT
