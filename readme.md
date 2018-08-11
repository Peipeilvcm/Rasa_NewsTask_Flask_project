# RASA + FLASK 搭建 news_task_dialogue_bot

## NLU训练python3 bot.py train_nlu
根据train_file_news.json和nlu_model_config.yml配置文件，模型保存至models/news/demo
data文件夹下total_word_feature_extractor.dat需要自己结合场景语料通过mitie训练，这里直接使用维基百科中文已经训练好的https://pan.baidu.com/share/init?surl=kNENvlHLYWZIddmtWJ7Pdg，密码p4vx

## Dialogue训练python3 bot.py train_dialogue
根据stories.md和上面已经训练好的模型，训练对话管理
动作执行策略选择用LSTM网络训练
保存至models/dialogue

## 在线训练python3 bot.py online_train
主要保存为了stroies.md中的对话语料

## 运行机器人python3 bot.py run

## 运行Flask框架下bot服务器python3 web_flask_main.py
在web_flask分支中