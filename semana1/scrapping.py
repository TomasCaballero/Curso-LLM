import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI()


class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No tiene título"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

web = Website("https://cursos.frogamesformacion.com/")


system_prompt = "Eres un asistente que analiza el contenido de un sitio web y proporciona un breve resumen, ignorando el texto que podría estar relacionado con la navegación. Responder en Markdown."

def user_prompt_for(website):
    user_prompt = f"Estás viendo un sitio web titulado {website.title}"
    user_prompt += "\nEl contenido de este sitio web es el siguiente; \
    proporciona un breve resumen de este sitio web en formato Markdown. \
    Si incluye noticias, productos o anuncios, resúmelos también.\n\n"
    user_prompt += website.text
    return user_prompt


def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages_for(website)
    )
    return response.choices[0].message.content

print(summarize("https://cursos.frogamesformacion.com"))