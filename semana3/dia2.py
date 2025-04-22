from transformers import pipeline

# Crear el pipeline de clasificación de texto
pipe = pipeline("text-classification")

# Usar el pipeline
resultados = pipe(["This restaurant is awesome", "This restaurant is awful"])

# Mostrar los resultados
# print(resultados)

qa = pipeline("question-answering")
result = qa(question="Where do I live?", context="My name is Claude and I live in San Francisco.")
print(result)


