core_model_dir = "models/dialogue"
nlu_model_dir = "models/news/demo"

from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.channels import CollectingOutputChannel

agent = Agent.load(core_model_dir,
                    interpreter = RasaNLUInterpreter(nlu_model_dir))

def handle_saying(saying):
    res = agent.handle_message(saying)
    # print(type(res))
    return res[0]['text']