from telebot import types
import telebot
from Dialogues import Dialogues
import Texts


class Callbacks:
    def __init__(self, bot: telebot.TeleBot, dialogues: Dialogues):
        self.bot = bot
        self.dialogues = dialogues
        self.user_id = self.dialogues.user_id

    def __set_user_id__(self, user_id):
        self.user_id = user_id


    def start(self, call):
        if call.data == "services":
            self.dialogues.services()
        elif call.data == "about":
            self.bot.send_message(self.user_id, Texts.about_msg())

    def services(self, call):
        if call.data == '3d_print':
            self.dialogues.order['service'] = '3Д Печать'
            self.dialogues.ask_model()
        elif call.data == '3d_scan':
            self.dialogues.order['service'] = '3Д Сканирование'
            self.bot.send_message(self.user_id, 'Ещё не реализовано :(')
            pass                       # TODO: СКАНИРОВАНИЕ

    def ask_model(self, call):
        if call.data == "yes":
            self.dialogues.order['has_model'] = 'Да'
            self.bot.send_message(self.user_id, 'Отправьте боту файл с вашей моделью для расчёта примерной стоимости')
            self.bot.register_next_step_handler(self.dialogues.last_message, self.dialogues.accept_model)
        elif call.data == "no":
            self.dialogues.order['has_model'] = 'Нет'
            self.dialogues.ask_blueprint()

    def ask_material(self, call):
        self.dialogues.order['material'] = call.data
        if self.dialogues.model is not None:
            self.dialogues.tell_price(self.dialogues.model, self.dialogues.order['material'])
        self.dialogues.ask_wishes()

    def ask_blueprint(self, call):
        if call.data == 'yes':
            self.dialogues.order['has_blueprint'] = 'Да'
            self.bot.send_message(self.user_id, 'Отправьте боту файл/фото с чертежём или эскизом')
            self.bot.register_next_step_handler(self.dialogues.last_message, self.dialogues.accept_blueprint)
        if call.data == 'no':
            self.dialogues.order['has_blueprint'] = 'Нет'
            self.dialogues.ask_photo()

    def ask_photo(self, call):
        if call.data == 'yes':
            self.dialogues.order['has_photo'] = 'Да'
            self.bot.send_message(self.user_id, 'Отправьте боту фото оригинала модели')
            self.bot.register_next_step_handler(self.dialogues.last_message, self.dialogues.accept_photo)
        if call.data == 'no':
            self.dialogues.order['has_photo'] = 'Нет'
            self.dialogues.ask_description()










