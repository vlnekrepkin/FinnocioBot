import telebot
from settings import Settings
import time
from action import Action
from database import DataBase
from telebot import types
import time


db = DataBase()
settings = Settings()
action = Action()

bot = telebot.TeleBot(settings.token)
temp_text = []
temp_data = []
temp_photo_id = []

# /start - начало работы приветствие
@bot.message_handler(commands=['start'])
def start(message):
    # Добавляет пользователя в базу данных
    db.registration(str(message.chat.id),
                    str(message.from_user.first_name),
                    str(message.from_user.last_name),
                    str(message.from_user.username))

    action.create_all_user_folder(str(message.chat.id))

    bot.send_message(message.chat.id, 'Hello {:}'.format(message.from_user.first_name))
    time.sleep(1.0)
    bot.send_message(message.chat.id, 'Меня создали для Академии BelHard\n'
                                      'Сейчас я умею немногое, но меня старательно обучают))')

# Информация о собеседнике
@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(message.chat.id, 'Тебя зовут {:} {:}'.format(message.from_user.first_name,
                                                                  message.from_user.last_name))
    time.sleep(1.0)
    bot.send_message(message.chat.id, 'Твой уникальный номер в этой сети {:}'.format(message.chat.id))
    time.sleep(1.0)
    bot.send_message(message.from_user.id, 'А никнейм похож на {:}'.format(message.from_user.username))

# Показать содержимое временной памяти
@bot.message_handler(commands=['brain'])
def brain(message):
    global temp_text
    if temp_text == []:
        bot.send_message(message.chat.id, 'У меня амнезия я не помню ничего')
    else:
        bot.send_message(message.chat.id,
                         'Иногда у меня каша в голове но я точно знаю, что последнее что ты сказал: \n')
        for text in temp_text:
            bot.send_message(message.chat.id, text)
        bot.send_message(message.chat.id, 'Я могу забыть все это просто нажми : \n'
                                          '/forget')

# Показать содержимое временной памяти
@bot.message_handler(commands=['show_photo'])
def brain(message):
    result_photo = db.reverse_data_from_file(db.users_temp_image, str(message.chat.id))
    if result_photo != 0:
        bot.send_message(message.chat.id, 'Вот, смотри что я нашел')
        for photo in result_photo:
            if photo != 'First':
                bot.send_photo(message.chat.id, photo)
                time.sleep(0.5)

# Показать актуальные новости
@bot.message_handler(commands=['news'])
def news(message):
    bot.send_message(message.chat.id, 'Я спросил у tut.by: что нового? И вот, что он ответил: ')
    news_now = action.news_tut_by()
    for news in news_now:
        bot.send_message(message.chat.id, news)

# Очистить временную память
@bot.message_handler(commands=['forget'])
def forget(message):
    global temp_text
    bot.send_message(message.chat.id, 'Хорошо, я просто начну запоминать заново))')
    temp_text = []

@bot.message_handler(content_types=['photo'])
def photo(message):
    global temp_text
    global temp_data
    global temp_photo_id

    photo_id = message.photo[-1].file_id
    path = bot.get_file(photo_id).file_path
    url = 'https://api.telegram.org/file/bot{}/{}'.format(settings.token, path)
    temp_data.append(url)
    temp_photo_id.append(photo_id)
    img = action.request_get(url)
    name_photo_file = '/' + photo_id + '.jpg'
    action.save_image(img, name_photo_file, str(message.chat.id))
    db.include_content_table(db.users_temp_image, str(message.chat.id), photo_id)

    # ---------------------------------------- ДЕЙСТВИЯ В ОТВЕТ НА ОТПРАВКУ ИЗОБРАЖЕНИЙ --------------------------------


    if len(temp_text) != 0:

        # -------------------------------------------------------------- /dream -----------

        if temp_text[0] == '/dream':
            if len(temp_data) != 0:
                dream = action.dream_image(temp_data[0])
                bot.send_message(message.chat.id, dream)
                temp_data = []

        # ---------------------------------------------------------- /send_gmail -----------

        elif temp_text[0] == '/send_gmail':
            data_photo = []
            if len(temp_photo_id) != 0:
                for photo in temp_photo_id:
                    path = settings.temp_image + str(message.chat.id) + '/' + photo +'.jpg'
                    data_photo.append(path)

                action.send_gmail(temp_text[1], temp_text[1], data_photo)
                temp_text = []


# Ответы на текстовые сообщения. Все сообщения по умолчанию сохраняются в temp_text.
@bot.message_handler(content_types=['text'])
def text(message):
    global temp_text
    global temp_data

    # Если сообщением будет комманда предварительно очистится temp_text
    if message.text in settings.skills_for_bot:
        temp_text = []

    if message.text == '/dream':
        temp_data = []

    # Команда будет внесена в temp_text. От этого будут определяться дальнейшие действия.
    temp_text.append(message.text)

    if temp_text != []:
        print(temp_text)

        # ---------------------------------------- Отправка сообщений --------------------------------------------------

        if temp_text[0] == '/send_gmail':
            temp_data = []

            if len(temp_text) == 1:
                bot.send_message(message.chat.id, 'Было бы неплохо получить email\n')
                result_email = db.reverse_data_from_file(db.users_gmail_data, str(message.chat.id))
                if result_email != 0:
                    bot.send_message(message.chat.id, 'Но ты можешь отправить на один из тех что я уже знаю: ')
                    for email in result_email:
                        if email != 'First':
                            bot.send_message(message.chat.id, email)

            elif len(temp_text) == 2:
                db.include_content_table(db.users_gmail_data, str(message.chat.id), temp_text[1])
                bot.send_message(message.chat.id, 'Окей а теперь введи текст\n'
                                                  'или фото, их я тоже умею отправлять')

            elif len(temp_text) == 3:
                result = action.send_gmail(temp_text[1], temp_text[2], [])
                if result == 'error':
                    bot.send_message(message.chat.id, 'Я не смог отправить сообщение на этот email')
                else:
                    bot.send_message(message.chat.id, 'Ну все, я его отправил')
                temp_text = []

        # --------------------------------- Преобразует текс в аудио ---------------------------------------------------

        elif temp_text[0] == '/tell_me':

            if len(temp_text) == 1:
                bot.send_message(message.chat.id, 'Введи текст и моя подруга скажет его \n')

            elif len(temp_text) == 2:
                audio = action.text_in_audio(temp_text[1], str(message.chat.id))
                bot.send_audio(message.chat.id, audio)
                temp_text = []

        # --------------------------------- Преобразует фото DeepDreamEasy ---------------------------------------------

        elif temp_text[0] == '/dream':


            if len(temp_text) == 1:
                    bot.send_message(message.chat.id, 'Один мой знакомый может делать удивительные картинки\n'
                                                      'загрузи изображение и посмотри что получится')

            elif len(temp_text) == 2:
                bot.send_message(message.chat.id, 'Ты должен был загрузить изображение, а не болтать :)')
                temp_text = temp_text[:1]


        # ------------------------------------- АДМИНИСТРИРОВАНИЕ ------------------------------------------------------

        # Выводит список команд
        elif temp_text[0] == '/Fin5333236Time':
            for admin_action in settings.actions_admin:
                bot.send_message(message.chat.id, admin_action)
                temp_text = []

        # Очищает базу данных
        elif temp_text[0] == '/AbR2aCada9BRA':
            db.kill_born_base()
            bot.send_message(message.chat.id, 'База обновлена')
            temp_text = []

        # Очищает все папки в которых хранятся данные пользователя
        elif temp_text[0] == '/Si93mSaLa4bim':
            action.kill_born_folder()
            bot.send_message(message.chat.id, 'Все данные пользователей удалены')
            temp_text = []

        # ---------------------------------------- ПРОСТЫЕ ОТВЕТЫ НА ВОПРОСЫ -------------------------------------------

        else:
            answer = settings.simple_answer.get(temp_text[-1])
            if answer != None:
                bot.send_message(message.chat.id, answer)
                temp_text = []




if __name__ == '__main__':
    bot.polling(none_stop=True)
