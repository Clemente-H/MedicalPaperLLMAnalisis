import re
from docx import Document

def preprocess_papers_docx(input_file, output_file):
    # Leer el documento .docx
    doc = Document(input_file)
    
    # Extraer el texto completo del documento
    full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Dividir el contenido en documentos individuales
        documents = re.split(r'\n(?=\d+\.)', full_text)
        
        for doc in documents:
            # Extraer el título
            title_match = re.search(r'\d+\.\s*(.*?)\n', doc)
            if title_match:
                title = title_match.group(1).strip()
                
                # Extraer el abstract (todo el contenido después del título)
                abstract = re.sub(r'\d+\.\s*(.*?)\n', '', doc, 1).strip()
                
                # Escribir el título y el abstract en el archivo de salida
                outfile.write(f"TITLE: {title}\n")
                outfile.write(f"ABSTRACT: {abstract}\n\n")