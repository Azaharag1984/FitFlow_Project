# 💪 FitFlow API

**FitFlow API** es una aplicación desarrollada con FastAPI, MongoDB y Streamlit para ayudar a usuarios y entrenadores personales a registrar, visualizar y mejorar su progreso de entrenamiento físico a través de dashboards y un chatbot inteligente motivacional.

---

## 🚀 Características principales

- 📊 Seguimiento de progresos por ejercicio: peso, repeticiones, frecuencia.
- 📈 Dashboard interactivo con evolución temporal del rendimiento.
- 🤖 Chatbot motivacional con integración OpenAI para generar rutinas personalizadas y analizar el estado anímico.
- 🏆 Sistema de logros: metas alcanzadas por el usuario (récords, frecuencia, constancia).
- 🧠 API RESTful modular para integrar otras plataformas fácilmente.

---

## 🧱 Tecnologías usadas

- **Backend:** FastAPI
- **Base de datos:** MongoDB (Motor async)
- **Frontend:** Streamlit
- **LLM:** OpenAI GPT-4 (API)
- **Otros:** Python 3.10+, Pydantic, Uvicorn

---

## 📁 Estructura del proyecto

fitflow_api/

├── main.py                          # Punto de entrada FastAPI

├── database.py                      # Conexión a MongoDB

├── requirements.txt                 # Dependencias del proyecto

├── .env                             # Variables de entorno (ej. MONGO_URL, OPENAI_KEY)

├── README.md                        # Documentación inicial

│

├── models/                          # Modelos Pydantic (validación de datos)

│   ├── usuario.py                   # Usuario (nombre, email, objetivo...)

│   ├── ejercicio.py                 # Ejercicio (nombre, grupo muscular...)

│   ├── registro.py                  # Registro de sets

│   ├── logro.py                     # Logros alcanzados

│   └── conversacion.py              # Conversaciones con el chatbot

│

├── controllers/                    # Lógica de negocio y acceso a BBDD

│   ├── usuario_controller.py

│   ├── ejercicio_controller.py

│   ├── registro_controller.py

│   ├── logro_controller.py

│   └── conversacion_controller.py

│

├── routes/                         # Rutas de la API (FastAPI)

│   ├── usuarios.py

│   ├── ejercicios.py

│   ├── registros.py

│   ├── logros.py

│   └── chatbot.py

│

├── utils/                          # Funciones auxiliares

│   └── openai_client.py            # Llamadas a OpenAI para el chatbot

│

└── streamlit_app/                  # Interfaz gráfica en Streamlit

    ├── app.py                      # Principal
    
    ├── components/                # Formularios, gráficos, dashboards
    
    └── styles/                    # CSS personalizado (opcional)


# 📦 Instalación y uso local
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/fitflow-api.git
cd fitflow-api

# 2. Crea entorno virtual
python -m venv env
source env/bin/activate  # o .\env\Scripts\activate en Windows

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Ejecuta FastAPI
uvicorn main:app --reload


 Accede a la documentación interactiva en:
📎 http://localhost:8000/docs


# 🔑 Variables de entorno recomendadas

Usa .env para definir:

MONGO_URL=mongodb://localhost:27017
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx


# 🌐 Endpoints destacados
## Método	Endpoint	Descripción
POST	/usuarios	Crear un nuevo usuario
POST	/registros	Añadir registro de ejercicio
GET	/usuarios/{user_id}/progreso	Obtener progreso global por ejercicio
POST	/chatbot	Enviar mensaje al chatbot
GET	/conversaciones/{user_id}	Ver historial de conversación


# 🛠️ Pendiente de desarrollo

    Sistema de autenticación (opcional)

    Módulo de rutinas automáticas generadas por IA

    Exportación de datos personales

📄 Licencia

MIT License © 2025 - [Tu Nombre o Equipo]
