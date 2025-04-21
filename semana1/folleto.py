import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# if api_key and api_key[:8]=='sk-proj-':
#     print("La clave de API parece buena")
# else:
#     print("¿Puede haber un problema con tu clave API? ¡Visita el cuaderno de resolución de problemas!")
    
MODEL = 'gpt-4o-mini'
openai = OpenAI()

class Website:
    """
    Una clase de utilidad para representar un sitio web que hemos scrappeado, ahora con enlaces
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "Sin título"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Título de la Web:\n{self.title}\nContenido de la Web:\n{self.text}\n\n"
    

link_system_prompt = "Se te proporciona una lista de enlaces que se encuentran en una página web. \
Puedes decidir cuáles de los enlaces serían los más relevantes para incluir en un folleto sobre la empresa, \
como enlaces a una página Acerca de, una página de la empresa, las carreras/empleos disponibles o páginas de Cursos/Packs.\n"
link_system_prompt += "Debes responder en JSON como en este ejemplo:"
link_system_prompt += """
{
    "links": [
        {"type": "Pagina Sobre nosotros", "url": "https://url.completa/aqui/va/sobre/nosotros"},
        {"type": "Pagina de Cursos": "url": "https://otra.url.completa/courses"}
    ]
}
"""

def get_links_user_prompt(website):
    user_prompt = f"Aquí hay una lista de enlaces de la página web {website.url} - "
    user_prompt += "Por favor, decide cuáles de estos son enlaces web relevantes para un folleto sobre la empresa. Responde con la URL https completa en formato JSON. \
No incluyas Términos y Condiciones, Privacidad ni enlaces de correo electrónico.\n"
    user_prompt += "Links (puede que algunos sean links relativos):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt


def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
      ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)


def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Links encontrados:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result


system_prompt = "Eres un asistente que analiza el contenido de varias páginas relevantes del sitio web de una empresa\
y crea un folleto breve sobre la empresa para posibles clientes, inversores y nuevos empleados. Responde en formato Markdown.\
Incluye detalles sobre la cultura de la empresa, los clientes, las carreras/empleos y los cursos/packs para futuros empleos si tienes la información."

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"Estás mirando una empresa llamada: {company_name}\n"
    user_prompt += f"Aquí se encuentra el contenido de su página de inicio y otras páginas relevantes; usa esta información para crear un breve folleto de la empresa en Markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:20_000] # Truncar si tiene más de 20.000 caracteres
    return user_prompt


def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
    )
    result = response.choices[0].message.content
    print(result)
    # display(Markdown(result))



create_brochure("Mexané", "https://mexane.com")