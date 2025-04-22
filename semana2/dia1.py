import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from IPython.display import Markdown, display, update_display
# import google.generativeai


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
# google_api_key = os.getenv('GOOGLE_API_KEY')

# if openai_api_key:
#     print(f"OpenAI API Key existe y empieza por {openai_api_key[:8]}")
# else:
#     print("OpenAI API Key Sin Configurar")
    
# if anthropic_api_key:
#     print(f"Anthropic API Key existe y empieza por {anthropic_api_key[:7]}")
# else:
#     print("Anthropic API Key Sin Configurar")

openai = OpenAI()
claude = anthropic.Anthropic()

system_message = "Eres un asistente que es genial contando chistes."
user_prompt = "Cuente un chiste divertido para una audiencia de científicos de datos."

prompts = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_prompt}
  ]

completion = openai.chat.completions.create(
    model='gpt-4o-mini',
    messages=prompts,
    temperature=0.7
)
# print(completion.choices[0].message.content)


result = claude.messages.stream(
    model="claude-3-5-sonnet-20240620",
    max_tokens=200,
    temperature=0.7,
    system=system_message,
    messages=[
        {"role": "user", "content": user_prompt},
    ],
)

# with result as stream:
#     for text in stream.text_stream:
#             print(text, end="", flush=True)