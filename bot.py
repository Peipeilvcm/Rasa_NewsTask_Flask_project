# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings

from rasa_core.actions import Action
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import SlotSet
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy

logger = logging.getLogger(__name__)


support_search = ["人工智能", "娱乐","体育"]
def extract_item(item):
    if item is None:
        return None
    for name in support_search:
        if name in item:
            return name
    return None


class ActionSearchNews(Action):
    def name(self):
        return 'action_search_news'

    #dispatch用来为哪个用户服务，tracker状态追踪
    def run(self, dispatcher, tracker, domain):
        item = tracker.get_slot("item")
        item = extract_item(item)
        time = tracker.get_slot("time")

        if item is None and time is None:   #默认时间和类型
            dispatcher.utter_message("没有抓取到ITEM或TIME")  
        elif item is None:                  #只知时间
            dispatcher.utter_message("只抓取到TIME = {}".format(time)) 
        elif time is None:                  #只知新闻类型
            dispatcher.utter_message("只抓取到ITEM = {}".format(item)) 
        else:                               
            dispatcher.utter_message("抓取到TIME = {}, ITEM = {}".format(time, item))
        
        return []


class NewsPolicy(KerasPolicy):

    def model_architecture(self, input_shape, output_shape):
        """Build a Keras model and return a compiled model."""
        from keras.layers import LSTM, Activation, Masking, Dense
        from keras.models import Sequential

        # n_hidden = 32  # size of hidden layer in LSTM
        # Build Model
        model = Sequential()
        if len(output_shape) == 1:
            # y is (num examples, num features)
            model.add(Masking(mask_value=-1, input_shape=input_shape))
            model.add(LSTM(self.rnn_size))
            model.add(Dense(input_dim=self.rnn_size, units=output_shape[-1]))
        elif len(output_shape) == 2:
             # y is (num examples, max_dialogue_len, num features)
            model.add(Masking(mask_value=-1,
                              input_shape=(None, input_shape[1])))
            model.add(LSTM(self.rnn_size, return_sequences=True))
            model.add(TimeDistributed(Dense(units=output_shape[-1])))
        else:
            raise ValueError("Cannot construct the model because"
                             "length of output_shape = {} "
                             "should be 1 or 2."
                             "".format(len(output_shape)))

        model.add(Activation("softmax"))

        model.compile(loss="categorical_crossentropy",
                      optimizer="adam",
                      metrics=["accuracy"])

        logger.debug(model.summary())
        return model


def train_dialogue(domain_file="data/domain.yml",
                   model_path="models/dialogue",
                   training_data_file="stories.md"):
    # from rasa_core.featurizers import MaxHistoryTrackerFeaturizer, BinarySingleStateFeaturizer
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history=2), NewsPolicy()])

    training_data = agent.load_data(training_data_file,augmentation_factor=50)
    agent.train(
        training_data,
        epochs=200,
        batch_size=16,
        validation_split=0.2
    )

    agent.persist(model_path)
    return agent


def train_nlu():
    from rasa_nlu.training_data.loading import load_data
    from rasa_nlu import config
    from rasa_nlu.model import Trainer

    training_data = load_data("data/train_file_news.json")
    trainer = Trainer(config.load("data/nlu_model_config.yml"))
    trainer.train(training_data)
    model_directory = trainer.persist("models/", project_name="news", fixed_model_name="demo")

    return model_directory


def run_bot_online(input_channel=ConsoleInputChannel(),
                      interpreter=RasaNLUInterpreter("models/news/demo"),
                      domain_file="data/domain.yml",
                      training_data_file="stories.md"):
                     
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history = 2), KerasPolicy()],
                  interpreter=interpreter)

    agent.train_online(training_data_file,
                       input_channel=input_channel,
                       max_visual_history=2,    #只记录最近的两次对话
                       batch_size=50,
                       epochs=200,
                       max_training_samples=300)

    return agent

def run(serve_forever=True):
    agent = Agent.load("models/dialogue",
                       interpreter=RasaNLUInterpreter("models/news/demo"))

    if serve_forever:
        agent.handle_channel(ConsoleInputChannel())
    return agent


if __name__ == "__main__":
    logging.basicConfig(level="INFO")

    parser = argparse.ArgumentParser(
        description="starts the bot")

    parser.add_argument(
        "task",
        choices=["train_nlu", "train_dialogue", "run", "train_online"],
        help="what the bot should do - e.g. run or train?")
    task = parser.parse_args().task

    # python3 bot.py *args
    if task == "train_nlu":
        train_nlu()
    elif task == "train_dialogue":
        train_dialogue()
    elif task == "run":
        run()
    elif task == "train_online":
        run_bot_online()
    else:
        warnings.warn("Need to pass either 'train_nlu', 'train_dialogue' or "
                      "'run', 'train_online' to use the script.")
        exit(1)
