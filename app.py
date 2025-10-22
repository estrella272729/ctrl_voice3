import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import json
import paho.mqtt.client as paho
from gtts import gTTS
from googletrans import Translator

# ==========================
# FUNCIONES MQTT
# ==========================

def on_publish(client, userdata, result):
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# ==========================
# CONFIGURACIÓN MQTT
# ==========================

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("emma_assistant")
client1.on_message = on_message

# ==========================
# INTERFAZ STREAMLIT
# ==========================

st.set_page_config(page_title="Emma - Asistente de Notas", page_icon="📝", layout="centered")

st.markdown(
    """
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
        .footer {
            text-align: center; 
            font-size: 14px;
            color: #777;
            margin-top: 30px;
        }
    </style>
    """, unsafe_allow_html=True
)

# ==========================
# CABECERA Y PRESENTACIÓN
# ==========================

st.markdown("<div class='title'>🎓 EMMA - Tu Asistente de Clase</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Toma notas por voz mientras estudias o asistes a clase</div>", unsafe_allow_html=True)

# Imagen decorativa
image = Image.open('emma_voice.jpg')  # Reemplaza con tu imagen o 'voice_ctrl.jpg'
st.image(image, width=250, caption="Tu compañera inteligente de notas 🪶")

st.divider()
st.markdown("### 🎤 Habla con Emma")
st.write("Haz clic en el botón para empezar a hablar. Emma transcribirá tu voz y enviará el mensaje para guardar tus notas 🧠")

# ==========================
# BOTÓN DE RECONOCIMIENTO DE VOZ
# ==========================

stt_button = Button(label="🎙️ Iniciar grabación", width=220, button_type="success")

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

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
    }
    recognition.start();
"""))

# Escuchar los eventos de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ==========================
# PROCESAMIENTO DE RESULTADO
# ==========================

if result:
    if "GET_TEXT" in result:
        st.success(f"🗒️ Emma escuchó: **{result.get('GET_TEXT')}**")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"nota": result.get("GET_TEXT").strip()})
        client1.publish("emma_notas", message)

        # Crear carpeta temporal para audios si no existe
        os.makedirs("temp", exist_ok=True)

        # Convertir texto a voz como respuesta de Emma
        tts = gTTS(f"Tu nota ha sido guardada: {result.get('GET_TEXT')}", lang='es')
        tts.save("temp/emma_respuesta.mp3")
        st.audio("temp/emma_respuesta.mp3", format="audio/mp3")

st.markdown("<div class='footer'>Hecho con 💜 por Emma, tu asistente personal de notas</div>", unsafe_allow_html=True)

