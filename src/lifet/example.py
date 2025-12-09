from lifet.coder.coder import Coder
from lifet.coder.llm_adapters.deepseek_adapter import DeepSeekAdapter
from lifet.coder.llm_adapters.gemini_adapter import GeminiAdapter
from lifet.coder.llm_adapters.config_llm import RESPONSE_SCHEMA, LLMConfig, get_response_schema_str
from lifet.tools.shell_tool import ShellTool
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM
from lifet.coder.llm_adapters.system_promt_llm import generate_system_prompt_llm
from lifet.utils.objects import object_to_json
from lifet.utils.utils_so import get_info_so_json

config = LLMConfig(
    api_key="sk-9d5a46c9960a40089e0fface17047192",
    model_name="deepseek-chat"
)

adapter = DeepSeekAdapter(config_llm=config)
coder = Coder(llm_adapter=adapter)

coder.tool_subscription([ShellTool()])

task = RequestLLM(
    request_system_data=generate_system_prompt_llm(response_schema=get_response_schema_str(), so_info=get_info_so_json(), tools_description=coder.get_tools_description()),
    request_user="""
    Haz commit de los cambios que se han realizado en el proyecto ~/projects/lifet/ usa el estandar de conventional commits para realizar los commits, ademas de eso
    revisa el .gitignore del proyecto para agregar aquellas cosas que no son relevantes para el proyecto como archivos de cache etc, agrega tambien a la gitignore eso 
    del __pycache__ ya que no es algo que deba de mandar a el repositorio
    """,
    json_schema={}
)

coder.code(task)
