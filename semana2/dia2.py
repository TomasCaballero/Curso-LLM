import os
import requests
from bs4 import BeautifulSoup
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import gradio as gr

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')
openai = OpenAI()
claude = anthropic.Anthropic()


class Website:
    url: str
    title: str
    text: str

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No se ha encontrado título de la página"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

    def get_contents(self):
        return f"Título de la Web:\n{self.title}\nContenido de la Web:\n{self.text}\n\n"
    

# system_message = "Eres un asistente que analiza el contenido de la página de inicio \
# del sitio web de una empresa y crea un folleto breve sobre la empresa para posibles clientes, inversores y nuevos empleados.\
# Responde en formato Markdown."

def select_tone(tone):
    if tone == "Formal":
        return "Eres un asistente que analiza el contenido de la página de inicio \
del sitio web de una empresa y crea un folleto breve sobre la empresa para posibles clientes, inversores y nuevos empleados.\
utiliza un tono formal y profesional, con un lenguaje técnico y preciso.\
Por ultimo, dame sugerencias que podría agregar para mejorar la página web.\
Responde en formato Markdown."
    elif tone == "Amistoso":
        return "Eres un asistente que analiza el contenido de la página de inicio \
del sitio web de una empresa y crea un folleto breve sobre la empresa para posibles clientes, inversores y nuevos empleados.\
utiliza un tono amigable y cercano, con un lenguaje informal y directo.\
Utiliza emojis y caracteres especiales para hacer el texto más atractivo.\
Por ultimo, dame sugerencias que podría agregar para mejorar la página web.\
Responde en formato Markdown."
    else:
        raise ValueError("Tono Desconocido")


def stream_gpt(prompt, tone):
    messages = [
        {"role": "system", "content": select_tone(tone)},
        {"role": "user", "content": prompt}
      ]
    stream = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result

def stream_claude(prompt, tone):
    result = claude.messages.stream(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.7,
        system=select_tone(tone),
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    response = ""
    with result as stream:
        for text in stream.text_stream:
            response += text or ""
            yield response

def stream_brochure(company_name, url, model, tone):
    prompt = f"Genera un folleto de la empresa {company_name}. Esta es su página de destino:\n"    
    prompt += Website(url).get_contents()
    if model=="GPT":
        result = stream_gpt(prompt, tone)
    elif model=="Claude":
        result = stream_claude(prompt, tone)
    else:
        raise ValueError("Modelo Desconocido")
    yield from result


view = gr.Interface(
    fn=stream_brochure,
    inputs=[
        gr.Textbox(label="Nombre de la Empresa:"),
        gr.Textbox(label="Landing page, recuerda incluir http:// o https://"),
        gr.Dropdown(["GPT", "Claude"], label="Selecciona un modelo"),
        gr.Dropdown(["Formal", "Amistoso"], label="Selecciona un tono")],
    outputs=[gr.Markdown(label="Folleto:")],
    flagging_mode="never"
)
view.launch()