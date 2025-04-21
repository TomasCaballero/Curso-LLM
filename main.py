import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

# if not api_key:
#     print("No se encontró ninguna clave API: diríjase al cuaderno de resolución de problemas en esta carpeta para identificarla y solucionarla.")
# elif not api_key.startswith("sk-proj-"):
#     print("Se encontró una clave API, pero no inicia sk-proj-; verifique que esté usando la clave correcta; consulte el cuaderno de resolución de problemas")
# elif api_key.strip() != api_key:
#     print("Se encontró una clave API, pero parece que puede tener espacios o caracteres de tabulación al principio o al final; elimínelos; consulte el cuaderno de resolución de problemas")
# else:
#     print("¡Se encontró la clave API y hasta ahora parece buena!")


openai = OpenAI()


class Website:
    """
    Una clase de utilidad para representar un sitio web que hemos scrappeado
    """
    def __init__(self, url):
        """
        Crea este objeto de sitio web a partir de la URL indicada utilizando la biblioteca BeautifulSoup
        """
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No tiene título"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)


web = Website("https://cursos.frogamesformacion.com/")
# print(frog.title)
# print(frog.text)




# Define nuestro mensaje de sistema: puedes experimentar con esto más tarde, cambiando la última oración a "Responder en Markdown en español".

system_prompt = "Eres un asistente que analiza el contenido de un sitio web y proporciona un breve resumen, ignorando el texto que podría estar relacionado con la navegación. Responder en Markdown."


# Una función que escribe un mensaje de usuario que solicita resúmenes de sitios web:

def user_prompt_for(website):
    user_prompt = f"Estás viendo un sitio web titulado {website.title}"
    user_prompt += "\nEl contenido de este sitio web es el siguiente; \
    proporciona un breve resumen de este sitio web en formato Markdown. \
    Si incluye noticias, productos o anuncios, resúmelos también.\n\n"
    user_prompt += website.text
    return user_prompt


# print(user_prompt_for(web))


# Puedes ver cómo esta función crea exactamente el formato anterior
def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

# print(messages_for(web))



# Y ahora: llama a la API de OpenAI. ¡Te resultará muy familiar!
def summarize(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages_for(website)
    )
    return response.choices[0].message.content

print(summarize("https://cursos.frogamesformacion.com"))


# Una función para mostrar esto de forma clara en la salida de Jupyter, usando markdown
# def display_summary(url):
#     summary = summarize(url)
#     display(Markdown(summary))

# display_summary("https://cursos.frogamesformacion.com")