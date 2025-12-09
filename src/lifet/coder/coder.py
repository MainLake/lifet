from lifet.coder.coder_protocol import CoderProtocol
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM
from lifet.tools.tool_prototipe import ToolPrototipe

# Definimos colores simples para la consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Coder(CoderProtocol):

    tools: list[ToolPrototipe] = []

    def __init__(self, llm_adapter: LLMAdapterProtocol) -> None:
        self.llm_adapter = llm_adapter

    def code(self, request: RequestLLM) -> ResponseLLM | None:
        
        # 1. VISUALIZACIÓN INICIAL
        print(f"{Colors.HEADER}{Colors.BOLD}=== INICIANDO AGENTE CODER ==={Colors.ENDC}")
        print(f"{Colors.BOLD}Tools Loaded:{Colors.ENDC}")
        for t in self.tools:
            print(f"  └─ {t.__class__.__name__}")
        print("-" * 60)

        # Contexto de sistema para el llm
        request.request_system_data

        # Variable de control de finalizacion de tarea
        end_task = False

        # memoria temporal de llamdas y contexto anteriores
        responseLLMAutoCall = []
        iteration_count = 1 

        responseLLMEnd: ResponseLLM = ResponseLLM(
            reasoning="",
            response="",
            tool_calls=[],
            task_end=True
        )
        
        # Generar un loop de ejecucion
        while not end_task:
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}>>> ITERACIÓN #{iteration_count}{Colors.ENDC}")

            # Si hay contexto de las llamadas anteriores, las adjuntamos a la nueva llamada 
            if responseLLMAutoCall:
                for previous_call in responseLLMAutoCall:
                    request.request_system_data += f"\nPrevious reasoning: {previous_call.reasoning}"
                    request.request_system_data += f"\nPrevious response: {previous_call.response}"
                    if previous_call.tool_calls:
                        for tool_call in previous_call.tool_calls:
                            request.request_system_data += f"\nPrevious tool call: {tool_call.tool_name} with arguments {tool_call.arguments}"

            # Llamada al LLM
            responseLLM = self.llm_adapter.generate_content(request)
            print("ResponseLLM: ", responseLLM)
            
            # 2. VISUALIZACIÓN DEL PENSAMIENTO (REASONING)
            if responseLLM.reasoning:
                print(f"{Colors.BLUE}🧠 Reasoning:{Colors.ENDC}")
                print(f"{Colors.BLUE}   {responseLLM.reasoning}{Colors.ENDC}")
            
            # 3. VISUALIZACIÓN DE LA RESPUESTA DIRECTA
            if responseLLM.response:
                print(f"{Colors.GREEN}🗣️  Response:{Colors.ENDC} {responseLLM.response}")

            end_task = responseLLM.task_end

            if end_task:
                print(f"\n{Colors.HEADER}=== TAREA FINALIZADA ==={Colors.ENDC}")
                # Parsear respuesta final a responseLLM 
                responseLLMEnd = ResponseLLM(
                    reasoning=responseLLM.reasoning,
                    response=responseLLM.response,
                    tool_calls=[],
                    task_end=responseLLM.task_end
                )
                break
            
            # Guardamos contexto de las llamadas anteriores
            responseLLMAutoCall.append(responseLLM)

            # Ejecutamos las herramientas llamadas
            if responseLLM.tool_calls:
                print(f"\n{Colors.YELLOW}🛠️  TOOL CALLS DETECTED ({len(responseLLM.tool_calls)}){Colors.ENDC}")
                
                for tool in responseLLM.tool_calls:
                    for tool_avaliable in self.tools:
                        if tool_avaliable.__class__.__name__ == tool.tool_name:
                            
                            # Imprimir ejecución
                            print(f"{Colors.YELLOW}   ⚡ Executing: {Colors.BOLD}{tool.tool_name}{Colors.ENDC}")
                            print(f"{Colors.YELLOW}      Args: {tool.arguments}{Colors.ENDC}")
                            
                            result = tool_avaliable.execute(**tool.arguments)

                            if result.error:
                                # Imprimir Error en ROJO
                                print(f"{Colors.RED}      ❌ Error: {result.error}{Colors.ENDC}")
                                request.request_system_data += f"\nError al ejecutar {tool.tool_name}: {result.error}"
                            else:
                                # Imprimir Éxito (truncado si es muy largo para no ensuciar)
                                output_display = str(result.result)
                                if len(output_display) > 200:
                                    output_display = output_display[:200] + "... [truncated]"
                                
                                print(f"{Colors.GREEN}      ✅ Result: {output_display}{Colors.ENDC}")
                                request.request_system_data += f"\nResultado de {tool.tool_name}: {result.result}"
                            
            iteration_count += 1
            print(f"{Colors.CYAN}{'-'*40}{Colors.ENDC}") # Separador de ciclo

        print('\n\n')
        return responseLLMEnd 


    def tool_subscription(self, tools: list[ToolPrototipe]) -> None:
        self.tools = tools

    def get_tools_description(self) -> str:
        description = "Available tools:\n"
        for tool in self.tools:
            description += f"- {tool.__class__.__name__}: {tool.__doc__}: {tool.execute.__doc__}\n"
        return description


