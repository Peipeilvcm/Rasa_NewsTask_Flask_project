core_model_dir = "models/dialogue"
nlu_model_dir = "models/news/demo"

from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.channels import CollectingOutputChannel

agent = Agent.load(core_model_dir,
                    interpreter = RasaNLUInterpreter(nlu_model_dir))

def handle_saying(saying):
    #saying 格式 : sender_id + '##' + message
    msg = saying.split("##")
    sender_id = msg[0]
    message = msg[1]

    res = agent.handle_message(message,sender_id = sender_id)
    print(res)
    return res[0]['text']
