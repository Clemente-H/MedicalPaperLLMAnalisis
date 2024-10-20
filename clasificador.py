import csv
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import pandas as pd

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

OPENAI_API_KEY =  os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

class RelevancePaperExtraction(BaseModel):
    resumen: str
    relevancia: bool
    explicacion: str

system_prompt = f"""
Eres un asistente especializado en análisis de literatura médica, capaz de entender y analizar papers en múltiples idiomas.
Tu trabajo es determinar la relevancia entre dos investigaciones.
Se te daran dos investigaciones y deberas responder de forma estructurada con un resumen (máximo 50 palabras) de la segunda investigación, 
su relevancia (True/False) respecto a la primera, donde True significa que si es relevante y False que no lo es, y una 
explicación sobre por que es o no es relevante (máximo 50 palabras).

Criterios de relevancia:
1. El paper debe describir la existencia de una vía clínica para la estandarización de algún proceso clínico (puede ser tratamiento, operación, procedimiento, post operatorio, diagnóstico, etc.).
2. El paper debe incluir, entre sus resultados (outcomes), un registro de las experiencias de los pacientes.

La primera investigación es la siguiente:

Titulo: Impacto positivo de una vía clínica, como proceso asistencial, en la experiencia del paciente y la familia
Abstract: Teniendo en cuenta la centralidad del paciente y su familia como uno de los valores transversales de la institución, es necesario encontrar una metodología que ayude a mejorar la experiencia de nuestros pacientes durante la atención clínica. Al utilizar las vías clínicas como herramienta para estandarizar los procesos clínicos, buscamos lograr una alta satisfacción del usuario.

Responde SIEMPRE en español.

"""

def analizar_paper(titulo, abstract):
    user_input = f"""
Segunda investigación:
Titulo: {titulo}
Abstract: {abstract}
"""
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        response_format=RelevancePaperExtraction,
    )

    research_paper = completion.choices[0].message.parsed
    return research_paper

# Función principal
def procesar_papers(input_file, output_file):
    df  = pd.read_json(input_file, lines = True, encoding='utf-8')
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for _, row in df.iterrows():
            resultado = analizar_paper(row['Title'], row['Abstract'])
            
            print(f"Título: {row['Title']}")
            print(f"Abstract: {row['Abstract']}")
            print(f"Resumen: {resultado.resumen}")
            print(f"Es Relevante: {resultado.relevancia}")
            print(f"Explicación: {resultado.explicacion}")
            print("-" * 50)
            
            paper_dict = {
                'Título': row['Title'],
                'Abstract':row['Abstract'],
                'Resumen': resultado.resumen,
                'Es Relevante': resultado.relevancia,
                'Explicación': resultado.explicacion
            }
            
            json_line = json.dumps(paper_dict, ensure_ascii=False)
            outfile.write(json_line + '\n')