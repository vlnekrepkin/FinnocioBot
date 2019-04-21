import sqlite3
class DataBase:
    def __init__(self):
        self.database = 'db.db'

        self.users_temp_image = 'users_temp_image'
        self.users_temp_audio = 'users_temp_audio'
        self.users_temp_video = 'users_temp_video'
        self.users_temp_file = 'users_temp_file'
        self.users_gmail_data = 'users_gmail_data'


    def open_base(self):
        self.conn = sqlite3.connect(self.database, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close_base(self):
        self.conn.close()
    # ----------------------------------- АДМИНИСТРИРОВАНИЕ БАЗЫ ДАННЫХ ----------------------------------------------#
    def create_table_users(self):
        # Создание таблицы с данными пользователя
        self.cursor.execute("CREATE TABLE users_telegram (id TEXT, name TEXT, lastname TEXT, username TEXT)")
        self.conn.commit()

    def create_table_gmail_users(self):
        # Создание таблицы с данными Gmail пользователя
        self.cursor.execute("CREATE TABLE users_gmail_data (id TEXT, data TEXT)")
        self.conn.commit()
        
    def create_table_temp_image(self):
        # Создание таблицы с данными фото пользователей
        self.cursor.execute("CREATE TABLE users_temp_image (id TEXT, data TEXT)")
        self.conn.commit()
        
    def create_table_temp_audio(self):
        # Создание таблицы с данными аудио пользователей
        self.cursor.execute("CREATE TABLE users_temp_audio (id TEXT, data TEXT)")
        self.conn.commit()
        
    def create_table_temp_video(self):
        # Создание таблицы с данными видео пользователей
        self.cursor.execute("CREATE TABLE users_temp_video (id TEXT, data TEXT)")
        self.conn.commit()
    
    def create_table_temp_file(self):
        # Создание таблицы с данными файлов пользователя
        self.cursor.execute("CREATE TABLE users_temp_file (id TEXT, data TEXT)")
        self.conn.commit()

    def create_new_base(self):
        # Создание базы данных (всех необходимых таблиц одновременно)
        self.open_base()
        self.create_table_users()
        self.create_table_gmail_users()
        self.create_table_temp_image()
        self.create_table_temp_audio()
        self.create_table_temp_video()
        self.create_table_temp_file()

    def db_delete(self):
        # Удаляет базу со всеми данными
        import os
        if os.path.isfile(self.database):
            os.remove(self.database)
        else:
            print('База была удалена ранее или еще не создана')

    def kill_born_base(self):
        # Удаляет базу с данными и создает новую по шаблону
        self.db_delete()
        self.create_new_base()

    # --------------------------------------------- КОНТЕНТ ---------------------------------------------------------- #
    def create_in_tables_user(self, table, id):
        # При регистрации пользователя создает в таблице ячейку для пользователя
        self.open_base()
        self.cursor.execute("SELECT id FROM " + table)
        registration_data = "'" + id + "', '" + 'First' + "'"
        users = self.cursor.fetchall()
        id = (id,)
        if id not in users or users == []:
            self.cursor.execute("INSERT INTO " + table + " VALUES(" + registration_data + ")")
            self.conn.commit()
        else:
            pass

    def create_in_all_tables_user(self, id):
        # Создание всех ячеек для файлов к одномупользователю
        self.create_in_tables_user(self.users_temp_image, id)
        self.create_in_tables_user(self.users_temp_audio, id)
        self.create_in_tables_user(self.users_temp_video, id)
        self.create_in_tables_user(self.users_temp_file, id)
        self.create_in_tables_user(self.users_gmail_data, id)

    def include_content_table(self, table, id, data_file):
        data = self.search_data_table(table, id)
        data = self.control_data_table(data, data_file)
        self.write_data_table(table, id, data)

    def search_data_table(self, table, id):
        # Возвращает ячейку с данными
        self.open_base()
        self.cursor.execute("SELECT data " + " FROM " + table + " WHERE id=" + id )
        data = self.cursor.fetchall()
        if data != []:
            data = data[0][0]
            data = data.split('&&&')
            self.close_base()
        else:
            data.append('First')
        return data

    def control_data_table(self, data, data_file):
        # Проверяет данные в ячейке. Вносит изменения
        if data_file in data:
            pass
        else:
            if len(data)<5:
                data.append(data_file)
            else:
                data.pop(0)
                data.append(data_file)
        data = '&&&'.join(data)
        return data

    def write_data_table(self, table, id, data):
        # Записывает данные в таблицу
        self.open_base()
        self.cursor.execute("UPDATE " + table + " SET data='" + data + "' WHERE id='" + id + "'""")
        self.conn.commit()
        self.close_base()


    def reverse_data_from_file(self, table, id):
        request_table = self.search_data_table(table, id)
        if request_table == ['First']:
            return 0
        else:
            return request_table


    # ---------------------------------------- TELEGRAM ДАННЫЕ ------------------------------------------------------- #

    def registration(self, *args):
        # Проверяет есть ли пользователь в базе данных. Если пользователь новый то вносит его в базу
        self.open_base()
        self.cursor.execute("SELECT id FROM users_telegram")
        users = self.cursor.fetchall()
        new_user = (args[0],)
        n_user = args[0]
        if new_user not in users:
            self.include_user_telegram(*args)
            self.create_in_all_tables_user(n_user)
        else:
            pass
        self.close_base()

    def include_user_telegram(self, *args):
        # Производит запись пользователя в базу данных
        registration_data = "'" + "','".join(args) + "'"
        self.cursor.execute("INSERT INTO users_telegram VALUES(" + registration_data + ")")
        self.conn.commit()





if __name__ == '__main__':
    data = DataBase()
    data.kill_born_base()



