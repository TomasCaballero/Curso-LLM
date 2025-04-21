import requests
import ollama
from bs4 import BeautifulSoup
from IPython.display import Markdown, display

MODEL = "llama3.2"

class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No tiene título"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

def user_prompt_for(website):
    user_prompt = f"Estás viendo un sitio web titulado {website.title}"
    user_prompt += "\nEl contenido de este sitio web es el siguiente; \
    proporciona un breve resumen de este sitio web en formato Markdown. \
    Si incluye noticias, productos o anuncios, resúmelos también.\n\n"
    user_prompt += website.text
    return user_prompt

def messages_for(website):
    return [
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize(url):
    website = Website(url)
    response = ollama.chat(
        model = MODEL,
        messages = messages_for(website)
    )
    print(response['message']['content'])

summarize("https://mexane.com/MXN/")
