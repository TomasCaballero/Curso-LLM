import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

openai = OpenAI()
MODEL = 'gpt-4o-mini'

system_message = "Eres un asistente útil en una tienda de ropa. \
Debes tratar de alentar gentilmente al cliente a que pruebe los artículos que están en oferta.\
Los sombreros tienen un 60 % de descuento y la mayoría de los demás artículos tienen un 50 % de descuento. \
Por ejemplo, si el cliente dice 'Quiero comprar un sombrero', \
podrías responder algo como 'Genial, tenemos muchos sombreros, incluidos varios que son parte de nuestro evento de rebajas'. \
Anima al cliente a comprar sombreros si no está seguro de qué comprar."

system_message += "\nSi el cliente pide zapatos, debes responder que los zapatos no están en oferta hoy, \
¡pero recuérdale al cliente que mire los sombreros!"

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    if 'cinturon' or 'cinturones' or 'cinturón' in message:
        messages.append({"role": "system", "content": "Para mayor contexto, la tienda no vende cinturones,\
        pero asegúrate de señalar otros artículos en oferta."})
    
    messages.append({"role": "user", "content": message})

    stream = openai.chat.completions.create(model=MODEL, messages=messages, stream=True)

    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        yield response


gr.ChatInterface(fn=chat, type="messages").launch()