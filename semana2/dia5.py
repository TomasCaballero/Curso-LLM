import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

import base64
from io import BytesIO
from PIL import Image

import tempfile
import subprocess
from io import BytesIO
from pydub import AudioSegment
import time

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o-mini"
openai = OpenAI()

system_message = "Eres un asistente útil para una aerolínea llamada FlightAI. "
system_message += "Da respuestas breves y corteses, de no más de una oración. "
system_message += "Se siempre preciso. Si no sabes la respuesta, dilo."

# -------------------------- Funciones para obtener el precio de los billetes --------------------------
ticket_prices = {"londres": "$799", "parís": "$899", "tokyo": "$1400", "berlín": "$499"}

def get_ticket_price(destination_city):
    print(f"Tool get_ticket_price called for {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "Unknown")


price_function = {
    "name": "get_ticket_price",
    "description": "Obtén el precio de un billete de ida y vuelta a la ciudad de destino. Llámalo siempre que necesites saber el precio del billete, por ejemplo, cuando un cliente pregunte '¿Cuánto cuesta un billete a esta ciudad?'",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "La ciudad a la que el cliente desea viajar",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}
# ------------------------------------------------------------------------

# -------------------------- Funciones para manejar las herramientas --------------------------
tools = [{"type": "function", "function": price_function}]

def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    city = arguments.get('destination_city')
    price = get_ticket_price(city)
    response = {
        "role": "tool",
        "content": json.dumps({"destination_city": city,"price": price}),
        "tool_call_id": message.tool_calls[0].id
    }
    return response, city

# -------------------------- Funciones para generar imágenes --------------------------
def artist(city):
    image_response = openai.images.generate(
            model="dall-e-3",
            prompt=f"Una imagen que representa unas vacaciones en {city}, mostrando lugares turísticos y todo lo único de {city}, en un vibrante estilo pop-art",
            size="1024x1024",
            n=1,
            response_format="b64_json",
        )
    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    return Image.open(BytesIO(image_data))
# ------------------------------------------------------------------------

# --------------- Funciones para reproducir audio ----------------
def play_audio(audio_segment):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "temp_audio.wav")
    try:
        audio_segment.export(temp_path, format="wav")
        time.sleep(3) # El estudiante Dominic consideró que esto era necesario. También podrías intentar comentar para ver si no es necesario en tu PC
        subprocess.call([
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-hide_banner",
            temp_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass
 
def talker(message):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",  # Prueba también de reemplazar onyx por alloy
        input=message
    )
    audio_stream = BytesIO(response.content)
    audio = AudioSegment.from_file(audio_stream, format="mp3")
    play_audio(audio)
# -----------------------------------------------------------------
# -------------------------- Chat ---------------------------------
def chat(history):
    messages = [{"role": "system", "content": system_message}] + history
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    image = None
    
    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        response, city = handle_tool_call(message)
        messages.append(message)
        messages.append(response)
        image = artist(city)
        response = openai.chat.completions.create(model=MODEL, messages=messages)
        
    reply = response.choices[0].message.content
    history += [{"role":"assistant", "content":reply}]

    # Comenta o elimina la siguiente línea si prefiere omitir el audio por ahora.
    talker(reply)
    
    return history, image
# ------------------------------------------------------------------------

# -------------------------- Interfaz de usuario --------------------------
with gr.Blocks() as ui:
    with gr.Row():
        chatbot = gr.Chatbot(height=500, type="messages")
        image_output = gr.Image(height=500)
    with gr.Row():
        entry = gr.Textbox(label="Chatea con nuestro Agente de IA:")
    with gr.Row():
        clear = gr.Button("Clear")

    def do_entry(message, history):
        history += [{"role":"user", "content":message}]
        return "", history

    entry.submit(do_entry, inputs=[entry, chatbot], outputs=[entry, chatbot]).then(
        chat, inputs=chatbot, outputs=[chatbot, image_output]
    )
    clear.click(lambda: None, inputs=None, outputs=chatbot, queue=False)

ui.launch(inbrowser=True)
# ------------------------------------------------------------------------