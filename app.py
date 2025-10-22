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

# ========================
# CONFIGURACIÓN BÁSICA
# ========================
st.set_page_config(page_title="Asistente Smart Home", page_icon="💡", layout="centered")

st.title("🏡 Asistente de voz para el Hogar Inteligente")
st.subheader("Controla tus dispositivos con la voz")

# Imagen decorativa
image = Image.open("voice_ctrl.jpg")
st.image(image, width=250)

st.write("Di comandos como:")
st.markdown("""
- **Encender la luz de la sala**  
- **Apagar ventilador**  
- **Encender música ambiental**  
""")

# ========================
# MQTT CONFIG
# ========================
def on_publish(client, userdata, result):
    print("Comando enviado al broker MQTT.\n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(1)
    message_received = str(message.payload.decode("utf-8"))
    st.write("🔔 Respuesta del sistema:", message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("SMART-HOME-VOICE")
client1.on_message = on_message


# ========================
# INTERFAZ DE RECONOCIMIENTO DE VOZ
# ========================
st.write("🎙️ Pulsa el botón y da tu orden por voz")

stt_button = Button(label="🎤 Hablar", width=200)
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

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ========================
# PROCESAMIENTO DE COMANDO
# ========================
if result and "GET_TEXT" in result:
    comando = result.get("GET_TEXT").strip().lower()
    st.success(f"🗣️ Comando detectado: **{comando}**")

    client1.on_publish = on_publish
    client1.connect(broker, port)

    message = json.dumps({"comando": comando})
    client1.publish("smart_home/voz", message)

    # Respuesta hablada
    respuesta = "Comando recibido. Ejecutando " + comando
    tts = gTTS(respuesta, lang="es")
    tts.save("respuesta.mp3")

    # Mostrar y reproducir
    audio_file = open("respuesta.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3")

    st.info("💬 El sistema está ejecutando tu orden...")

# ========================
# LIMPIEZA TEMP
# ========================
try:
    os.mkdir("temp")
except:
    pass

