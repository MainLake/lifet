from lifet.coder.coder_protocol import CoderProtocol
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM
from lifet.coder.llm_adapters.system_promt_llm import SYSTEM_PROMT_LLM
from lifet.tools.tool_prototipe import ToolPrototipe
from lifet.memory.memory_manager import MemoryManager

# Colores para consola
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
        self.memory = MemoryManager(max_messages=8)  # Memoria compactada

    def code(self, request: RequestLLM) -> ResponseLLM | None:

        print(f"{Colors.HEADER}{Colors.BOLD}=== INICIANDO AGENTE CODER ==={Colors.ENDC}")
        print(f"{Colors.BOLD}Tools Loaded:{Colors.ENDC}")

        for t in self.tools:
            print(f"  └─ {t.__class__.__name__}")

        print("-" * 60)

        # Contexto del sistema
        system_context = {
            "system_prompt": SYSTEM_PROMT_LLM,
            "tools_available": self.get_tools_description()
        }

        request.request_system_data += "\n" + str(system_context)

        end_task = False

        # memoria temporal de llamdas y contexto anteriores
        #responseLLMAutoCall = []

        iteration_count = 1

        responseLLMEnd = ResponseLLM(
            reasoning="",
            response="",
            tool_calls=[],
            task_end=True
        )

        # Generar un loop de ejecucion
        while not end_task:

            print(f"\n{Colors.CYAN}{Colors.BOLD}>>> ITERACIÓN #{iteration_count}{Colors.ENDC}")

            # INYECTAR MEMORIA COMPACTADA
            memory_context = self.memory.build_context()
            if memory_context:
                request.request_system_data += "\n" + memory_context

            # Llamada al LLM
            responseLLM = self.llm_adapter.generate_content(request)

            # Mostrar reasoning
            if responseLLM.reasoning:
                print(f"{Colors.BLUE}🧠 Reasoning:{Colors.ENDC}")
                print(f"   {responseLLM.reasoning}")

            # Mostrar respuesta
            if responseLLM.response:
                print(f"{Colors.GREEN}🗣️  Response:{Colors.ENDC} {responseLLM.response}")

            end_task = responseLLM.task_end

            # Si terminó, salir del loop
            if end_task:
                print(f"\n{Colors.HEADER}=== TAREA FINALIZADA ==={Colors.ENDC}")

                responseLLMEnd = ResponseLLM(
                    reasoning=responseLLM.reasoning,
                    response=responseLLM.response,
                    tool_calls=[],
                    task_end=True
                )
                break

            # GUARDAR MEMORIA
            self.memory.add(
                reasoning=responseLLM.reasoning,
                response=responseLLM.response,
                tool_calls=responseLLM.tool_calls
            )

            # Ejecutar tool calls
            if responseLLM.tool_calls:
                print(f"\n{Colors.YELLOW}🛠️  TOOL CALLS DETECTED ({len(responseLLM.tool_calls)}){Colors.ENDC}")

                for tool in responseLLM.tool_calls:
                    for tool_avaliable in self.tools:
                        if tool_avaliable.__class__.__name__ == tool.tool_name:

                            print(f"{Colors.YELLOW}   ⚡ Executing: {Colors.BOLD}{tool.tool_name}{Colors.ENDC}")
                            print(f"{Colors.YELLOW}      Args: {tool.arguments}{Colors.ENDC}")

                            result = tool_avaliable.execute(**tool.arguments)

                            if result.error:
                                print(f"{Colors.RED}      ❌ Error: {result.error}{Colors.ENDC}")
                                request.request_system_data += f"\nError al ejecutar {tool.tool_name}: {result.error}"
                            else:
                                output_display = str(result.result)
                                if len(output_display) > 200:
                                    output_display = output_display[:200] + "... [truncated]"
                                print(f"{Colors.GREEN}      ✅ Result: {output_display}{Colors.ENDC}")
                                request.request_system_data += f"\nResultado de {tool.tool_name}: {result.result}"

            iteration_count += 1
            print(f"{Colors.CYAN}{'-'*40}{Colors.ENDC}")

        print("\n\n")
        return responseLLMEnd

    def tool_subscription(self, tools: list[ToolPrototipe]) -> None:
        self.tools = tools

    def get_tools_description(self) -> str:
        description = "Available tools:\n"
        for tool in self.tools:
            description += f"- {tool.__class__.__name__}: {tool.__doc__}: {tool.execute.__doc__}\n"
        return description
