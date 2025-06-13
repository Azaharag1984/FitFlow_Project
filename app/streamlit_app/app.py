import streamlit as st
import requests
import json
from datetime import datetime, date

# --- Configuración de la API de FastAPI ---
# ¡IMPORTANTE! Asegúrate de que esta URL coincida con la dirección donde tu backend FastAPI está corriendo.
FASTAPI_BASE_URL = "http://localhost:8000"

# --- Funciones de Utilidad y Cliente API ---

def make_api_request(method, endpoint, data=None, params=None):
    """
    Realiza una solicitud HTTP a la API de FastAPI.
    Maneja respuestas JSON y errores HTTP.
    """
    url = f"{FASTAPI_BASE_URL}/{endpoint}"
    # Mensajes de depuración solo en la consola, no en la UI de Streamlit
    # print(f"DEBUG (Consola): Realizando {method} request a: {url}") 
    # if data:
    #     print(f"DEBUG (Consola): Datos enviados: {data}") 

    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, params=params)
        elif method == "DELETE":
            response = requests.delete(url, params=params)
        else:
            st.error(f"Método HTTP no soportado: {method}")
            return None

        # print(f"DEBUG (Consola): Respuesta de la API (Status: {response.status_code})")
        
        response.raise_for_status() # Lanza una excepción si la respuesta no es 2xx

        try:
            json_response = response.json()
            # print(f"DEBUG (Consola): Respuesta JSON recibida: {json_response}")
            return json_response
        except json.JSONDecodeError:
            if response.status_code == 204:
                return {"message": "Operación exitosa sin contenido de respuesta."}
            st.warning(f"La respuesta no es JSON, texto recibido: {response.text}")
            return {"message": response.text}

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        detail = "Error desconocido"
        try:
            error_json = e.response.json()
            detail = error_json.get("detail", detail)
        except json.JSONDecodeError:
            detail = e.response.text
        st.error(f"Error {status_code}: {detail}")
        # print(f"DEBUG (Consola): HTTPError: {status_code} - {detail}")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"No se pudo conectar con el servidor FastAPI en {FASTAPI_BASE_URL}. Asegúrate de que esté corriendo.")
        # print(f"DEBUG (Consola): ConnectionError: No se pudo conectar con {FASTAPI_BASE_URL}")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
        # print(f"DEBUG (Consola): Error inesperado: {e}")
        return None

def get_display_options(entities, entity_type):
    """
    Genera un diccionario de opciones para st.selectbox con IDs como claves y nombres legibles como valores.
    Asegura que el _id sea siempre una cadena.
    """
    options_dict = {}
    if entities:
        for entity in entities:
            entity_id = entity.get('_id')
            if isinstance(entity_id, dict) and '$oid' in entity_id:
                entity_id = entity_id['$oid']
            elif entity_id is not None:
                entity_id = str(entity_id) # Ensure ID is always a string

            if entity_id:
                display_name = ""
                if entity_type == "usuarios":
                    display_name = entity.get('nombre', 'Usuario sin nombre')
                elif entity_type == "registros":
                    date_part = entity.get('fecha_registro', 'N/A')
                    if isinstance(date_part, str) and 'T' in date_part:
                        date_part = date_part.split('T')[0] # Get only date part
                    display_name = f"{entity.get('ejercicio_nombre', 'Ejercicio sin nombre')} - {date_part}"
                elif entity_type == "logros":
                    display_name = entity.get('descripcion', 'Logro sin descripción')
                elif entity_type == "ejercicios":
                    display_name = entity.get('nombre', 'Ejercicio sin nombre')
                elif entity_type == "conversaciones":
                    date_part = entity.get('fecha', 'N/A')
                    if isinstance(date_part, str) and 'T' in date_part:
                        date_part = date_part.split('T')[0]
                    display_name = f"Usuario: {entity.get('usuario_id', 'N/A')}, Fecha: {date_part}"
                else:
                    display_name = "Entidad Desconocida" # Fallback

                options_dict[entity_id] = display_name
    return options_dict

def _format_selectbox_option(option_id, options_dict, placeholder_text):
    """
    Formatea el texto que se muestra en el st.selectbox.
    Incluye el nombre legible y el ID real para mayor claridad.
    """
    if option_id is None:
        return placeholder_text
    
    display_name = options_dict.get(option_id, "Nombre Desconocido")
    return f"{display_name} (ID: {option_id})"


def display_entity_list(entity_name, entities, excluded_keys=None):
    """Muestra una lista de entidades en un formato de tabla."""
    if entities:
        processed_entities = []
        for entity in entities:
            processed_entity = entity.copy()
            if '_id' in processed_entity:
                if isinstance(processed_entity['_id'], dict) and '$oid' in processed_entity['_id']:
                    processed_entity['_id'] = processed_entity['_id']['$oid']
                else: 
                    processed_entity['_id'] = str(processed_entity['_id']) 
            
            if excluded_keys:
                for key in excluded_keys:
                    processed_entity.pop(key, None)
            processed_entities.append(processed_entity)
        
        st.dataframe(processed_entities, use_container_width=True)
    else:
        st.info(f"No hay {entity_name} registrados.")

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="FitFlow: Gestión Integral",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Estilos CSS personalizados para un aspecto profesional y curioso (¡FINALMENTE CORREGIDOS!) ---
st.markdown("""
<style>
    /* Global body and container styles */
    .stApp {
        background-color: #2e7d32; /* Light gray background for the app */
        font-family: 'Inter', sans-serif; /* Consistent font */
        color: #333333; /* Default text color for the entire app */
    }
    .reportview-container {
        background: #2e7d32; /* Ensure report container matches body */
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #2e7d32; /* White sidebar background */
        border-right: 1px solid #e6e6e6; /* Subtle border */
        box-shadow: 2px 0 5px rgba(0,0,0,0.05); /* Soft shadow */
    }
    /* Specific selector for Streamlit sidebar radio container (may change with updates) */
    .st-emotion-cache-1kyx633 { /* Ensure this selector is up-to-date with Streamlit's latest version */
        background-color: #f8f9fa; /* Slightly darker background for the radio options area */
        border-radius: 10px;
        padding: 10px;
        margin-top: 10px;
    }
    /* Specific selector for radio options text (may change with updates) */
    .st-emotion-cache-1kyx633 .st-bd { /* Ensure this selector is up-to-date with Streamlit's latest version */
        font-weight: bold;
        color: #555;
    }


    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #333333; /* Darker text for readability */
        font-family: 'Inter', sans-serif;
        padding-top: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee; /* Subtle underline */
        margin-bottom: 20px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #4CAF50; /* Vibrant green */
        color: white;
        border-radius: 8px; /* Rounded corners */
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2); /* Soft shadow */
        transition: all 0.3s ease; /* Smooth transition for hover effects */
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049; /* Slightly darker green on hover */
        transform: translateY(-2px); /* Lift effect */
        box-shadow: 3px 3px 8px rgba(0,0,0,0.3); /* Enhanced shadow on hover */
    }
    /* Specific styling for delete buttons */
    .stButton>button[kind="secondaryFormSubmit"] {
        background-color: #dc3545; /* Red for delete actions */
    }
    .stButton>button[kind="secondaryFormSubmit"]:hover {
        background-color: #c82333;
    }


    /* Input fields (text, textarea, number, date) - FORCED WHITE background and BLACK text */
    /* Target the input elements directly */
    .stTextInput input[data-baseweb="input"], 
    .stTextArea textarea[data-baseweb="textarea"],
    .stNumberInput input[data-baseweb="input"],
    .stDateInput input[data-baseweb="input"] {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 8px 10px;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.05); /* Inner shadow for depth */
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        background-color: #2e7d32 !important; /* FORCED WHITE background for inputs */
        color: #000000 !important; /* FORCED BLACK text for inputs */
    }
    /* Placeholder text within inputs */
    .stTextInput input::placeholder, 
    .stTextArea textarea::placeholder {
        color: #6c757d !important; /* Lighter grey for placeholder */
    }
    /* Focus state for inputs */
    .stTextInput input:focus, 
    .stTextArea textarea:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus {
        border-color: #4CAF50; /* Highlight on focus */
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.05), 0 0 0 0.2rem rgba(76, 175, 80, 0.25); /* Focus ring */
        outline: none;
    }
    /* Labels of input fields (e.g., "Nombre del Usuario*") */
    .stForm label {
        color: #000000 !important; /* FORCED BLACK text for all input labels */
        font-weight: bold; /* Make labels stand out */
    }

    /* st.selectbox specific styling - FORCED WHITE background and BLACK text */
    /* Target the currently displayed value container in the selectbox */
    .stSelectbox [data-baseweb="select"] > div:first-child { /* This targets the input-like part of selectbox */
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 8px 10px;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.05);
        background-color: #2e7d32 !important; /* FORCED WHITE background for the selected value area */
        color: #000000 !important; /* FORCED BLACK text for the selected value */
    }
    /* Target the dropdown list container when it's open */
    .stSelectbox [data-baseweb="popover"] > div[role="listbox"] { /* This targets the actual dropdown menu */
        background-color: #2e7d32 !important; /* FORCED WHITE background for the dropdown list */
        border-radius: 8px;
        border: 1px solid #ccc;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        z-index: 10000; /* Ensure it appears above everything else */
    }
    /* Target individual options within the dropdown list */
    .stSelectbox [role="option"] {
        color: #000000 !important; /* FORCED BLACK text for options */
        background-color: #2e7d32 !important; /* FORCED WHITE background for options */
        padding: 8px 10px;
    }
    /* Hover state for dropdown options */
    .stSelectbox [role="option"]:hover {
        background-color: #f0f0f0 !important; /* Light gray on hover */
    }
    /* Selected option in the dropdown list */
    .stSelectbox [role="option"][aria-selected="true"] {
        background-color: #e6e6e6 !important; /* Slightly darker grey for selected option */
    }


    /* Alerts and messages */
    .stAlert {
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .stAlert.info {
        background-color: #e0f2f7; /* Light blue */
        color: #01579b;
    }
    .stAlert.success {
        background-color: #e8f5e9; /* Light green */
        color: #2e7d32;
    }
    .stAlert.warning {
        background-color: #fff3e0; /* Light orange */
        color: #ef6c00;
    }
    .stAlert.error {
        background-color: #ffebee; /* Light red */
        color: #c62828;
    }

    /* Forms */
    .stForm {
        padding: 25px;
        background-color: #2e7d32; /* White background for forms */
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* More prominent shadow */
        margin-bottom: 30px;
        color: #333333; /* Default text color for content within the form (e.g. st.write) */
    }

    /* Dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden; /* Ensures rounded corners are visible */
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stDataFrame .ag-header-cell, .stDataFrame .ag-cell {
        font-family: 'Inter', sans-serif;
    }

    /* Tabs */
    .stTabs {
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa; /* Light background for tabs */
        border-radius: 10px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        background-color: #e9ecef; /* Tab background */
        border-radius: 8px;
        margin: 0;
        padding: 0 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        font-weight: bold;
        color: #495057;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important; /* Active tab green */
        color: white !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #dee2e6; /* Hover effect */
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
    }
    .stChatMessage.user {
        background-color: #e0f2f7; /* Light blue for user */
        align-self: flex-end;
    }
    .stChatMessage.assistant {
        background-color: #e8f5e9; /* Light green for assistant */
        align-self: flex-start;
    }
</style>
""", unsafe_allow_html=True)


# --- Barra Lateral (Navegación) ---
st.sidebar.title("Menú FitFlow 🏋️‍♂️")
page = st.sidebar.radio(
    "Navegación",
    ["Dashboard", "Usuarios", "Registros", "Logros", "Ejercicios", "Conversaciones", "Acerca de"]
)

# --- Contenido Principal de la Aplicación ---

if page == "Dashboard":
    st.title("📊 Dashboard FitFlow")
    st.write("Bienvenido al panel de control integral de tu aplicación FitFlow. Aquí podrás ver un resumen y gestionar tus datos.")

    st.subheader("Estadísticas Rápidas")
    col1, col2, col3 = st.columns(3)

    # Contar usuarios
    usuarios = make_api_request("GET", "usuarios")
    if usuarios is not None:
        col1.metric("Total Usuarios", len(usuarios))
    else:
        col1.metric("Total Usuarios", "Error")

    # Contar registros
    registros = make_api_request("GET", "registros")
    if registros is not None:
        col2.metric("Total Registros", len(registros))
    else:
        col2.metric("Total Registros", "Error")

    # Contar logros
    logros = make_api_request("GET", "logros")
    if logros is not None:
        col3.metric("Total Logros", len(logros))
    else:
        col3.metric("Total Logros", "Error")

    st.markdown("---")
    st.subheader("Últimos Registros")
    if registros:
        # Ordenar registros por fecha (asumiendo 'fecha_registro' existe)
        for r in registros:
            if 'fecha_registro' in r and isinstance(r['fecha_registro'], str):
                try:
                    r['fecha_registro_dt'] = datetime.fromisoformat(r['fecha_registro'])
                except ValueError:
                    r['fecha_registro_dt'] = datetime.min 
            else:
                r['fecha_registro_dt'] = datetime.min 

        registros_ordenados = sorted(registros, key=lambda x: x.get('fecha_registro_dt', datetime.min), reverse=True)
        display_entity_list("últimos registros", registros_ordenados[:5], excluded_keys=['fecha_registro_dt'])
    else:
        st.info("No hay registros para mostrar en el dashboard.")

    st.subheader("Volumen Total de Entrenamiento por Usuario")
    if usuarios:
        volumen_data = []
        for user in usuarios:
            user_id = user.get('_id')
            if isinstance(user_id, dict) and '$oid' in user_id:
                user_id = user_id['$oid']
            elif user_id is not None:
                user_id = str(user_id) 

            if user_id:
                volumen_total = make_api_request("GET", f"usuarios/{user_id}/volumen_total")
                if volumen_total is not None:
                    volumen_data.append({"Usuario": user.get("nombre", "Desconocido"), "Volumen": volumen_total})
        
        if volumen_data:
            import pandas as pd
            df_volumen = pd.DataFrame(volumen_data)
            if not df_volumen.empty:
                st.bar_chart(data=df_volumen, x="Usuario", y="Volumen")
            else:
                st.info("No hay datos de volumen para mostrar o hubo un error al recuperarlos.")
        else:
            st.info("No hay datos de volumen para mostrar o hubo un error al recuperarlos.")
    else:
        st.info("Necesitas tener usuarios para ver el volumen de entrenamiento.")


elif page == "Usuarios":
    st.title("👤 Gestión de Usuarios")

    tab1, tab2, tab3 = st.tabs(["Lista de Usuarios", "Crear Usuario", "Actualizar/Eliminar Usuario"])

    with tab1:
        st.subheader("Lista de Todos los Usuarios")
        usuarios = make_api_request("GET", "usuarios")
        display_entity_list("usuarios", usuarios)

    with tab2:
        st.subheader("Crear Nuevo Usuario")
        with st.form("create_usuario_form"):
            nombre = st.text_input("Nombre del Usuario*", key="create_nombre")
            email = st.text_input("Email del Usuario*", key="create_email")
            objetivo = st.text_area("Objetivo (Opcional)", key="create_objetivo")
            
            submitted = st.form_submit_button("Crear Usuario")
            if submitted:
                if nombre and email:
                    usuario_data = {
                        "nombre": nombre,
                        "email": email,
                        "objetivo": objetivo if objetivo else None 
                    }
                    response = make_api_request("POST", "usuarios", usuario_data)
                    if response:
                        st.success(f"Usuario creado con ID: {response}")
                        st.rerun() 
                else:
                    st.warning("Nombre y Email son campos obligatorios.")

    with tab3:
        st.subheader("Actualizar o Eliminar Usuario")
        
        # Obtener la lista de usuarios y procesar para las opciones del selectbox
        users_from_api = make_api_request("GET", "usuarios")
        usuario_options_dict = get_display_options(users_from_api, "usuarios")
        
        if not usuario_options_dict: # If the dict is empty, no users are available
            st.info("No hay usuarios disponibles para actualizar o eliminar. Por favor, crea algunos primero.")
        else:
            options_for_selectbox = [None] + list(usuario_options_dict.keys())
            
            selected_user_id = st.selectbox("Selecciona un Usuario para Actualizar/Eliminar", 
                                            options=options_for_selectbox, 
                                            format_func=lambda x: _format_selectbox_option(x, usuario_options_dict, "--- Selecciona un usuario ---"),
                                            index=0, # Default to the placeholder
                                            key="update_delete_select_user")
            
            if selected_user_id is not None: # Only proceed if a real user ID is selected
                usuario_data = make_api_request("GET", f"usuarios/{selected_user_id}")
                if usuario_data:
                    current_nombre = usuario_data.get("nombre", "")
                    current_email = usuario_data.get("email", "")
                    current_objetivo = usuario_data.get("objetivo", "")

                    with st.form("update_delete_usuario_form"):
                        new_nombre = st.text_input("Nuevo Nombre", value=current_nombre, key="update_nombre")
                        new_email = st.text_input("Nuevo Email", value=current_email, key="update_email")
                        new_objetivo = st.text_area("Nuevo Objetivo", value=current_objetivo, key="update_objetivo")

                        col_update, col_delete = st.columns(2)
                        update_submitted = col_update.form_submit_button("Actualizar Usuario")
                        delete_submitted = col_delete.form_submit_button("Eliminar Usuario", help="Esta acción es irreversible.")

                        if update_submitted:
                            if new_nombre and new_email:
                                update_data = {
                                    "nombre": new_nombre,
                                    "email": new_email,
                                    "objetivo": new_objetivo if new_objetivo else None
                                }
                                response = make_api_request("PUT", f"usuarios/{selected_user_id}", update_data)
                                if response:
                                    st.success(f"Usuario {selected_user_id} actualizado: {response.get('message', 'Éxito')}")
                                    st.rerun() 
                            else:
                                st.warning("Nombre y Email son campos obligatorios para la actualización.")

                        if delete_submitted:
                            confirm_delete = st.expander("Confirmar Eliminación")
                            with confirm_delete:
                                st.warning(f"¿Estás seguro de que quieres eliminar el usuario '{_format_selectbox_option(selected_user_id, usuario_options_dict, '')}'?")
                                if st.button(f"Sí, Eliminar Usuario {_format_selectbox_option(selected_user_id, usuario_options_dict, '')}", key="confirm_delete_user_btn"):
                                    response = make_api_request("DELETE", f"usuarios/{selected_user_id}")
                                    if response:
                                        st.success("Usuario eliminado exitosamente.")
                                        st.rerun() 
                                    else:
                                        st.error("Error al eliminar el usuario.")
                else:
                    st.info("No se pudieron cargar los detalles del usuario seleccionado.")
            else:
                st.info("Por favor, selecciona un usuario para ver/modificar sus detalles.")


elif page == "Registros":
    st.title("📝 Gestión de Registros de Entrenamiento")

    tab1, tab2, tab3, tab4 = st.tabs(["Lista de Registros", "Crear Registro", "Actualizar/Eliminar Registro", "Análisis de Registros"])

    with tab1:
        st.subheader("Lista de Todos los Registros")
        registros = make_api_request("GET", "registros")
        display_entity_list("registros", registros)

    with tab2:
        st.subheader("Crear Nuevo Registro")
        with st.form("create_registro_form"):
            users_from_api = make_api_request("GET", "usuarios")
            usuario_options_dict = get_display_options(users_from_api, "usuarios")
            
            if not usuario_options_dict:
                st.warning("No hay usuarios disponibles. Por favor, crea un usuario primero para crear un registro.")
                selected_usuario_id = None 
            else:
                options_for_user_selectbox = [None] + list(usuario_options_dict.keys())
                selected_usuario_id = st.selectbox("Selecciona Usuario*", 
                                                    options=options_for_user_selectbox, 
                                                    format_func=lambda x: _format_selectbox_option(x, usuario_options_dict, "--- Selecciona un usuario ---"), 
                                                    index=0, 
                                                    key="create_registro_usuario_id")
            
            exercises_from_api = make_api_request("GET", "ejercicios")
            ejercicio_options_dict = get_display_options(exercises_from_api, "ejercicios")
            ejercicio_options_for_select = {None: "--- Selecciona un ejercicio (Opcional) ---"}
            ejercicio_options_for_select.update(ejercicio_options_dict)

            selected_ejercicio_id = st.selectbox("ID del Ejercicio (Opcional)", 
                                                options=list(ejercicio_options_for_select.keys()), 
                                                format_func=lambda x: _format_selectbox_option(x, ejercicio_options_for_select, "--- Selecciona un ejercicio (Opcional) ---"), 
                                                index=0, 
                                                key="create_registro_ejercicio_id")

            ejercicio_nombre_val = ""
            if selected_ejercicio_id is not None and selected_ejercicio_id in ejercicio_options_dict: # Ensure ID exists
                ejercicio_nombre_val = ejercicio_options_dict[selected_ejercicio_id] # Use the display name from the dict
                # Remove "(ID: ...)" part if you only want the pure name in the text input
                if " (ID: " in ejercicio_nombre_val:
                    ejercicio_nombre_val = ejercicio_nombre_val.split(" (ID: ")[0]


            ejercicio_nombre = st.text_input("Nombre del Ejercicio*", value=ejercicio_nombre_val, help="Si seleccionas un ID de ejercicio, este campo se autocompletará. Puedes modificarlo.", key="create_registro_ejercicio_nombre")
            
            fecha_registro = st.date_input("Fecha del Registro*", datetime.now().date(), key="create_registro_fecha")
            peso_levantado = st.number_input("Peso Levantado (kg/lb)*", min_value=0.0, step=0.1, key="create_registro_peso")
            repeticiones = st.number_input("Repeticiones*", min_value=1, step=1, key="create_registro_reps")
            notas = st.text_area("Notas (Opcional)", key="create_registro_notas")

            submitted = st.form_submit_button("Crear Registro")
            if submitted:
                if selected_usuario_id and fecha_registro and ejercicio_nombre and peso_levantado is not None and repeticiones is not None:
                    registro_data = {
                        "usuario_id": selected_usuario_id,
                        "ejercicio_id": selected_ejercicio_id if selected_ejercicio_id else None,
                        "ejercicio_nombre": ejercicio_nombre,
                        "peso_levantado": peso_levantado,
                        "repeticiones": repeticiones,
                        "fecha_registro": datetime.combine(fecha_registro, datetime.min.time()).isoformat(), 
                        "notas": notas if notas else None
                    }
                    response = make_api_request("POST", "registros", registro_data)
                    if response:
                        st.success(f"Registro creado con ID: {response}")
                        st.rerun() 
                else:
                    st.warning("Los campos 'Usuario', 'Fecha', 'Nombre del Ejercicio', 'Peso Levantado' y 'Repeticiones' son obligatorios.")

    with tab3:
        st.subheader("Actualizar o Eliminar Registro")
        records_from_api = make_api_request("GET", "registros")
        registro_options_dict = get_display_options(records_from_api, "registros")

        if not registro_options_dict:
            st.info("No hay registros disponibles para actualizar o eliminar. Por favor, crea algunos primero.")
        else:
            options_for_selectbox = [None] + list(registro_options_dict.keys())
            
            selected_registro_id = st.selectbox("Selecciona un Registro para Actualizar/Eliminar", 
                                                options=options_for_selectbox, 
                                                format_func=lambda x: _format_selectbox_option(x, registro_options_dict, "--- Selecciona un registro ---"),
                                                index=0, 
                                                key="update_delete_select_registro")

            if selected_registro_id is not None:
                registro_data = make_api_request("GET", f"registros/{selected_registro_id}")
                if registro_data:
                    current_fecha_registro_str = registro_data.get('fecha_registro')
                    current_fecha_registro = datetime.now().date() 
                    if isinstance(current_fecha_registro_str, str):
                        try:
                            current_fecha_registro = datetime.fromisoformat(current_fecha_registro_str).date()
                        except ValueError:
                            pass 

                    current_ejercicio_nombre = registro_data.get("ejercicio_nombre", "")
                    current_peso_levantado = float(registro_data.get("peso_levantado", 0.0))
                    current_repeticiones = int(registro_data.get("repeticiones", 0))
                    current_notas = registro_data.get("notas", "")
                    
                    with st.form("update_delete_registro_form"):
                        st.write(f"**Registro para Usuario ID:** {registro_data.get('usuario_id', 'N/A')}")
                        st.write(f"**Ejercicio ID Asociado:** {registro_data.get('ejercicio_id', 'N/A')}")

                        new_ejercicio_nombre = st.text_input("Nombre del Ejercicio", value=current_ejercicio_nombre, key="update_registro_ejercicio")
                        new_peso_levantado = st.number_input("Peso Levantado (kg/lb)", value=current_peso_levantado, min_value=0.0, step=0.1, key="update_registro_peso")
                        new_repeticiones = st.number_input("Repeticiones", value=current_repeticiones, min_value=1, step=1, key="update_registro_reps")
                        new_fecha_registro = st.date_input("Fecha del Registro", value=current_fecha_registro, key="update_registro_fecha")
                        new_notas = st.text_area("Notas", value=current_notas, key="update_registro_notas")


                        col_update, col_delete = st.columns(2)
                        update_submitted = col_update.form_submit_button("Actualizar Registro")
                        delete_submitted = col_delete.form_submit_button("Eliminar Registro", help="Esta acción es irreversible.")

                        if update_submitted:
                            update_data = {
                                "ejercicio_nombre": new_ejercicio_nombre,
                                "peso_levantado": new_peso_levantado,
                                "repeticiones": new_repeticiones,
                                "fecha_registro": datetime.combine(new_fecha_registro, datetime.min.time()).isoformat(), 
                                "notas": new_notas if new_notas else None
                            }
                            response = make_api_request("PUT", f"registros/{selected_registro_id}", update_data)
                            if response:
                                st.success(f"Registro {selected_registro_id} actualizado.")
                                st.rerun()
                            else:
                                st.error("Error al actualizar el registro.")

                        if delete_submitted:
                            confirm_delete = st.expander("Confirmar Eliminación")
                            with confirm_delete:
                                st.warning(f"¿Estás seguro de que quieres eliminar el registro '{_format_selectbox_option(selected_registro_id, registro_options_dict, '')}'?")
                                if st.button(f"Sí, Eliminar Registro {_format_selectbox_option(selected_registro_id, registro_options_dict, '')}", key="confirm_delete_record_btn"):
                                    response = make_api_request("DELETE", f"registros/{selected_registro_id}")
                                    if response:
                                        st.success("Registro eliminado exitosamente.")
                                        st.rerun()
                                    else:
                                        st.error("Error al eliminar el registro.")
                else:
                    st.info("No se pudieron cargar los detalles del registro seleccionado.")
            else:
                st.info("Por favor, selecciona un registro para ver/modificar sus detalles.")

    with tab4:
        st.subheader("Análisis de Registros")
        
        users_from_api_analysis = make_api_request("GET", "usuarios")
        usuario_options_analysis_dict = get_display_options(users_from_api_analysis, "usuarios")
        
        selected_usuario_id_analysis = st.selectbox("Selecciona un Usuario para Análisis", 
                                                    options=[None] + list(usuario_options_analysis_dict.keys()), 
                                                    format_func=lambda x: _format_selectbox_option(x, usuario_options_analysis_dict, "--- Selecciona un usuario ---"), 
                                                    index=0, 
                                                    key="analysis_usuario_id")

        if selected_usuario_id_analysis is not None:
            st.markdown("---")
            st.write("### Último Peso Levantado por Ejercicio")
            ultimo_peso_data = make_api_request("GET", f"usuarios/{selected_usuario_id_analysis}/ultimo_peso_por_ejercicio")
            if ultimo_peso_data:
                display_entity_list("último peso por ejercicio", ultimo_peso_data)
            else:
                st.info("No se encontró información de último peso por ejercicio para este usuario.")

            st.markdown("---")
            st.write("### Mejor Marca por Ejercicio")
            registros_del_usuario = make_api_request("GET", f"registros/usuario/{selected_usuario_id_analysis}")
            
            ejercicio_nombres = []
            if registros_del_usuario:
                ejercicio_nombres = sorted(list(set([e.get('ejercicio_nombre') for e in registros_del_usuario if e.get('ejercicio_nombre')])))
            
            selected_ejercicio_for_best_mark = st.selectbox("Selecciona un Ejercicio para ver la Mejor Marca", 
                                                            options=[None] + ejercicio_nombres, 
                                                            format_func=lambda x: x if x else "--- Selecciona un ejercicio ---",
                                                            index=0, 
                                                            key="select_best_mark_exercise")
            
            if selected_ejercicio_for_best_mark is not None:
                mejor_marca_data = make_api_request("GET", f"usuarios/{selected_usuario_id_analysis}/mejor_marca/{selected_ejercicio_for_best_mark}")
                if mejor_marca_data:
                    st.json(mejor_marca_data)
                else:
                    st.info("No se encontró la mejor marca para este ejercicio y usuario.")
            else:
                st.info("Por favor, selecciona un ejercicio para analizar sus mejores marcas.")
            
            st.markdown("---")
            st.write("### Frecuencia Semanal de Entrenamiento")
            frecuencia_semanal_data = make_api_request("GET", f"usuarios/{selected_usuario_id_analysis}/frecuencia_semanal")
            if frecuencia_semanal_data:
                import pandas as pd
                df_frecuencia = pd.DataFrame(frecuencia_semanal_data)
                if not df_frecuencia.empty:
                    df_frecuencia['Periodo'] = df_frecuencia['_id'].apply(lambda x: f"Año {x['año']}, Semana {x['semana']}")
                    st.line_chart(df_frecuencia, x="Periodo", y="dias")
                else:
                    st.info("No hay datos de frecuencia semanal para mostrar.")
            else:
                st.info("No se encontró información de frecuencia semanal para este usuario.")

        else:
            st.info("Por favor, selecciona un usuario para ver sus análisis de registros.")


elif page == "Logros":
    st.title("🏆 Gestión de Logros")

    tab1, tab2, tab3 = st.tabs(["Lista de Logros", "Crear Logro", "Actualizar/Eliminar Logro"])

    with tab1:
        st.subheader("Lista de Todos los Logros")
        logros = make_api_request("GET", "logros")
        display_entity_list("logros", logros)

    with tab2:
        st.subheader("Crear Nuevo Logro")
        st.warning("""
            **Nota Importante para Logros:**
            Basado en tu `logro_schema.py` (`LogroBase`), cada logro está directamente asociado a un `usuario_id`.
            El `nombre` del logro del controlador anterior (`create_logro` en `logro_controller.py`)
            se asume que es la `descripcion` del schema.
            Por favor, asegúrate de que tu backend esté configurado para manejar esta estructura.
            """)
        with st.form("create_logro_form"):
            users_from_api = make_api_request("GET", "usuarios")
            usuario_options_logro_dict = get_display_options(users_from_api, "usuarios")

            if not usuario_options_logro_dict:
                st.warning("No hay usuarios disponibles. Por favor, crea un usuario primero para crear un logro.")
                selected_usuario_id_logro = None 
            else:
                options_for_user_selectbox = [None] + list(usuario_options_logro_dict.keys())
                selected_usuario_id_logro = st.selectbox("Usuario Asociado al Logro*", 
                                                        options=options_for_user_selectbox, 
                                                        format_func=lambda x: _format_selectbox_option(x, usuario_options_logro_dict, "--- Selecciona un usuario ---"), 
                                                        index=0, 
                                                        key="create_logro_usuario_id")
            
            descripcion = st.text_input("Nombre/Descripción del Logro*", key="create_logro_descripcion")
            valor = st.text_input("Valor del Logro (ej. '100kg', '5k carrera')", key="create_logro_valor")
            
            exercises_from_api = make_api_request("GET", "ejercicios")
            ejercicio_options_logro_dict = get_display_options(exercises_from_api, "ejercicios")
            ejercicio_options_for_select_logro = {None: "--- Ninguno (Logro General) ---"}
            ejercicio_options_for_select_logro.update(ejercicio_options_logro_dict)

            selected_ejercicio_id_logro = st.selectbox("Ejercicio Asociado (Opcional)", 
                                                        options=list(ejercicio_options_for_select_logro.keys()), 
                                                        format_func=lambda x: _format_selectbox_option(x, ejercicio_options_for_select_logro, "--- Ninguno (Logro General) ---"), 
                                                        index=0, 
                                                        key="create_logro_ejercicio_id")

            fecha_logro = st.date_input("Fecha del Logro*", datetime.now().date(), key="create_logro_fecha")
            tipo = st.selectbox("Tipo de Logro (Opcional)", ["", "General", "Peso", "Repeticiones", "Frecuencia", "Distancia"], key="create_logro_tipo")

            submitted = st.form_submit_button("Crear Logro")
            if submitted:
                if selected_usuario_id_logro and descripcion and valor and fecha_logro:
                    logro_data = {
                        "usuario_id": selected_usuario_id_logro,
                        "ejercicio_id": selected_ejercicio_id_logro if selected_ejercicio_id_logro else None,
                        "descripcion": descripcion,
                        "valor": valor,
                        "fecha_logro": datetime.combine(fecha_logro, datetime.min.time()).isoformat(), 
                        "tipo": tipo if tipo else None
                    }
                    response = make_api_request("POST", "logros", logro_data)
                    if response:
                        st.success(f"Logro creado con ID: {response}")
                        st.rerun()
                else:
                    st.warning("Usuario, Descripción, Valor y Fecha del Logro son campos obligatorios.")

    with tab3:
        st.subheader("Actualizar o Eliminar Logro")
        logros_from_api = make_api_request("GET", "logros")
        logro_options_dict = get_display_options(logros_from_api, "logros") 

        if not logro_options_dict:
            st.info("No hay logros disponibles para actualizar o eliminar. Por favor, crea algunos primero.")
        else:
            options_for_selectbox = [None] + list(logro_options_dict.keys())
            
            selected_logro_id = st.selectbox("Selecciona un Logro para Actualizar/Eliminar", 
                                            options=options_for_selectbox, 
                                            format_func=lambda x: _format_selectbox_option(x, logro_options_dict, "--- Selecciona un logro ---"),
                                            index=0, 
                                            key="update_delete_select_logro")

            if selected_logro_id is not None:
                logro_data = make_api_request("GET", f"logros/{selected_logro_id}")
                if logro_data:
                    current_descripcion = logro_data.get("descripcion", "")
                    current_valor = logro_data.get("valor", "")
                    current_fecha_logro_str = logro_data.get("fecha_logro")
                    current_fecha_logro = datetime.now().date()
                    if isinstance(current_fecha_logro_str, str):
                        try:
                            current_fecha_logro = datetime.fromisoformat(current_fecha_logro_str).date()
                        except ValueError:
                            pass
                    current_tipo = logro_data.get("tipo", "")
                    current_ejercicio_id = logro_data.get("ejercicio_id", "")
                    current_usuario_id = logro_data.get("usuario_id", "")

                    with st.form("update_delete_logro_form"):
                        st.write(f"**Usuario Asociado:** {current_usuario_id}")
                        st.write(f"**Ejercicio Asociado:** {current_ejercicio_id if current_ejercicio_id else 'Ninguno'}")
                        
                        new_descripcion = st.text_input("Nueva Descripción", value=current_descripcion, key="update_logro_descripcion")
                        new_valor = st.text_input("Nuevo Valor", value=current_valor, key="update_logro_valor")
                        new_fecha_logro = st.date_input("Nueva Fecha del Logro", value=current_fecha_logro, key="update_logro_fecha")
                        new_tipo = st.selectbox("Nuevo Tipo (Opcional)", ["", "General", "Peso", "Repeticiones", "Frecuencia", "Distancia"], index=(["", "General", "Peso", "Repeticiones", "Frecuencia", "Distancia"].index(current_tipo) if current_tipo in ["", "General", "Peso", "Repeticiones", "Frecuencia", "Distancia"] else 0), key="update_logro_tipo")

                        col_update, col_delete = st.columns(2)
                        update_submitted = col_update.form_submit_button("Actualizar Logro")
                        delete_submitted = col_delete.form_submit_button("Eliminar Logro", help="Esta acción es irreversible.")

                        if update_submitted:
                            update_data = {
                                "descripcion": new_descripcion,
                                "valor": new_valor,
                                "fecha_logro": datetime.combine(new_fecha_logro, datetime.min.time()).isoformat(), 
                                "tipo": new_tipo if new_tipo else None
                            }
                            response = make_api_request("PUT", f"logros/{selected_logro_id}", update_data)
                            if response:
                                st.success(f"Logro {selected_logro_id} actualizado.")
                                st.rerun()
                            else:
                                st.error("Error al actualizar el logro.")

                        if delete_submitted:
                            confirm_delete = st.expander("Confirmar Eliminación")
                            with confirm_delete:
                                st.warning(f"¿Estás seguro de que quieres eliminar el logro '{_format_selectbox_option(selected_logro_id, logro_options_dict, '')}'?")
                                if st.button(f"Sí, Eliminar Logro {_format_selectbox_option(selected_logro_id, logro_options_dict, '')}", key="confirm_delete_achievement_btn"):
                                    response = make_api_request("DELETE", f"logros/{selected_logro_id}")
                                    if response:
                                        st.success("Logro eliminado exitosamente.")
                                        st.rerun()
                                    else:
                                        st.error("Error al eliminar el logro.")
                else:
                    st.info("No se pudieron cargar los detalles del logro seleccionado.")
            else:
                st.info("Por favor, selecciona un logro para ver/modificar sus detalles.")


elif page == "Ejercicios":
    st.title("🏋️‍♂️ Gestión de Ejercicios")

    tab1, tab2, tab3 = st.tabs(["Lista de Ejercicios", "Crear Ejercicio", "Actualizar/Eliminar Ejercicio"])

    with tab1:
        st.subheader("Lista de Todos los Ejercicios")
        ejercicios = make_api_request("GET", "ejercicios")
        display_entity_list("ejercicios", ejercicios)

    with tab2:
        st.subheader("Crear Nuevo Ejercicio")
        with st.form("create_ejercicio_form"):
            nombre = st.text_input("Nombre del Ejercicio*", key="create_ejercicio_nombre")
            grupo_muscular = st.text_input("Grupo Muscular (Opcional)", key="create_ejercicio_grupo_muscular")
            descripcion = st.text_area("Descripción (Opcional)", key="create_ejercicio_descripcion")
            
            submitted = st.form_submit_button("Crear Ejercicio")
            if submitted:
                if nombre:
                    ejercicio_data = {
                        "nombre": nombre,
                        "grupo_muscular": grupo_muscular if grupo_muscular else None,
                        "descripcion": descripcion if descripcion else None
                    }
                    response = make_api_request("POST", "ejercicios", ejercicio_data)
                    if response:
                        st.success(f"Ejercicio creado con ID: {response}")
                        st.rerun()
                else:
                    st.warning("El Nombre del Ejercicio es un campo obligatorio.")

    with tab3:
        st.subheader("Actualizar o Eliminar Ejercicio")
        exercises_from_api = make_api_request("GET", "ejercicios")
        ejercicio_options_dict = get_display_options(exercises_from_api, "ejercicios")

        if not ejercicio_options_dict:
            st.info("No hay ejercicios disponibles para actualizar o eliminar. Por favor, crea algunos primero.")
        else:
            options_for_selectbox = [None] + list(ejercicio_options_dict.keys())
            
            selected_ejercicio_id = st.selectbox("Selecciona un Ejercicio para Actualizar/Eliminar", 
                                            options=options_for_selectbox, 
                                            format_func=lambda x: _format_selectbox_option(x, ejercicio_options_dict, "--- Selecciona un ejercicio ---"),
                                            index=0, 
                                            key="update_delete_select_ejercicio")

            if selected_ejercicio_id is not None:
                ejercicio_data = make_api_request("GET", f"ejercicios/{selected_ejercicio_id}")
                if ejercicio_data:
                    current_nombre = ejercicio_data.get("nombre", "")
                    current_grupo_muscular = ejercicio_data.get("grupo_muscular", "")
                    current_descripcion = ejercicio_data.get("descripcion", "")

                    with st.form("update_delete_ejercicio_form"):
                        new_nombre = st.text_input("Nuevo Nombre", value=current_nombre, key="update_ejercicio_nombre")
                        new_grupo_muscular = st.text_input("Nuevo Grupo Muscular", value=current_grupo_muscular, key="update_ejercicio_grupo_muscular")
                        new_descripcion = st.text_area("Nueva Descripción", value=current_descripcion, key="update_ejercicio_descripcion")

                        col_update, col_delete = st.columns(2)
                        update_submitted = col_update.form_submit_button("Actualizar Ejercicio")
                        delete_submitted = col_delete.form_submit_button("Eliminar Ejercicio", help="Esta acción es irreversible.")

                        if update_submitted:
                            update_data = {
                                "nombre": new_nombre,
                                "grupo_muscular": new_grupo_muscular if new_grupo_muscular else None,
                                "descripcion": new_descripcion if new_descripcion else None
                            }
                            response = make_api_request("PUT", f"ejercicios/{selected_ejercicio_id}", update_data)
                            if response:
                                st.success(f"Ejercicio {selected_ejercicio_id} actualizado: {response.get('message', 'Éxito')}")
                                st.rerun()
                            else:
                                st.error("Error al actualizar el ejercicio.")

                        if delete_submitted:
                            confirm_delete = st.expander("Confirmar Eliminación")
                            with confirm_delete:
                                st.warning(f"¿Estás seguro de que quieres eliminar el ejercicio '{_format_selectbox_option(selected_ejercicio_id, ejercicio_options_dict, '')}'?")
                                if st.button(f"Sí, Eliminar Ejercicio {_format_selectbox_option(selected_ejercicio_id, ejercicio_options_dict, '')}", key="confirm_delete_exercise_btn"):
                                    response = make_api_request("DELETE", f"ejercicios/{selected_ejercicio_id}")
                                    if response:
                                        st.success("Ejercicio eliminado exitosamente.")
                                        st.rerun()
                                    else:
                                        st.error("Error al eliminar el ejercicio.")
                else:
                    st.info("No se pudieron cargar los detalles del ejercicio seleccionado.")
            else:
                st.info("Por favor, selecciona un ejercicio para ver/modificar sus detalles.")


elif page == "Conversaciones":
    st.title("💬 Chatbot / Gestión de Conversaciones")
    st.write("Interactúa con el chatbot y gestiona el historial de conversaciones.")

    tab1, tab2, tab3 = st.tabs(["Chatbot (Beta)", "Lista de Conversaciones", "Análisis de Conversaciones"])

    with tab1:
        st.subheader("Tu Asistente FitFlow")
        st.info("Esta es una simulación del chatbot. Para una funcionalidad completa, necesitarías integrar un modelo de lenguaje grande (LLM) y adaptar las respuestas.")

        users_from_api = make_api_request("GET", "usuarios")
        chat_user_options_dict = get_display_options(users_from_api, "usuarios")
        
        selected_chat_user_id = st.selectbox("Selecciona un Usuario para el Chat", 
                                            options=[None] + list(chat_user_options_dict.keys()), 
                                            format_func=lambda x: _format_selectbox_option(x, chat_user_options_dict, "--- Selecciona un usuario ---"), 
                                            index=0, 
                                            key="chat_user_id")

        if selected_chat_user_id: 
            # Initialize session state for chat history for selected user
            # This will reset if a new user is selected via the selectbox
            if f'chat_history_{selected_chat_user_id}' not in st.session_state:
                st.session_state[f'chat_history_{selected_chat_user_id}'] = []
                st.session_state[f'loaded_chat_history_{selected_chat_user_id}'] = False # Flag to load history once per user selection
            
            # Load existing messages if not already loaded for this user
            if not st.session_state[f'loaded_chat_history_{selected_chat_user_id}']: 
                existing_messages = make_api_request("GET", f"conversaciones/ultimos_mensajes/{selected_chat_user_id}/10") 
                if existing_messages:
                    sorted_messages = sorted(existing_messages, key=lambda x: x.get('fecha', '1900-01-01'))
                    for msg in sorted_messages:
                        st.session_state[f'chat_history_{selected_chat_user_id}'].append({"role": msg.get("rol", "assistant"), "content": msg.get("mensaje", "")})
                st.session_state[f'loaded_chat_history_{selected_chat_user_id}'] = True 

            for message in st.session_state[f'chat_history_{selected_chat_user_id}']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Escribe tu mensaje..."):
                st.session_state[f'chat_history_{selected_chat_user_id}'].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                create_user_msg_data = {
                    "usuario_id": selected_chat_user_id,
                    "mensaje": prompt,
                    "fecha": datetime.now().isoformat(), 
                    "rol": "user",
                    "tema": "general" 
                }
                make_api_request("POST", "conversaciones", create_user_msg_data)

                with st.chat_message("assistant"):
                    with st.spinner("Pensando..."):
                        response_from_llm = f"He recibido tu mensaje: '{prompt}'. ¿Cómo puedo ayudarte con tu entrenamiento?"
                        st.markdown(response_from_llm)
                        
                        create_bot_msg_data = {
                            "usuario_id": selected_chat_user_id,
                            "mensaje": response_from_llm,
                            "fecha": datetime.now().isoformat(), 
                            "rol": "assistant",
                            "tema": "general" 
                        }
                        make_api_request("POST", "conversaciones", create_bot_msg_data)

                st.session_state[f'chat_history_{selected_chat_user_id}'].append({"role": "assistant", "content": response_from_llm})
        else:
            st.info("Por favor, crea o selecciona un usuario para empezar a chatear.")


    with tab2:
        st.subheader("Lista de Todas las Conversaciones")
        conversations_from_api = make_api_request("GET", "conversaciones")
        display_entity_list("conversaciones", conversations_from_api, excluded_keys=["mensaje"]) 

        st.markdown("---")
        st.subheader("Detalle de Conversación (por ID)")
        conv_options_dict = get_display_options(conversations_from_api, "conversaciones")

        if not conv_options_dict:
            st.info("No hay conversaciones disponibles para ver detalles. Por favor, crea algunas primero.")
        else:
            options_for_selectbox = [None] + list(conv_options_dict.keys())
            
            selected_conv_id = st.selectbox("Selecciona una Conversación para ver el detalle", 
                                            options=options_for_selectbox, 
                                            format_func=lambda x: _format_selectbox_option(x, conv_options_dict, "--- Selecciona una conversación ---"), 
                                            index=0, 
                                            key="detail_conv_id")

            if selected_conv_id is not None:
                conv_data = make_api_request("GET", f"conversaciones/{selected_conv_id}")
                if conv_data:
                    st.json(conv_data)
                    if st.button(f"Eliminar Conversación {selected_conv_id}", key="delete_specific_conv_btn"):
                        response = make_api_request("DELETE", f"conversaciones/{selected_conv_id}")
                        if response:
                            st.success("Conversación eliminada exitosamente.")
                            st.rerun()
                        else:
                            st.error("Error al eliminar la conversación.")
                else:
                    st.info("No se pudieron cargar los detalles de la conversación seleccionada.")
            else:
                st.info("Por favor, selecciona una conversación para ver su detalle.")

    with tab3:
        st.subheader("Análisis de Conversaciones por Usuario")
        
        users_from_api_analysis = make_api_request("GET", "usuarios")
        usuario_options_analysis_dict = get_display_options(users_from_api_analysis, "usuarios")
        
        selected_conv_analysis_user_id = st.selectbox("Selecciona un Usuario para Análisis de Conversaciones", 
                                                    options=[None] + list(usuario_options_analysis_dict.keys()), 
                                                    format_func=lambda x: _format_selectbox_option(x, usuario_options_analysis_dict, "--- Selecciona un usuario ---"), 
                                                    index=0, 
                                                    key="conv_analysis_user_id")

        if selected_conv_analysis_user_id is not None:
            st.markdown("---")
            st.write("### Últimos 5 Mensajes")
            ultimos_mensajes = make_api_request("GET", f"conversaciones/ultimos_mensajes/{selected_conv_analysis_user_id}/5")
            if ultimos_mensajes:
                for msg in ultimos_mensajes:
                    st.write(f"- **Mensaje:** {msg.get('mensaje', 'N/A')}")
                    st.write(f"  **Fecha:** {msg.get('fecha', 'N/A')}")
                    st.write(f"  **Rol:** {msg.get('rol', 'N/A')}")
                    st.write(f"  **Tema:** {msg.get('tema', 'N/A')}")
                    st.markdown("---")
            else:
                st.info("No se encontraron mensajes recientes para este usuario.")

            st.write("### Mensajes por Tema")
            tema_input = st.text_input("Introduce un tema para buscar mensajes:", key="tema_conversacion")
            if tema_input:
                mensajes_por_tema = make_api_request("GET", f"conversaciones/por_tema/{selected_conv_analysis_user_id}/{tema_input}")
                if mensajes_por_tema:
                    for msg in mensajes_por_tema:
                        st.write(f"- **Mensaje:** {msg.get('mensaje', 'N/A')}")
                        st.write(f"  **Fecha:** {msg.get('fecha', 'N/A')}")
                        st.write(f"  **Rol:** {msg.get('rol', 'N/A')}")
                    st.markdown("---")
                else:
                    st.info(f"No se encontraron mensajes sobre '{tema_input}' para este usuario.")
            else:
                st.info("Introduce un tema para buscar.")

            st.write("### Análisis de Estado de Ánimo")
            if st.button("Analizar Estado de Ánimo"):
                estado_animo_result = make_api_request("GET", f"conversaciones/analizar_estado_animo/{selected_conv_analysis_user_id}")
                if estado_animo_result:
                    st.success(f"El estado de ánimo detectado es: **{estado_animo_result.get('estado_animo', 'No disponible')}**")
                else:
                    st.error("No se pudo realizar el análisis de estado de ánimo.")
        else:
            st.info("Por favor, selecciona un usuario para analizar sus conversaciones.")


elif page == "Acerca de":
    st.title("ℹ️ Acerca de FitFlow")
    st.write("FitFlow es una aplicación integral para la gestión de tu bienestar físico, diseñada para ayudarte a registrar tus entrenamientos, seguir tu progreso, alcanzar logros y comunicarte con un asistente inteligente.")
    st.markdown("""
    **Características Principales:**
    * **Gestión de Usuarios:** Crea y administra perfiles de usuario.
    * **Registro de Entrenamiento:** Lleva un control detallado de tus ejercicios, pesos y repeticiones.
    * **Seguimiento de Logros:** Define y celebra tus hitos de fitness.
    * **Catálogo de Ejercicios:** Explora y gestiona una base de datos de ejercicios.
    * **Asistente de Conversación:** Interactúa con un chatbot para obtener consejos y soporte (funcionalidad LLM extensible).

    Esta aplicación de gestión está construida con **Streamlit** para la interfaz de usuario y **FastAPI** para el backend de la API, utilizando **MongoDB** como base de datos.
    """)
    st.markdown("---")
    st.subheader("Tecnologías Utilizadas:")
    col_tech1, col_tech2, col_tech3 = st.columns(3)
    with col_tech1:
        st.image("https://streamlit.io/images/brand/streamlit-mark-color.svg", width=100, caption="[Image of Streamlit logo]")
        st.write("Interfaz de Usuario Web")
    with col_tech2:
        st.image("https://fastapi.tiangolo.com/img/logo-with-text/logo-with-text.png", width=100, caption="[Image of FastAPI logo]")
        st.write("API Backend")
    with col_tech3:
        st.image("https://www.mongodb.com/assets/images/global/leaf.png", width=100, caption="[Image of MongoDB logo]")
        st.write("Base de Datos NoSQL")
    st.markdown("---")
    st.markdown("Desarrollado por ...")

