import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

import base64
from io import BytesIO
from PIL import Image

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o-mini"
openai = OpenAI()

system_message = "Eres un asistente útil para una aerolínea llamada FlightAI. "
system_message += "Da respuestas breves y corteses, de no más de una oración. "
system_message += "Se siempre preciso. Si no sabes la respuesta, dilo."

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

# image = artist("Tokyo")
# display(image) # solo en jupyter