import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# ==========================
# FUNCIONES MQTT
# ==========================
def on_publish(client, userdata, result):
    print("✅ El comando ha sido publicado al broker MQTT\n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write("📩 Mensaje recibido desde Wokwi:", message_received)


# ==========================
# CONFIGURACIÓN MQTT
# ==========================
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message


# ==========================
# INTERFAZ STREAMLIT
# ==========================
st.set_page_config(page_title="Smart Home - Control por Voz", page_icon="💡")

st.title("🏡 INTERFACES MULTIMODALES - Asistente de Voz para Hogar Inteligente")
st.subheader("🎙️ Controla tus dispositivos del hogar con tu voz")

# Imagen decorativa
image = Image.open('voice_ctrl.jpg')
st.image(image, width=250)

st.markdown("""
**Ejemplos de comandos:**
- "Encender la luz del salón" 💡  
- "Apagar el ventilador" 🌬️  
- "Prender la música" 🎵  
- "Apagar todo" 🔌  
""")

st.write("Toca el botón y da tu comando por voz 👇")

# ==========================
# BOTÓN DE RECONOCIMIENTO DE VOZ
# ==========================
stt_button = Button(label="🎤 Iniciar reconocimiento", width=250)

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

# ==========================
# PROCESAR COMANDO DE VOZ
# ==========================
if result:
    if "GET_TEXT" in result:
        comando = result.get("GET_TEXT").strip().lower()
        st.success(f"🗣️ Comando detectado: **{comando}**")

        # Publicar comando a MQTT (para Wokwi)
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": comando})
        ret = client1.publish("voice_ctrl", message)

        # Traducir y generar respuesta hablada
        traductor = Translator()
        respuesta = traductor.translate(f"Comando recibido: {comando}", src='es', dest='es').text
        tts = gTTS(respuesta, lang='es')
        tts.save("respuesta.mp3")

        # Mostrar y reproducir
        audio_file = open("respuesta.mp3", "rb")
        st.audio(audio_file.read(), format="audio/mp3")

        st.info("💡 Enviando orden al sistema inteligente...")

# ==========================
# CREAR CARPETA TEMP
# ==========================
try:
    os.mkdir("temp")
except:
    pass

