import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# Dirección base de tu API FastAPI (ajústala si es necesario)
API_URL = "http://localhost:8000"

# 🧠 Funciones para interactuar con la API
def get_usuarios():
    try:
        r = requests.get(f"{API_URL}/usuarios/")
        return r.json()
    except requests.RequestException:
        return []

def registrar_ejercicio(usuario_id, ejercicio, peso, repeticiones):
    payload = {
        "usuario_id": usuario_id,
        "ejercicio_nombre": ejercicio,
        "peso_levantado": peso,
        "repeticiones": repeticiones
    }
    r = requests.post(f"{API_URL}/registros/", json=payload)
    return r.status_code in (200, 201)

def get_historial(usuario_id, ejercicio=None):
    if ejercicio:
        r = requests.get(f"{API_URL}/usuarios/{usuario_id}/progreso/{ejercicio}")
        return r.json()
    else:
        r = requests.get(f"{API_URL}/usuarios/{usuario_id}/progreso")
        return r.json()

def get_mensajes(usuario_id, n=5):
    r = requests.get(f"{API_URL}/chat/ultimos/{usuario_id}/{n}")
    return r.json()

def enviar_mensaje(usuario_id, mensaje):
    payload = {"usuario_id": usuario_id, "mensaje": mensaje}
    r = requests.post(f"{API_URL}/chat/enviar/", json=payload)
    return r.status_code in (200, 201)

# 🎛️ Interfaz Streamlit
st.set_page_config(page_title="FitFlow", layout="wide")
st.title("💪 FitFlow - Dashboard Deportivo")

# Selección de usuario
usuarios = get_usuarios()
if not usuarios:
    st.error("No se pudo cargar la lista de usuarios.")
    st.stop()

def get_id_str(u):
    _id = u.get('_id')
    if isinstance(_id, dict) and '$oid' in _id:
        return _id['$oid']
    return str(_id)

usuario_map = {u.get('nombre', f"SinNombre-{i}"): get_id_str(u) for i, u in enumerate(usuarios) if 'nombre' in u}

usuario_nombre = st.selectbox("Selecciona un usuario", list(usuario_map.keys()))
usuario_id = usuario_map[usuario_nombre]

tabs = st.tabs(["🏋️ Registro", "📈 Progreso", "💬 Chat"])

# 🏋️ Registro
with tabs[0]:
    st.header("Registrar nuevo ejercicio")
    with st.form("registro_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ejercicio = st.text_input("Ejercicio")
        with col2:
            peso = st.number_input("Peso (kg)", min_value=0.0, step=1.0)
        with col3:
            reps = st.number_input("Repeticiones", min_value=1, max_value=100)
        enviar = st.form_submit_button("Guardar")
        if enviar:
            if registrar_ejercicio(usuario_id, ejercicio, peso, reps):
                st.success("✅ Ejercicio registrado")
                st.experimental_rerun()
            else:
                st.error("❌ Error al guardar")

# 📈 Progreso
with tabs[1]:
    st.header("Historial y evolución")
    datos = get_historial(usuario_id)
    if "ultimo_peso" in datos:
        st.subheader("Últimos pesos por ejercicio")
        df = pd.DataFrame(datos["ultimo_peso"])
        df.rename(columns={"_id": "Ejercicio", "ultimo_peso": "Peso (kg)", "fecha": "Fecha"}, inplace=True)
        st.dataframe(df)

        ejercicios_disponibles = df["Ejercicio"].tolist()
        ejercicio_sel = st.selectbox("Ver evolución de", ejercicios_disponibles)
        detalle = get_historial(usuario_id, ejercicio_sel)
        if detalle and "historial" in detalle:
            df_hist = pd.DataFrame(detalle["historial"])
            if "fecha_registro" in df_hist.columns:
                fechas = []
                for val in df_hist["fecha_registro"]:
                    if isinstance(val, dict) and "$date" in val:
                        fechas.append(pd.to_datetime(val["$date"]))
                    else:
                        fechas.append(pd.to_datetime(val))
                df_hist["fecha_registro"] = fechas
            fig = px.line(df_hist, x="fecha_registro", y="peso_levantado", title=f"Evolución: {ejercicio_sel}", markers=True)
            st.plotly_chart(fig)
        else:
            st.info("No hay historial para este ejercicio.")

# 💬 Chat
with tabs[2]:
    st.header("Chatbot y emociones")
    st.subheader("Últimos mensajes")
    mensajes = get_mensajes(usuario_id)
    if mensajes and isinstance(mensajes, list):
        for m in mensajes:
            fecha = m.get("fecha", "")
            mensaje = m.get("mensaje", "")
            origen = "🧑 Tú" if m.get("origen") == "usuario" else "🤖 Bot"
            st.markdown(f"{origen} ({fecha}): {mensaje}")
    else:
        st.info("No hay mensajes recientes.")

    st.subheader("Enviar mensaje")
    with st.form("mensaje_form"):
        mensaje = st.text_area("Mensaje")
        enviar = st.form_submit_button("Enviar")
        if enviar:
            if enviar_mensaje(usuario_id, mensaje):
                st.success("✅ Mensaje enviado")
                st.experimental_rerun()
            else:
                st.error("❌ Error al enviar")
