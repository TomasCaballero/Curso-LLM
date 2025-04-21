import os
import sqlalchemy
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

class DatabaseQueryAssistant:
    def __init__(self, connection_string):
        """
        Inicializa el asistente de consultas de base de datos
        
        Args:
            connection_string (str): Cadena de conexión a la base de datos
        """
        # Configurar motor de base de datos
        self.engine = create_engine(connection_string)
        self.inspector = inspect(self.engine)
        
        # Configurar cliente OpenAI
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def get_database_structure(self):
        """
        Obtiene la estructura completa de la base de datos
        
        Returns:
            dict: Diccionario con estructura de tablas, columnas y relaciones
        """
        database_structure = {}
        
        for table_name in self.inspector.get_table_names():
            # Obtener columnas
            columns = self.inspector.get_columns(table_name)
            column_details = [
                {
                    'name': col['name'], 
                    'type': str(col['type']), 
                    'nullable': col.get('nullable', True)
                } for col in columns
            ]
            
            # Obtener claves foráneas
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            fk_details = [
                {
                    'name': fk['name'],
                    'local_column': fk['constrained_columns'][0],
                    'remote_table': fk['referred_table'],
                    'remote_column': fk['referred_columns'][0]
                } for fk in foreign_keys
            ]
            
            database_structure[table_name] = {
                'columns': column_details,
                'foreign_keys': fk_details
            }
        
        return database_structure
    
    def generate_sql_query(self, user_prompt):
        """
        Genera consulta SQL basada en el prompt del usuario
        
        Args:
            user_prompt (str): Descripción de la consulta deseada
        
        Returns:
            str: Consulta SQL generada
        """
        # Obtener estructura de base de datos
        db_structure = self.get_database_structure()
        
        # Preparar prompt para el modelo
        system_prompt = """
        Eres un experto generador de consultas SQL. 
        Debes generar consultas precisas basándote en la estructura de base de datos proporcionada.
        Solo genera la consulta SQL. No añadas explicaciones adicionales.
        Si no puedes generar la consulta, responde con un mensaje de error claro.
        """
        
        full_prompt = f"""
        Estructura de Base de Datos:
        {str(db_structure)}
        
        Consulta solicitada por el usuario:
        {user_prompt}
        
        Genera la consulta SQL correspondiente.
        """
        
        # Generar consulta usando OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        return response.choices[0].message.content

# Ejemplo de uso
def main():
    # Cadena de conexión (ajustar según tu base de datos)
    connection_string = os.getenv('STRING_CONNECTION_POSTGRE')
    
    try:
        # Crear instancia del asistente
        query_assistant = DatabaseQueryAssistant(connection_string)
        
        # Mostrar estructura de base de datos
        estructura = query_assistant.get_database_structure()
        # print("Estructura de Base de Datos:")
        # print(estructura)
        
        # Ejemplo de generación de consulta
        # user_prompt = "Quiero obtener todos los usuarios que hayan creado minimo 10 registros"
        user_prompt = "Quiero obtener todos los registros relacinados con el Cliente OpenFarma en el ultimo mes."
        sql_query = query_assistant.generate_sql_query(user_prompt)
        print("\nConsulta SQL generada:")
        print(sql_query)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()