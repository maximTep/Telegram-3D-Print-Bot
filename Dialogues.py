import re
import telebot
from telebot import types
import datetime
import Texts
import Funcs
from DataBase import DataBase


class Dialogues:
    def __init__(self, bot: telebot.TeleBot, database: DataBase, user_id):
        self.bot = bot
        self.database = database
        self.cur_callback: str = ''
        self.user_id = user_id
        self.last_message: telebot.types.Message
        self.model = None
        self.model_ext = None
        self.blueprint = None
        self.blueprint_ext = None
        self.photo = None
        self.photo_ext = None
        self.order = {}

    def __set_last_message__(self, last_message: telebot.types.Message):
        self.last_message = last_message

    def __set_user_id__(self, user_id):
        self.user_id = user_id

    def __set_callback__(self, callback: str):
        self.cur_callback = callback

    def __is_start__(self, message: telebot.types.Message):
        self.__set_last_message__(message)
        if message.text == '/start':
            self.start(message)
            return True
        return False

    def __send_order_to_operator__(self, order_id, src_model, src_blueprint, src_photo):
        if self.model is not None:
            with open(src_model, 'rb') as doc:
                self.bot.send_document(Texts.operator_id(), doc,
                                       caption=f'Поступил заказ №{order_id}: {str(self.order)}')
        if self.blueprint is not None:
            with open(src_blueprint, 'rb') as doc:
                self.bot.send_document(Texts.operator_id(), doc,
                                       caption=f'Поступил заказ: {str(self.order)}')
        if self.photo is not None:
            with open(src_photo, 'rb') as doc:
                self.bot.send_photo(Texts.operator_id(), doc,
                                    caption=f'Поступил заказ: {str(self.order)}')

    def first_handler(self, message):
        self.__set_last_message__(message)
        if message.text == '/start':
            self.start(message)
        else:
            self.bot.send_message(self.user_id, 'Введите /start, чтобы начать работу с ботом :)')

    def start(self, message):
        self.__set_last_message__(message)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Каталог услуг', callback_data='services'),
                     types.InlineKeyboardButton(text='О нас', callback_data='about'))
        msg_text = Texts.hello_msg()
        self.bot.send_message(self.user_id, text=msg_text, reply_markup=keyboard)
        self.__set_callback__('start')

    def services(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='3Д Печать', callback_data='3d_print'),
                     types.InlineKeyboardButton(text='3Д Сканирование', callback_data='3d_scan'),)
        msg_text = 'Выберите услугу'
        self.bot.send_message(self.user_id, text=msg_text, reply_markup=keyboard)
        self.__set_callback__('services')

    def ask_model(self):
        keyboard = types.InlineKeyboardMarkup()
        key_order = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_order)
        key_other = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_other)
        msg_text = 'У вас есть 3д модель для печати?'
        self.bot.send_message(self.user_id, text=msg_text, reply_markup=keyboard)
        self.__set_callback__('ask_model')

    def accept_model(self, message: telebot.types.Message):
        if self.__is_start__(message): return
        self.__set_last_message__(message)
        try:
            file_info = self.bot.get_file(message.document.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            self.model = downloaded_file
            self.model_ext = re.findall('\.\w+', message.document.file_name)[0]
        except Exception:
            self.bot.send_message(self.user_id, 'Ошибка загрузки файла, попробуйте ещё раз')
            self.bot.register_next_step_handler(self.last_message, self.accept_model)
            return
        self.bot.send_message(self.user_id, 'Принято')
        # self.tell_price(self.model, ...)
        self.ask_description()

    def tell_price(self, model_downloaded_file, material):
        price = Funcs.evaluate_price(model_downloaded_file, material)
        self.order['eval_price'] = price
        if price > 0:
            self.bot.send_message(self.user_id,
                                  f'Примерная цена изделия: {price} рублей, окончательную стоимость' +
                                  f' назовёт оператор после рассмотрения заказа')
        else:
            self.bot.send_message(self.user_id,
                                  'Для данного файла цена не может быть посчитана автоматически.' +
                                  ' Цену назовёт оператор после рассмотрения заказа')

    def ask_description(self):
        self.bot.send_message(self.user_id, 'Добавьте описание изделия')
        self.bot.register_next_step_handler(self.last_message, self.accept_description)

    def accept_description(self, message):
        if self.__is_start__(message): return
        self.order['description'] = message.text
        self.__set_last_message__(message)
        self.ask_material()

    def ask_material(self):
        materials = Texts.materials_price_dict()
        keyboard = types.InlineKeyboardMarkup()
        for material, price in materials.items():
            keyboard.add(types.InlineKeyboardButton(text=f'{material}', callback_data=f'{material}'))
        msg_text = 'Выберите материал'
        self.bot.send_message(self.user_id, text=msg_text, reply_markup=keyboard)
        self.__set_callback__('ask_material')

    def ask_wishes(self):
        self.bot.send_message(self.user_id, 'Есть какие-то пожелания?')
        self.bot.register_next_step_handler(self.last_message, self.accept_wishes)

    def accept_wishes(self, message):
        if self.__is_start__(message): return
        self.order['wishes'] = message.text
        self.__set_last_message__(message)
        wishes = message.text
        self.ask_contacts()

    def ask_contacts(self):
        self.bot.send_message(self.user_id, 'Оставьте контакты, чтобы оператор мог' +
                                            ' связаться с вами для уточнения деталей заказа')
        self.bot.register_next_step_handler(self.last_message, self.accept_contacts)

    def accept_contacts(self, message):
        if self.__is_start__(message): return
        self.order['contacts'] = message.text
        self.__set_last_message__(message)
        contacts = message.text
        self.goodbye()

    def ask_blueprint(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='yes'),
                     types.InlineKeyboardButton(text='Нет', callback_data='no'), )
        msg_text = 'У вас есть чертёж или эскиз?'
        self.bot.send_message(self.user_id, text=msg_text, reply_markup=keyboard)
        self.__set_callback__('ask_blueprint')

    def accept_blueprint(self, message: telebot.types.Message):
        if self.__is_start__(message): return
        self.__set_last_message__(message)
        try:
            file_info = self.bot.get_file(message.document.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            self.blueprint = downloaded_file
            self.blueprint_ext = re.findall('\.\w+', message.document.file_name)[0]
        except Exception:
            try:
                file_info = self.bot.get_file(message.photo[-1].file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                self.photo = downloaded_file
                self.photo_ext = 'jpeg'
            except Exception as e:
                self.bot.send_message(self.user_id, 'Ошибка загрузки файла, попробуйте ещё раз')
                self.bot.register_next_step_handler(self.last_message, self.accept_blueprint)
                return
        self.bot.send_message(self.user_id, 'Принято')
        self.ask_description()

    def ask_photo(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='yes'),
                     types.InlineKeyboardButton(text='Нет', callback_data='no'), )
        msg_text = 'У вас есть фото оригинала?'
        self.bot.send_message(self.user_id, text=msg_text, reply_markup=keyboard)
        self.__set_callback__('ask_photo')

    def accept_photo(self, message):
        if self.__is_start__(message): return
        self.__set_last_message__(message)
        try:
            file_info = self.bot.get_file(message.photo[-1].file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            self.photo = downloaded_file
            self.photo_ext = 'jpeg'
        except Exception:
            self.bot.send_message(self.user_id, 'Ошибка загрузки файла, попробуйте ещё раз')
            self.bot.register_next_step_handler(self.last_message, self.accept_photo)
            return
        self.bot.send_message(self.user_id, 'Принято')
        self.ask_description()


    def goodbye(self):
        order_id = self.database.get_new_id()
        self.order['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        src_model = 'DataBase\\Models\\' + f'model-{order_id}{self.model_ext}'
        if self.model is not None:
            with open(src_model, 'wb') as new_file:
                new_file.write(self.model)
        src_blueprint = 'DataBase\\Blueprints\\' + f'blueprint-{order_id}{self.blueprint_ext}'
        if self.blueprint is not None:
            with open(src_blueprint, 'wb') as new_file:
                new_file.write(self.blueprint)
        src_photo = f'DataBase\\Photos\\' + f'photo-{order_id}{self.photo_ext}'
        if self.photo is not None:
            with open(src_photo, 'wb') as new_file:
                new_file.write(self.photo)
        self.database.add_order(self.order)
        self.bot.send_message(self.user_id, f'Ваш заказ №{order_id} отправлен!')
        self.__send_order_to_operator__(order_id, src_model, src_blueprint, src_photo)
        self.bot.register_next_step_handler(self.last_message, self.first_handler)










