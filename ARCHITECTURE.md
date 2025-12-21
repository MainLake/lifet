# Arquitectura Interna de lifet

Este documento describe la arquitectura interna del framework lifet, explicando cómo está construido, cómo funcionan los protocolos, el bucle principal del Coder y el sistema de memoria.

## Visión General de la Arquitectura

lifet sigue una arquitectura basada en protocolos (interfaces) que permite componentes desacoplados y fácilmente intercambiables. La arquitectura se compone de cuatro pilares principales:

1. **Coder**: El orquestador central que gestiona el flujo de ejecución
2. **Protocolos**: Interfaces que definen contratos entre componentes
3. **Sistema de Herramientas**: Mecanismo para extender capacidades
4. **Sistema de Memoria**: Gestión del historial de conversación

## Sistema de Protocolos

### Protocolos como Base de la Arquitectura

lifet utiliza protocolos de Python (PEP 544) para definir interfaces claras entre componentes:

```python
# Ejemplo del protocolo de memoria
class MemoryProtocol(Protocol):
    def add_interaction(self, interaction: Interaction) -> None:
        """Añade una interacción al historial."""
        ...
    
    def get_history(self) -> List[Interaction]:
        """Obtiene el historial completo."""
        ...
```

### Principales Protocolos

1. **CoderProtocol**: Define la interfaz del agente principal
2. **LLMAdapterProtocol**: Define cómo comunicarse con LLMs
3. **MemoryProtocol**: Define operaciones de memoria
4. **ToolPrototipe**: Define la interfaz para herramientas

### Ventajas del Enfoque Basado en Protocolos

- **Desacoplamiento**: Los componentes solo dependen de interfaces, no de implementaciones
- **Extensibilidad**: Fácil crear nuevas implementaciones
- **Testabilidad**: Mocking simplificado para pruebas
- **Intercambiabilidad**: Cambiar implementaciones sin afectar el sistema

## El Bucle Principal del Coder

### Flujo de Ejecución

El Coder implementa el siguiente bucle principal cuando procesa una solicitud:

```python
def code(self, request: str) -> str:
    # 1. Preparar el contexto
    history = self.memory.get_history()
    
    # 2. Construir el prompt del sistema
    system_prompt = self._build_system_prompt()
    
    # 3. Preparar solicitud para el LLM
    llm_request = RequestLLM(
        system_prompt=system_prompt,
        user_prompt=request,
        history=history
    )
    
    # 4. Llamar al LLM a través del adaptador
    llm_response = self.llm_adapter.request(llm_request)
    
    # 5. Procesar la respuesta
    if self._is_tool_call(llm_response.response):
        # 5a. Extraer llamada a herramienta
        tool_call = self._extract_tool_call(llm_response.response)
        
        # 5b. Ejecutar herramienta
        tool_result = self._execute_tool(tool_call)
        
        # 5c. Actualizar memoria con resultado
        self.memory.add_interaction(Interaction(
            role="tool",
            content=tool_result
        ))
        
        # 5d. Continuar el bucle (recursión)
        return self.code(f"Resultado de herramienta: {tool_result}")
    else:
        # 6. Respuesta final del LLM
        self.memory.add_interaction(Interaction(
            role="assistant",
            content=llm_response.response
        ))
        
        return llm_response.response
```

### Estados del Bucle

1. **Estado Inicial**: Recepción de solicitud del usuario
2. **Estado de Procesamiento LLM**: Generación de respuesta o llamada a herramienta
3. **Estado de Ejecución de Herramienta**: Ejecución de herramienta suscrita
4. **Estado Final**: Devolución de respuesta al usuario

### Recursión para Múltiples Herramientas

El bucle es recursivo: si el LLM decide llamar a una herramienta, el resultado se añade al contexto y se reinicia el proceso, permitiendo cadenas de herramientas.

## Sistema de Memoria

### Arquitectura de Memoria

La memoria en lifet está diseñada como un sistema en capas:

```
┌─────────────────────────────────┐
│      MemoryProtocol (Interface) │
└────────────────┬────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼─────┐           ┌───────▼──────┐
│ Memory  │           │ LayeredMemory│
│ (Base)  │           │              │
└─────────┘           └───────┬──────┘
                              │
                     ┌────────▼────────┐
                     │ SummarizingMemory│
                     │                 │
                     └─────────────────┘
```

### Implementaciones de Memoria

1. **Memory (Base)**: Implementación simple con lista
2. **LayeredMemory**: Memoria en capas con diferentes niveles de retención
3. **SummarizingMemory**: Compresión automática del historial

### Estructura de Datos

```python
@dataclass
class Interaction:
    role: str  # "user", "assistant", "tool", "system"
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Gestión del Contexto

La memoria gestiona:
- **Historial completo**: Todas las interacciones
- **Ventana de contexto**: Subconjunto enviado al LLM
- **Resúmenes**: Versiones comprimidas de conversaciones largas
- **Metadatos**: Información adicional para cada interacción

## Sistema de Herramientas

### Registro y Ejecución

Las herramientas se suscriben al Coder y se ejecutan dinámicamente:

```python
# Suscripción de herramientas
agent.tool_subscription([
    ReadFileTool(),
    WriteFileTool(),
    ShellTool()
])

# Durante la ejecución
for tool in self.tools:
    if tool.tool_name == requested_tool:
        return tool.execute(**parameters)
```

### Protocolo de Herramienta

Todas las herramientas implementan `ToolPrototipe`:

```python
class ToolPrototipe(Protocol):
    tool_name: str
    description: str
    parameters: List[str]
    
    def execute(self, **kwargs) -> ToolResponse:
        ...
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        ...
```

## Adaptadores LLM

### Abstracción de Proveedores

Los adaptadores abstraen las diferencias entre proveedores de LLM:

```python
class LLMAdapterProtocol(Protocol):
    def request(self, request: RequestLLM) -> ResponseLLM:
        ...
```

### Flujo de Comunicación

1. **RequestLLM**: Contiene prompt del sistema, prompt del usuario e historial
2. **Procesamiento**: El adaptador formatea según la API del proveedor
3. **ResponseLLM**: Devuelve respuesta y conteo de tokens

## Sistema de Callbacks

### Eventos y Hooks

El sistema de callbacks permite extensión en puntos clave:

```python
class CoderCallbacks:
    def on_tool_execution_start(self, tool_name: str, params: Dict):
        """Antes de ejecutar herramienta."""
        ...
    
    def on_llm_response(self, response: str):
        """Después de recibir respuesta del LLM."""
        ...
```

### Puntos de Extensión

- **Pre-procesamiento**: Modificar solicitudes antes del LLM
- **Post-procesamiento**: Transformar respuestas del LLM
- **Monitoreo**: Logging y métricas
- **Validación**: Verificar entradas/salidas

## Flujo de Datos Completo

```
Usuario → Coder → Memoria (historial) → LLMAdapter → API LLM
    ↑                                     ↓
    │                             Respuesta LLM
    │                                     ↓
    │                             ¿Llamada a herramienta?
    │                                     ↓
    ├───────────── Sí ──────────→ Ejecutar herramienta
    │                                     ↓
    │                             Actualizar memoria
    │                                     ↓
    └───────────── Repetir ────────┐
                                   ↓
                            Respuesta final → Usuario
```

## Consideraciones de Diseño

### 1. Token Management
- Conteo de tokens para optimización de costos
- Truncamiento inteligente del historial
- Estimación de límites de contexto

### 2. Error Handling
- Recuperación elegante de fallos
- Reintentos automáticos
- Fallback a comportamientos seguros

### 3. Extensibilidad
- Registro dinámico de componentes
- Inyección de dependencias
- Plugins y módulos

### 4. Performance
- Caching de respuestas
- Procesamiento asíncrono
- Optimización de llamadas a API

## Ejemplo de Flujo Completo

```python
# 1. Usuario envía solicitud
user_request = "Lee el archivo config.yaml y dime qué puerto usa"

# 2. Coder procesa
#    - Obtiene historial de memoria
#    - Construye prompt con herramientas disponibles
#    - Envía a LLM

# 3. LLM responde con llamada a herramienta
llm_response = "{"tool_calls": [{"tool_name": "read_file", ...}]}"

# 4. Coder ejecuta herramienta
tool_result = read_file_tool.execute(file_path="config.yaml")

# 5. Actualiza memoria y repite
#    - Añade resultado al historial
#    - Vuelve a llamar al LLM con nuevo contexto

# 6. LLM da respuesta final
final_response = "El archivo config.yaml usa el puerto 8080"
```

## Conclusión

lifet está construido sobre principios de diseño sólidos:
- **Protocolos primero**: Interfaces claras para todos los componentes
- **Bucle recursivo**: Procesamiento flexible de herramientas múltiples
- **Memoria estratificada**: Gestión eficiente del contexto
- **Extensibilidad**: Fácil añadir nuevas capacidades

Esta arquitectura permite construir agentes de IA robustos, mantenibles y extensibles para una variedad de aplicaciones.
