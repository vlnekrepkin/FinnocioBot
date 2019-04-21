import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import requests
import shutil
import os
import gtts
from bs4 import BeautifulSoup
from settings import Settings

settings = Settings()

class Action:

    # ---------------------------------- ОТПРАВКА СООБЩЕНИЯ ------------------------------------------------------------

    def send_gmail(self, email, text, data):
        try:
            if data != []:
                msg = MIMEMultipart()
                msg['Subject'] = 'subject'
                msg['From'] = 'finnociobot@gmail.com'
                msg['To'] = email
                text = MIMEText(text)
                msg.attach(text)
                num_photo = 1
                for photo in data:
                    img = open(photo, 'rb').read()
                    image = MIMEImage(img, name=str(num_photo) + '.png')
                    msg.attach(image)
                    num_photo = num_photo + 1
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(settings.bot_gmail, settings.bot_gmailpassword)
                s.sendmail(settings.bot_gmail, email, msg.as_string())
                s.quit()

            else:
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(settings.bot_gmail, settings.bot_gmailpassword)
                s.sendmail(settings.bot_gmail, email, text.encode('utf-8'))
        except:
            return 'error'

    # --------------------------------------------- РАСПОЗНОВАНИЕ ТЕКСТА -----------------------------------------------

    def google_gtts(self, text, user_id):
        # Принимает текст сохраняет временный файл с аудио
        g = gtts.gTTS(text, lang='ru')
        g.save(settings.temp_audio + user_id + settings.name_temp_audio_file)

    def text_in_audio(self, text, user_id):
        # Октрывает аудиофайл и возвращает его побайтовое значение
        self.google_gtts(text, user_id)
        audio = self.open_file_rb(settings.temp_audio, settings.name_temp_audio_file, user_id)
        return audio

    # --------------------------------------------- НОВОСТИ ТУТ.БАЙ ----------------------------------------------------

    def news_tut_by(self):
        # Возвращает список новостей с ТУТ.БАЙ
        news_now = []
        soup = self.beautiful_soup(self.request_get(settings.tut_by))
        info_tut_by = soup.find_all('a', {'class': 'entry__link io-block-link'})
        for news in info_tut_by[:settings.count_news_tut_by]:
            url_news = news.get('href')
            #news = news.find('span', {'class': 'entry-head _title'}).text
            #news_now.append(news)
            news_now.append(url_news)
        return news_now

    # ------------------------------------------- СОХРАНЕНИЕ КОНТЕНТА --------------------------------------------------

    def open_file_rb(self, temp_folder, name_temp_file, user_id):
        # Открывает файл rb и возвращает его
        with open(temp_folder + user_id + name_temp_file, 'rb') as file:
            data = file.read()
            return data

    def save_file_wb(self, data, temp_folder, name_temp_file, user_id):
        # Принимает данные wb и записывает их в файл
        with open(temp_folder + user_id + name_temp_file, 'wb') as file:
            file.write(data)

    def save_image(self, img, name_img, user_id):
        # Сохраняет изображения в папке по умолчанию
        self.save_file_wb(img.content, settings.temp_image, name_img, user_id)

    # --------------------------------------- ЗАПРОСЫ  -----------------------------------------------------------------

    def request_get(self, url):
        # Осуществляет get запрос возвращает ответ
        response = requests.get(url)
        return response

    def beautiful_soup(self, response):
        # Подготавливает ответ для парсинга
        soup = BeautifulSoup(response.text)
        return soup

    def dream_image(self, url_image):
        print(url_image)
        r = requests.post(
            "https://api.deepai.org/api/neural-style",
            files={
                'style': settings.deepai_temp_file,
                'content': url_image,
            },
            headers={'api-key': settings.deepai_api_key}
        )
        print(r.json())
        return r.json()['output_url']
    # ---------------------------------- РАБОЧИЕ ПАПКИ -----------------------------------------------------------------

    def create_user_folder(self, temp_folder, user_id):
        # Создание папки для временного хранения файлов для конкретного пользователя
        user_folder = temp_folder + user_id + '/'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

    def delete_user_folder(self, temp_folder, user_id):
        # Удаление папки для временного хранения файлов для конкретного пользователя
        user_folder = temp_folder + user_id + '/'
        shutil.rmtree(user_folder, ignore_errors=True)

    def create_all_user_folder(self, user_id):
        # Создание всех необходимых папок для хранения файлов для конкретного пользователя
        for folder in settings.temp_folders:
            self.create_user_folder(folder, user_id)

    def create_all_folder(self):
        # Создание всех необходимых папок для хранения файлов
        for folder in settings.temp_folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def delete_all_folder(self):
        # Удаление всех папок для хранения файлов
        for folder in settings.temp_folders:
            shutil.rmtree(folder, ignore_errors=True)

    def kill_born_folder(self):
        # Очищает все папки одновременно
        self.delete_all_folder()
        self.create_all_folder()

if __name__ == '__main__':
    pass
