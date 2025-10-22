import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

# ==========================
# CONFIGURACIÓN DE PÁGINA
# ==========================
st.set_page_config(page_title="Audio a texto: Emma - Asistente de Notas", page_icon="🎧", layout="centered")

# ==========================
# ESTILOS
# ==========================
st.markdown("""
    <style>
        .title {
            font-size: 40px;
            color: #6C63FF;
            text-align: center;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #4B4B4B;
        }
        .note-box {
            background-color: #EDEBFF;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #6C63FF;
            margin-top: 25px;
            color: #000000; /* texto negro */
            font-size: 18px;
            line-height: 1.6;
        }
        .footer {
            text-align: center;
            font-size: 14px;
            color: #777;
            margin-top: 40px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================
# CABECERA E IMAGEN
# ==========================
st.markdown("<div class='title'>Audio a texto: Emma - Tu Asistente de Clase</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Convierte tu voz en texto y toma notas fácilmente 📝</div>", unsafe_allow_html=True)

# Imagen decorativa (puedes cambiarla)
image = Image.open("emma_voice.jpg")  # o "voice_ctrl.jpg"
st.image(image, width=250, caption="Tu compañera para tomar apuntes por voz ")

st.divider()

# ==========================
# BOTÓN DE RECONOCIMIENTO DE VOZ
# ==========================
st.markdown("### 🎤 Habla con Emma")
st.write("Haz clic en el botón y comienza a hablar. Emma transcribirá lo que digas en texto en tiempo real ")

stt_button = Button(label="🎙️ Iniciar grabación", width=220, button_type="success")

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';  // idioma español

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };
    recognition.start();
"""))

# Capturar resultados de voz a texto
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ==========================
# MOSTRAR RESULTADO
# ==========================
if result:
    if "GET_TEXT" in result:
        transcribed_text = result.get("GET_TEXT")
        st.markdown(f"<div class='note-box'>🗒️ <b>Transcripción:</b><br>{transcribed_text}</div>", unsafe_allow_html=True)


