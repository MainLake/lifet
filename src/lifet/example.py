from lifet.coder.coder import Coder
from lifet.coder.llm_adapters.deepseek_adapter import DeepSeekAdapter
from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.tools.shell_tool import ShellTool
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM
from lifet.memory.memory import InMemoryMemory

# 1. Configure the LLM
config = LLMConfig(
    api_key="sk-85f87a99f45c4fb3af6edd22e7503c81", # IMPORTANT: Add your API key here
    model_name="deepseek-chat"
)

# 2. Instantiate the core components
adapter = DeepSeekAdapter(config_llm=config)
memory = InMemoryMemory()
coder = Coder(llm_adapter=adapter, memory=memory)

# 3. Subscribe tools
coder.tool_subscription([ShellTool()])

# 4. Create the task request
# The Coder now handles the complex system prompt generation internally.
# We only need to provide the user's direct request.
task = RequestLLM(
    request_system_data="", # This is now managed by the Coder
    request_user="""
    Haz commit de los cambios que se han realizado en el proyecto ~/projects/lifet/ usa el estandar de conventional commits para realizar los commits, ademas de eso
    revisa el .gitignore del proyecto para agregar aquellas cosas que no son relevantes para el proyecto como archivos de cache etc, agrega tambien a la gitignore eso 
    del __pycache__ ya que no es algo que deba de mandar a el repositorio
    """,
    json_schema={}
)

# 5. Run the agent
coder.code(task)
