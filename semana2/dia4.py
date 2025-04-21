# Importación de las bibliotecas necesarias
import os  # Para interactuar con el sistema operativo (ej: leer archivos, variables de entorno)
import json  # Para manejar datos en formato JSON (ej: {"ciudad": "tokyo", "precio": "1400€"})
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env (ej: OPENAI_API_KEY=tu_clave)
from openai import OpenAI  # Cliente de OpenAI para interactuar con la API (ej: enviar mensajes al modelo)
import gradio as gr  # Para crear la interfaz de usuario web (ej: chat interactivo)

# Carga las variables de entorno desde el archivo .env
load_dotenv()
# Obtiene la clave API de OpenAI desde las variables de entorno
openai_api_key = os.getenv('OPENAI_API_KEY')
# Inicializa el cliente de OpenAI
openai = OpenAI()
# Define el modelo de OpenAI a utilizar
MODEL = 'gpt-4o-mini'

# Define el mensaje del sistema que establece el comportamiento del asistente
system_message = "Eres un asistente útil para una aerolínea llamada FlightAI. "
system_message += "Da respuestas breves y corteses, de no más de una oración. "
system_message += "Se siempre preciso. Si no sabes la respuesta, dilo."

# Diccionario que contiene los precios de los billetes para diferentes ciudades
# Ejemplo: Si el usuario pregunta por Tokyo, el precio será 1400€
ticket_prices = {"londres": "799€", "parís": "899€", "tokyo": "1400€", "berlín": "499€"}

# Función que obtiene el precio del billete para una ciudad específica
# Ejemplo: get_ticket_price("Tokyo") -> "1400€"
def get_ticket_price(destination_city):
    print(f"Se solicitó la herramienta get_ticket_price para {destination_city}")
    city = destination_city.lower()  # Convierte la ciudad a minúsculas para evitar problemas de mayúsculas/minúsculas
    return ticket_prices.get(city, "Unknown")  # Retorna el precio o "Unknown" si la ciudad no existe

# Define la función que será utilizada como herramienta por el modelo de OpenAI
# Ejemplo: Cuando el usuario pregunta "¿Cuánto cuesta un vuelo a Tokyo?", el modelo llamará a esta función
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

redirection_function = {
    "name": "redirection",
    "description": "En el caso de no tener la información que el usuario está buscando, sugierele al cliente visitar la página web 'https://www.FlightAI.com' para que pueda encontrar la información que está buscando",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

# Lista de herramientas disponibles para el modelo de OpenAI
tools = [{"type": "function", "function": price_function}, {"type": "function", "function": redirection_function}]

# Función principal de chat que maneja la conversación
# Ejemplo de flujo:
# 1. Usuario: "¿Cuánto cuesta un vuelo a Tokyo?"
# 2. El modelo detecta que necesita el precio y llama a la herramienta
# 3. Se obtiene el precio (1400€)
# 4. El modelo responde: "Un vuelo a Tokyo cuesta 1400€"
def chat(message, history):
    # Construye el historial de mensajes incluyendo el mensaje del sistema
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    # Realiza la primera llamada al modelo de OpenAI
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    # Si el modelo solicita llamar a una herramienta
    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        # Maneja la llamada a la herramienta y obtiene la respuesta
        response, city = handle_tool_call(message)
        # Agrega los mensajes al historial
        messages.append(message)
        messages.append(response)
        # Realiza una segunda llamada al modelo con la información actualizada
        response = openai.chat.completions.create(model=MODEL, messages=messages)
    
    # Retorna el contenido de la respuesta final
    return response.choices[0].message.content

# Función que maneja las llamadas a las herramientas
# Ejemplo:
# Input: {"destination_city": "Tokyo"}
# Output: {"role": "tool", "content": {"destination_city": "tokyo", "price": "1400€"}}
def handle_tool_call(message):
    # Obtiene la llamada a la herramienta
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    
    if function_name == "get_ticket_price":
        # Parsea los argumentos de la llamada
        arguments = json.loads(tool_call.function.arguments)
        # Obtiene la ciudad de destino
        city = arguments.get('destination_city')
        # Obtiene el precio del billete
        price = get_ticket_price(city)
        # Construye la respuesta de la herramienta
        response = {
            "role": "tool",
            "content": json.dumps({"destination_city": city, "price": price}),
            "tool_call_id": message.tool_calls[0].id
        }
        return response, city
    elif function_name == "redirection":
        # Construye la respuesta de redirección
        response = {
            "role": "tool",
            "content": json.dumps({"redirect_url": "https://www.FlightAI.com"}),
            "tool_call_id": message.tool_calls[0].id
        }
        return response, None

# Inicia la interfaz de chat de Gradio
# Crea una interfaz web donde los usuarios pueden:
# 1. Escribir sus preguntas
# 2. Ver el historial de la conversación
# 3. Recibir respuestas del asistente
gr.ChatInterface(fn=chat, type="messages").launch()
