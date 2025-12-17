# lifet: Un Framework Ligero para Agentes Potenciados por IA

`lifet` es un framework de Python modular y extensible diseñado para construir agentes de IA autónomos. Proporciona una estructura clara para conectarse a Modelos de Lenguaje Grandes (LLMs), gestionar la memoria y extender las capacidades del agente con herramientas personalizadas.

## Conceptos Clave

El framework se construye alrededor de algunos componentes clave que trabajan juntos a través de la inyección de dependencias, lo que lo hace altamente desacoplado y fácil de modificar.

### 1. El Coder
El `Coder` es el orquestador central del agente. Gestiona el bucle de ejecución principal, se comunica con el LLM, maneja la ejecución de herramientas y administra el historial de la conversación a través del sistema de memoria.

### 2. Adaptadores de LLM (LLM Adapters)
Los adaptadores son responsables de comunicarse con APIs de LLM específicas. El framework utiliza un enfoque basado en protocolos, por lo que puedes agregar fácilmente soporte para cualquier LLM.

- **`LLMAdapterProtocol`**: Una interfaz que define cómo el `Coder` interactúa con un LLM.
- **Implementaciones**: Se proporcionan `GeminiAdapter` y `DeepSeekAdapter` como ejemplos.

### 3. Memoria (Memory)
El sistema de memoria está desacoplado del `Coder`, permitiéndote conectar diferentes estrategias de memoria.

- **`MemoryProtocol`**: Una interfaz que define los métodos `save_memory` y `get_memory`.
- **`InMemoryMemory`**: Una implementación simple en memoria que almacena el historial de la conversación en una lista. Puedes crear tus propios sistemas de memoria persistente (por ejemplo, basados en archivos o bases de datos) implementando el `MemoryProtocol`.

### 4. Limpiadores de Respuesta (Response Cleaners)
Las respuestas de los LLM a veces pueden ser desordenadas o estar envueltas en un formato no estándar. Los Limpiadores de Respuesta son clases pequeñas e inyectables que sanean la salida cruda de un LLM antes de que sea analizada.

- **`ResponseCleanerProtocol`**: Una interfaz para limpiar cadenas de texto crudas.
- **`GeminiJSONCleaner`**: Un limpiador estándar que elimina bloques de código markdown y corrige problemas comunes de formato JSON.

### 5. Herramientas (Tools)
Las herramientas son la forma de extender las capacidades del agente para interactuar con el mundo exterior (por ejemplo, ejecutar comandos de shell, buscar en la web, etc.).

- **`ToolPrototipe`**: Una clase base para crear nuevas herramientas. Simplemente heredas de ella e implementas el método `execute`.

## Instalación

Para comenzar, clona el repositorio e instala las dependencias requeridas.

```bash
# Se recomienda usar un entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install "pydantic>=2.12.5,<3.0.0" "google-genai>=1.53.0,<2.0.0" "openai>=2.9.0,<3.0.0" "python-dotenv>=1.0.0,<2.0.0"
```

## Configuración de Claves de API

Para manejar las claves de API de forma segura, el framework utiliza un archivo `.env`.

1.  **Crea un archivo `.env`**: Renombra el archivo `.env.example` a `.env`.
2.  **Añade tus claves**: Abre el archivo `.env` y añade tus claves de API para los servicios que vayas a utilizar.

    ```bash
    # .env
    DEEPSEEK_API_KEY="tu_clave_de_api_de_deepseek"
    GEMINI_API_KEY="tu_clave_de_api_de_gemini"
    ```

El framework cargará automáticamente estas claves. **Nunca subas tu archivo `.env` a un repositorio de Git.**

## Cómo Usarlo

El siguiente ejemplo demuestra cómo ensamblar y ejecutar un agente. El sistema cargará la clave de API desde tu archivo `.env`.

```python
# main.py

from lifet.coder.coder import Coder
from lifet.coder.llm_adapters.deepseek_adapter import DeepSeekAdapter
from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.tools.shell_tool import ShellTool
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM
from lifet.memory.memory import InMemoryMemory

# 1. Configurar el LLM
# La clave de API se cargará automáticamente desde tu archivo .env
config = LLMConfig(
    model_name="deepseek-chat",
    service_name="deepseek"  # Especifica el servicio para cargar la clave correcta
)

# Opcional: También puedes pasar la clave directamente si lo prefieres
# config = LLMConfig(
#     model_name="deepseek-chat",
#     service_name="deepseek",
#     api_key="tu_clave_de_api_aqui"
# )

# 2. Instanciar los componentes principales
adapter = DeepSeekAdapter(config_llm=config)
memory = InMemoryMemory()
coder = Coder(llm_adapter=adapter, memory=memory)

# 3. Crear y suscribir herramientas
shell_tool = ShellTool()
coder.tool_subscription([shell_tool])

# 4. Preparar la solicitud inicial
# El Coder ahora maneja internamente la generación de prompts complejos.
# Solo necesitas proporcionar la solicitud directa del usuario.
task = RequestLLM(
    request_system_data="", # Dejar vacío, gestionado por el Coder
    request_user="Lista todos los archivos en el directorio actual, incluyendo los ocultos.",
    json_schema={} 
)

# 5. Ejecutar el agente
final_response = coder.code(task)

if final_response:
    print("El agente ha finalizado su tarea.")
    print(f"Razonamiento Final: {final_response.reasoning}")
    print(f"Respuesta Final: {final_response.response}")
```

## Extensibilidad

### Creando una Nueva Herramienta
Para crear una nueva herramienta, hereda de `ToolPrototipe` e implementa el método `execute`.

```python
from lifet.tools.tool_prototipe import ToolPrototipe, ToolResult

class FileWriteTool(ToolPrototipe):
    """Una herramienta para escribir contenido en un archivo."""

    def execute(self, file_path: str, content: str) -> ToolResult:
        """
        Escribe el contenido dado en el archivo especificado.
        
        Args:
            file_path: La ruta al archivo.
            content: El contenido a escribir.
        """
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return ToolResult(result=f"Se escribió correctamente en {file_path}")
        except Exception as e:
            return ToolResult(error=str(e))

# Luego, suscríbela al coder:
# coder.tool_subscription([ShellTool(), FileWriteTool()])
```

### Creando un Nuevo Adaptador de LLM
Implementa el `LLMAdapterProtocol` para conectarte a un nuevo LLM. También necesitarás un `ResponseCleaner`.

```python
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM
from lifet.coder.llm_adapters.response_cleaner import ResponseCleanerProtocol

class MyCustomLLMAdapter(LLMAdapterProtocol):
    def __init__(self, api_key: str, response_cleaner: ResponseCleanerProtocol):
        self.api_key = api_key
        self.response_cleaner = response_cleaner
        # ... inicializar cliente ...

    def generate_content(self, request: RequestLLM) -> ResponseLLM:
        # ... llamar a tu API de LLM personalizada ...
        raw_response = "..." 
        
        # Limpiar la respuesta
        cleaned_response = self.response_cleaner.clean(raw_response)
        
        # Analizar y devolver un objeto ResponseLLM
        # ...
        pass
```