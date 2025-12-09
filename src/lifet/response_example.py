import json


response = """
--REASONING---
    Primero analicé la solicitud del usuario y determiné que necesitamos ejecutar varios pasos para cumplir con la tarea. 
    El primer paso implica procesar un archivo HTML complejo que contiene múltiples imágenes con posibles enlaces rotos y placeholders. 
    Para esto, necesitamos un script temporal que abra el archivo, modifique los elementos img agregando un atributo 'onerror', 
    y luego lo guarde. Este proceso debe manejar excepciones para capturar cualquier error de lectura o escritura y registrar 
    información útil en caso de fallo. 

    El segundo paso es listar los archivos en el directorio de proyectos para verificar que los cambios se aplicaron correctamente. 
    Esto se hará con un simple comando de shell que muestre detalles de los archivos. 

    El tercer paso implica consultar un endpoint externo para obtener datos necesarios para la siguiente fase del proceso. 
    Se debe incluir la autorización correcta y parámetros de consulta, validando que la respuesta sea exitosa.<<<END>>>
--ENDREASONING---

--RESPONSE---
    Se crearán tres operaciones principales para cumplir la solicitud. 
    La primera modificará el archivo HTML de forma segura, agregando los placeholders donde sea necesario. 
    La segunda listará los archivos en el directorio especificado para asegurar que todo esté en orden. 
    La tercera llamará a un API externo para recuperar datos que podrían ser utilizados en pasos futuros. 
    Cada operación está diseñada para manejar errores de manera controlada, proporcionando registros claros en caso de que algo falle. 
    Al final del proceso, el usuario tendrá información tanto del estado de los archivos locales como de la respuesta del API, 
    lo que permite una visión completa del estado del sistema y de los datos necesarios para continuar con tareas posteriores.<<<END>>>
--ENDRESPONSE---

--TOOLCALLS---
    ---TOOL---
        --TOOLNAME--
            python_script_tool
        --ENDTOOLNAME--
        --ARGUMENTS--
            cat > /tmp/modify_html.py << 'SCRIPT_EOF'\\nimport os\\nimport sys\\nfrom bs4 import BeautifulSoup\\n\\nfile_path = os.path.expanduser('~/projects/prueba_pagina.html')\\n\\ntry:\\n    with open(file_path, 'r', encoding='utf-8') as f:\\n        html_content = f.read()\\n    \\n    soup = BeautifulSoup(html_content, 'html.parser')\\n    \\n    placeholder = \\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24'%3E%3Cpath fill='%23999' d='M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2z'/%3E%3C/svg%3E\\"\\n    \\n    for img in soup.find_all('img'):\\n        img['onerror'] = f\\"this.onerror=null; this.src='{placeholder}';\\"\\n    \\n    with open(file_path, 'w', encoding='utf-8') as f:\\n        f.write(soup.prettify())\\n    \\n    print(f\\"Archivo {file_path} modificado exitosamente\\")\\n\\nexcept Exception as e:\\n    print(f\\"Error: {e}\\", file=sys.stderr)\\n    sys.exit(1)\\nSCRIPT_EOF\\n&& python /tmp/modify_html.py && rm /tmp/modify_html.py
        --ENDARGUMENTS--
    ---ENDTOOL---
--ENDTOOLCALLS---

""".encode('utf-8').decode('utf-8')

reasoning_lines = []
response_lines = []
tool_calls_lines = []


in_reasoning = False
in_response = False
in_tool_calls_lines = False
    
    
for line in response.splitlines():
    
    cleaned_line = line.strip()
    
    if cleaned_line == "":
        continue
    
    if cleaned_line.startswith("--REASONING---"):
        in_reasoning = True
        continue
        
    if in_reasoning:
        if cleaned_line.startswith("--ENDREASONING---"):
            in_reasoning = False
            reasoning_lines[-1] = reasoning_lines[-1].replace("<<<END>>>", "")
        
        else:
            reasoning_lines.append(cleaned_line)
            continue
    
    
    if cleaned_line.startswith("--RESPONSE---"):
        in_response = True
        continue
    
    if in_response:
        if cleaned_line.startswith("--ENDRESPONSE---"):
            in_response = False
            response_lines[-1] = reasoning_lines[-1].replace("<<<END>>>", "")
        
        else:
            response_lines.append(cleaned_line)
            continue
        
    if cleaned_line.startswith("--TOOLCALLS---"):
        in_tool_calls_lines = True
        continue
    
    if in_tool_calls_lines:
        if cleaned_line.startswith("--ENDTOOLCALLS---"):
            in_tool_calls_lines = False
            continue
        else:
            tool_calls_lines.append(cleaned_line)
            continue


#print({
#    "reasoning": "".join(reasoning_lines).strip(),
#    "response": "".join(response_lines).strip(),
#})

xml_text = """
<data>
    <reasoning>
        Primero analicé la solicitud del usuario y determiné que necesitamos ejecutar varios pasos para cumplir con la tarea. 
        El primer paso implica procesar un archivo HTML complejo que contiene múltiples imágenes con posibles enlaces rotos y placeholders. 
        Para esto, necesitamos un script temporal que abra el archivo, modifique los elementos img agregando un atributo 'onerror', 
        y luego lo guarde. Este proceso debe manejar excepciones para capturar cualquier error de lectura o escritura y registrar 
        información útil en caso de fallo.

        El segundo paso es listar los archivos en el directorio de proyectos para verificar que los cambios se aplicaron correctamente. 
        Esto se hará con un simple comando de shell que muestre detalles de los archivos.

        El tercer paso implica consultar un endpoint externo para obtener datos necesarios para la siguiente fase del proceso. 
        Se debe incluir la autorización correcta y parámetros de consulta, validando que la respuesta sea exitosa.
    </reasoning>

    <response>
        Se crearán tres operaciones principales para cumplir la solicitud. 
        La primera modificará el archivo HTML de forma segura, agregando los placeholders donde sea necesario. 
        La segunda listará los archivos en el directorio especificado para asegurar que todo esté en orden. 
        La tercera llamará a un API externo para recuperar datos que podrían ser utilizados en pasos futuros. 
        Cada operación está diseñada para manejar errores de manera controlada, proporcionando registros claros en caso de que algo falle. 
        Al final del proceso, el usuario tendrá información tanto del estado de los archivos locales como de la respuesta del API, 
        lo que permite una visión completa del estado del sistema y de los datos necesarios para continuar con tareas posteriores.
    </response>

    <tool_calls>
        <tool>
            <tool_name>python_script_tool</tool_name>
            <arguments>
                <command>
                    <![CDATA[
                    cat > /tmp/modify_html.py << 'SCRIPT_EOF'
                    import os
                    import sys
                    from bs4 import BeautifulSoup

                    file_path = os.path.expanduser('~/projects/prueba_pagina.html')
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()

                        soup = BeautifulSoup(html_content, 'html.parser')

                        placeholder = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24'><path fill='#999' d='M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2z'/></svg>"
                        for img in soup.find_all('img'):
                            img['onerror'] = f"this.onerror=null; this.src='{placeholder}';"

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(soup.prettify())

                        print(f"Archivo {file_path} modificado exitosamente")

                    except Exception as e:
                        print(f"Error: {e}", file=sys.stderr)
                        sys.exit(1)
                    SCRIPT_EOF
                    && python /tmp/modify_html.py && rm /tmp/modify_html.py
                    ]]>
                </command>
            </arguments>
        </tool>
    </tool_calls>
    <task_end>true</task_end>
</data>
"""

import xml.etree.ElementTree as ET

# Parsear XML
tree = ET.fromstring(xml_text)

reasoning = tree.find('reasoning').text.strip()
response = tree.find('response').text.strip()

# Convertir task_end de string a boolean
task_end_str = tree.find('task_end').text.strip().lower()
task_end = True if task_end_str == 'true' else False

tools = []
for tool in tree.findall('tool_calls/tool'):
    tname = tool.find('tool_name').text.strip()
    # Guardar todo el CDATA dentro de "command"
    command_text = tool.find('arguments/command').text.strip()
    tools.append({
        "tool_name": tname,
        "arguments": {
            "command": command_text
        }
    })

result = {
    "reasoning": reasoning,
    "response": response,
    "tool_calls": tools,
    "task_end": task_end
}
