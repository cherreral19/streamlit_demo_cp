import streamlit as st
import requests
import random

API_BASE_URL = st.secrets["ENDPOINT"]
selected_bot_id = st.secrets["BOT"]
# -------------------------
# Funciones API
# -------------------------

def crear_chatbot(payload):
    try:
        res = requests.post(f"{API_BASE_URL}/crear_chatbot", json=payload)
        return res.json().get("data", {}).get("agent_engine_id")
    except:
        return None

# def listar_sesiones(chatbot_id, user_id):
#     try:
#         res = requests.post(f"{API_BASE_URL}/list_sessions", json={"chatbot_id": chatbot_id, "user_id": user_id})
#         data = res.json().get("data", {})
#         return data.get("sessions", [])
#     except:
#         return []

def crear_sesion(chatbot_id, user_id):
    try:
        res = requests.post(f"{API_BASE_URL}/create_session", json={"chatbot_id": chatbot_id, "user_id": user_id})
        session_id = res.json().get("data", {}).get("id")
        userId = res.json().get("data", {}).get("userId")
        return session_id, userId
    except:
        return None

def obtener_sesion(chatbot_id, user_id, session_id):
    try:
        res = requests.post(f"{API_BASE_URL}/get_session", json={
            "chatbot_id": chatbot_id,
            "user_id": user_id,
            "session_id": session_id
        })
        return res.json().get("data")
    except:
        return None

def enviar_mensaje(chatbot_id, user_id, session_id, pregunta):
    try:
        res = requests.post(f"{API_BASE_URL}/send_message", json={
            "chatbot_id": chatbot_id,
            "user_id": user_id,
            "session_id": session_id,
            "pregunta": pregunta
        })
        return res.json().get("data", [])
    except:
        return []

def gen_id(digitos: int) -> str:
    return f"{random.randint(0, 10**digitos - 1):0{digitos}d}"

# -------------------------
# Estado inicial
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_session" not in st.session_state:
    st.session_state.selected_session = None
if "selected_user_session" not in st.session_state:
    st.session_state.selected_user_session = None
if "current_input" not in st.session_state:
    st.session_state.current_input = ""

st.set_page_config(layout="wide")
st.title("💬 Demo chatbot cineplanet")

# -------------------------
# UI - Columnas
# -------------------------
col_left, col_right = st.columns([1, 4], gap="large")


with col_left:
    st.markdown("### Crear sesion")
    if st.button("Crear sesión", type="primary", use_container_width=True):
        user_id_auto = gen_id(8)  # 8 dígitos

        new_session_id, new_user_id = crear_sesion(
            selected_bot_id, user_id_auto
        )

        st.session_state.selected_session = new_session_id
        st.session_state.selected_user_session = new_user_id

        st.success(f"✅ Sesión creada\n\n• session_id: {new_session_id}\n• user_id: {new_user_id}")

# ----------- COLUMNA DERECHA ------------
with col_right:
    st.markdown("### 💬 Chat")
    current_session = st.session_state.get("selected_session")
    user_id = st.session_state.get("selected_user_session")

    if current_session:
        st.info(f"🟢 Sesión activa: {current_session}")
    else:
        st.warning("🔴 Aún no has creado una sesión.")

    for msg in st.session_state.chat_history:
        role, text = msg
        with st.chat_message(role):
            st.markdown(text)

    def procesar_mensaje():
        message = st.session_state.current_input
        if message.strip():
            st.session_state.chat_history.append(("user", message))
            print("selected_bot_id",selected_bot_id)
            print("user_id",user_id)
            print("current_session",current_session)
            print("message",message)

            respuestas = enviar_mensaje(selected_bot_id, user_id, current_session, message)

            print("respuestas:", respuestas)

            parts = respuestas[-1].get("content", {}).get("parts", [])
            texto_unido = "".join(p["text"] for p in parts)

            st.session_state.chat_history.append(("assistant", texto_unido))
            st.session_state.current_input = ""

    if current_session:
        st.chat_input("Escribe tu mensaje...", key="current_input", on_submit=procesar_mensaje)

    else:
        st.chat_input("Crea una sesión para comenzar...")
