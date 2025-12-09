from lifet.coder.coder import Coder
from lifet.coder.llm_adapters.gemini_adapter import GeminiAdapter
from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.tools.shell_tool import ShellTool
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM


config = LLMConfig(
    api_key="AIzaSyC8w3p3FtrPCZteQrYvyamVzbCk_S0smhY",
    model_name="gemini-2.5-flash",
)

task = RequestLLM(
    request_system_data="Eres un asistente de programacion que ayuda a crear codigo y ejecutar herramientas del sistema.",
    request_user="""
    Necesito que para el proyecto que esta en la ruta ~/projects/task_manager/ agreges animaciones al agregar tareas
    completar tareas o eliminarlas. usa css para agregar las animaciones.
    """
)

adapter = GeminiAdapter(config_llm=config)
coder = Coder(llm_adapter=adapter)

coder.tool_subscription([ShellTool()])

coder.code(task)
