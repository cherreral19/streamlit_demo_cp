import streamlit as st
import requests
import random

st.set_page_config(layout="wide")

API_BASE_URL = st.secrets["ENDPOINT"]
selected_bot_id = st.secrets["BOT"]


# ------------------------- Funciones API -------------------------
def crear_sesion(chatbot_id, user_id):
    try:
        res = requests.post(
            f"{API_BASE_URL}/create_session",
            json={"chatbot_id": chatbot_id, "user_id": user_id}
        )
        data = res.json().get("data", {})
        return data.get("id"), data.get("userId")
    except:
        return None

def enviar_mensaje(chatbot_id, user_id, session_id, pregunta):
    try:
        res = requests.post(
            f"{API_BASE_URL}/send_message",
            json={
                "chatbot_id": chatbot_id,
                "user_id": user_id,
                "session_id": session_id,
                "pregunta": pregunta
            }
        )
        return res.json().get("data", [])
    except:
        return []

def gen_id(digitos: int) -> str:
    return f"{random.randint(0, 10**digitos - 1):0{digitos}d}"

def extraer_texto_respuesta(respuestas):
    if isinstance(respuestas, list) and respuestas:
        last = respuestas[-1]
        if isinstance(last, dict):
            parts = (last.get("content") or {}).get("parts") or []
            if parts:
                return "".join(
                    p.get("text", "") if isinstance(p, dict) else str(p)
                    for p in parts
                ).strip()
            if "text" in last:
                return str(last["text"]).strip()
        return " ".join(map(str, respuestas)).strip()
    return str(respuestas).strip()

# ------------------------- Estado -------------------------
if "chat_history_by_session" not in st.session_state:
    st.session_state.chat_history_by_session = {}
if "selected_session" not in st.session_state:
    st.session_state.selected_session = None
if "selected_user_session" not in st.session_state:
    st.session_state.selected_user_session = None

st.title("💬 Demo chatbot cineplanet")

# ======================= IZQUIERDA FIJA (SIDEBAR) =======================
with st.sidebar:
    st.header("⚙️ Sesión")
    if st.button("Crear sesión", type="primary", use_container_width=True):
        user_id_auto = gen_id(8)
        res = crear_sesion(selected_bot_id, user_id_auto)
        if res:
            new_session_id, new_user_id = res
            st.session_state.selected_session = new_session_id
            st.session_state.selected_user_session = new_user_id
            st.success(f"✅ Sesión creada\n\n• session_id: {new_session_id}\n• user_id: {new_user_id}")
        else:
            st.error("❌ No se pudo crear la sesión.")

    # Info rápida (opcional)
    if st.session_state.selected_session:
        st.caption(f"Sesión: {st.session_state.selected_session}")
        st.caption(f"User: {st.session_state.selected_user_session}")

# ======================= INPUT FIJO ABAJO =======================
# Colócalo a nivel raíz: queda anclado abajo
prompt = st.chat_input(
    "Escribe tu mensaje..." if st.session_state.selected_session else "Crea una sesión para comenzar..."
)

# ======================= DERECHA (MAIN): CHAT =======================
st.subheader("💬 Chat")

current_session = st.session_state.selected_session
user_id = st.session_state.selected_user_session

if current_session:
    st.info(f"🟢 Sesión activa: {current_session}")
else:
    st.warning("🔴 Crea una sesión para comenzar.")

# Usa la clave de sesión o un placeholder si no hay
historial = st.session_state.chat_history_by_session.setdefault(
    current_session or "no_session", []
)

# 1) PRIMERO: procesar el prompt (si existe)
if prompt and not current_session:
    st.toast("Primero crea una sesión.", icon="⚠️")

if prompt and current_session:
    # Usuario
    historial.append(("user", prompt))
    # Backend
    try:
        respuestas = enviar_mensaje(selected_bot_id, user_id, current_session, prompt)
        texto = respuestas.get("text") or "⚠️ No recibí texto válido del servidor."
    except Exception as e:
        texto = f"⚠️ Ocurrió un error obteniendo la respuesta: {e}"
    # Asistente
    historial.append(("assistant", texto))

# 2) DESPUÉS: pintar el historial (ya incluye lo que se agregó arriba)
for role, text in historial:
    with st.chat_message(role):
        st.markdown(text)