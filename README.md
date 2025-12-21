# lifet: Un Framework Ligero para Agentes Potenciados por IA

`lifet` es un framework de Python modular y extensible diseñado para construir agentes de IA autónomos. Proporciona una estructura clara para conectarse a Modelos de Lenguaje Grandes (LLMs), gestionar la memoria y extender las capacidades del agente con herramientas personalizadas.

## Características Principales

- **Arquitectura basada en protocolos**: Componentes desacoplados y fácilmente intercambiables
- **Sistema de memoria flexible**: Soporte para memoria en capas y resumen automático
- **Herramientas extensibles**: Framework para crear y gestionar herramientas personalizadas
- **Adaptadores LLM**: Soporte para múltiples proveedores de LLM
- **Manejo de tokens**: Contadores de tokens para optimización de costos
- **Callbacks**: Sistema de eventos para monitoreo y extensión

## Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd lifet

# Instalar dependencias
pip install -r requirements.txt

# Instalar en modo desarrollo
pip install -e .
```

## Estructura del Proyecto

```
lifet/
├── src/lifet/
│   ├── __init__.py          # Inicialización del paquete
│   ├── coder/              # Núcleo del agente
│   │   ├── coder.py        # Implementación principal del Coder
│   │   ├── coder_protocol.py # Protocolo del Coder
│   │   ├── coder_callbacks.py # Sistema de callbacks
│   │   └── llm_adapters/   # Adaptadores para LLMs
│   ├── tools/              # Sistema de herramientas
│   │   ├── tool_prototipe.py # Protocolo base para herramientas
│   │   ├── read_file_tool.py
│   │   ├── write_file_tool.py
│   │   ├── list_files_tool.py
│   │   └── shell_tool.py
│   ├── memory/             # Sistema de memoria
│   │   ├── memory_protocol.py # Protocolo de memoria
│   │   ├── memory.py       # Implementación base
│   │   ├── layered_memory.py # Memoria en capas
│   │   └── summarizing_memory.py # Memoria con resumen
│   └── utils/              # Utilidades
│       ├── error.py        # Manejo de errores
│       ├── constants.py    # Constantes
│       ├── utils_so.py     # Utilidades del sistema
│       └── objects.py      # Objetos de datos
├── tests/                  # Pruebas unitarias
├── api/                    # API REST (opcional)
└── chat.py                # Ejemplo de aplicación
```

## Conceptos Clave

### 1. El Coder
El `Coder` es el orquestador central del agente. Implementa el protocolo `CoderProtocol` y gestiona:
- Comunicación con el LLM a través de adaptadores
- Ejecución de herramientas suscritas
- Gestión del historial de conversación mediante el sistema de memoria
- Procesamiento de respuestas y extracción de JSON

### 2. Adaptadores de LLM
Los adaptadores (`LLMAdapterProtocol`) son responsables de comunicarse con APIs de LLM específicas:
- `system_promt_llm.py`: Generación de prompts del sistema
- `deepseek_token_counter.py`: Contador de tokens para DeepSeek
- Protocolo base para implementar nuevos adaptadores

### 3. Sistema de Herramientas
Las herramientas (`ToolPrototipe`) extienden las capacidades del agente:
- **Protocolo base**: Define la interfaz para todas las herramientas
- **Herramientas incluidas**: Lectura/escritura de archivos, shell, listado de archivos
- **Extensibilidad**: Fácil creación de herramientas personalizadas

### 4. Sistema de Memoria
La memoria (`MemoryProtocol`) gestiona el historial de conversación:
- **Memoria en capas**: `LayeredMemory` para diferentes niveles de retención
- **Memoria con resumen**: `SummarizingMemory` para compresión automática
- **Protocolo flexible**: Interfaz para implementar nuevos sistemas de memoria

## Uso Básico

```python
from lifet import Coder
from lifet.coder.llm_adapters.system_promt_llm import SystemPromptLLMAdapter
from lifet.memory.layered_memory import LayeredMemory
from lifet.tools.read_file_tool import ReadFileTool
from lifet.tools.write_file_tool import WriteFileTool

# Configurar componentes
llm_adapter = SystemPromptLLMAdapter()
memory = LayeredMemory()
tools = [ReadFileTool(), WriteFileTool()]

# Crear el agente
agent = Coder(llm_adapter=llm_adapter, memory=memory)
agent.tool_subscription(tools)

# Ejecutar una tarea
response = agent.code("Lee el archivo README.md y resúmelo")
print(response)
```

## Ejemplo Completo

Ver `chat.py` para un ejemplo completo de un agente conversacional con:
- Conexión a LLM
- Sistema de memoria persistente
- Herramientas integradas
- Interfaz de línea de comandos

## Extensión del Framework

### Crear una nueva herramienta
```python
from lifet.tools.tool_prototipe import ToolPrototipe, ToolResponse

class CustomTool(ToolPrototipe):
    def __init__(self):
        super().__init__(
            tool_name="custom_tool",
            description="Una herramienta personalizada",
            parameters=["param1", "param2"]
        )
    
    def execute(self, **kwargs) -> ToolResponse:
        # Implementar lógica aquí
        return ToolResponse(
            success=True,
            data={"result": "operación exitosa"}
        )
```

### Implementar un nuevo adaptador LLM
```python
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM

class CustomLLMAdapter(LLMAdapterProtocol):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def request(self, request: RequestLLM) -> ResponseLLM:
        # Implementar llamada a API
        return ResponseLLM(
            response="Respuesta del LLM",
            token_count=100
        )
```

## API

### Coder
- `__init__(llm_adapter, memory)`: Inicializa el agente
- `code(request)`: Procesa una solicitud y devuelve respuesta
- `tool_subscription(tools)`: Suscribe herramientas al agente
- `extract_json_from_text(text)`: Extrae JSON de texto (método estático)

### MemoryProtocol
- `add_interaction(interaction)`: Añade interacción al historial
- `get_history()`: Obtiene historial completo
- `clear()`: Limpia la memoria

### ToolPrototipe
- `execute(**kwargs)`: Ejecuta la herramienta
- `validate_parameters(params)`: Valida parámetros de entrada

## Pruebas

Ejecutar las pruebas unitarias:
```bash
pytest tests/
```

Las pruebas cubren:
- Funcionalidad del Coder
- Sistema de memoria
- Herramientas
- Contadores de tokens
- Chat y conversaciones

## Contribución

1. Fork el repositorio
2. Crear una rama para la funcionalidad
3. Implementar cambios con pruebas
4. Asegurar que todas las pruebas pasen
5. Crear Pull Request

## Licencia

[Incluir información de licencia]

## Contacto

[Información de contacto del mantenedor]
