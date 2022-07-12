import telebot
from telebot import types
from Dialogues import Dialogues
from Callbacks import Callbacks
from DataBase import DataBase


TOKEN = ''  # SECRET TELEGRAM TOKEN
bot = telebot.TeleBot(TOKEN)


dialogues_by_id = {}
callbacks_by_id = {}
dict_callbacks_by_id = {}
database = DataBase()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id
    dialogues = Dialogues(bot, database, user_id)
    callbacks = Callbacks(bot, dialogues)
    dict_callbacks = {'start': callbacks.start,
                      'services': callbacks.services,
                      'ask_model': callbacks.ask_model,
                      'ask_material': callbacks.ask_material,
                      'ask_blueprint': callbacks.ask_blueprint,
                      'ask_photo': callbacks.ask_photo}
    dialogues_by_id[user_id] = dialogues
    callbacks_by_id[user_id] = callbacks
    dict_callbacks_by_id[user_id] = dict_callbacks
    dialogues_by_id[user_id].first_handler(message)



@bot.callback_query_handler(func=lambda call: True)
def callback(call: telebot.types.CallbackQuery):
    if call.from_user.id in dict_callbacks_by_id:
        dict_callbacks_by_id[call.from_user.id][dialogues_by_id[call.from_user.id].cur_callback](call)
    else:
        bot.send_message(call.from_user.id, 'Введите /start, чтобы начать работу с ботом :)')




class Bot3D:
    def __init__(self):
        pass


    def run(self):
        while True:
            try:
                print('Bot is running')
                bot.polling(none_stop=True, interval=0)
            except Exception as e:
                print(e)
        # print('Bot is running')
        # bot.polling(none_stop=True, interval=0)













