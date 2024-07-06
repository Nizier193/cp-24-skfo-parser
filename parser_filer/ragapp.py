import requests
import sys
import os
import sqlite3
import re


sys.path.append('../..')


class Config:
    RAGAPP_URL = 'https://cp-24-skfo.open-core.ru/api/'
    FILEBASE = 'data/'
    DATABASE_DIR = '../db_dir/db.db'


class RagAPP():
    url = Config.RAGAPP_URL

    def __init__(self):
        pass

    def add_file(self, filename):
        url = self.url + 'management/files'
        # Замените 'file_path' на путь к файлу, который вы хотите загрузить
        try:
            files = {'file': open(os.path.join(Config.FILEBASE, filename), 'rb')}

            print('[FLOW] Posting request to API')
            response = requests.post(url, files=files)

            if response.status_code == 200:
                print("[FLOW] File uploaded successfully!")

            else:
                print(f"[FLOW] Failed to upload file with status code: {response.status_code}")
        except Exception as err:
            print(err)

        return  # Все файлы

    def request(self, question):
        print(f'[FLOW] Got query {question}')
        url = Config.RAGAPP_URL + 'chat/request'  # URL для отправки запроса
        headers = {'Content-Type': 'application/json'}  # Устанавливаем заголовок Content-Type

        # Создаем тело запроса в формате JSON
        payload = {
            "messages": [
                {
                    "content": question,
                    "role": "user"
                }
            ]
        }

        print('[FLOW] Posting request to API')
        # Отправляем POST запрос к API
        response = requests.post(url, json=payload, headers=headers)
        print(f'[FLOW] Got response {response.json().get('result').get('content')}')
        return response.json().get('result').get('content')

    def get_files(self):
        url = self.url + 'management/files'
        return requests.get(url).json()

    def del_files(self, filename):
        url = self.url + f'management/files/{filename}'
        return requests.delete(url)


class TextDatabase:
    table_name = 'TextTable'

    def create_table(self):
        with sqlite3.connect(Config.DATABASE_DIR) as cursor:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name}(id INTEGER PRIMARY KEY, filename TEXT, content TEXT)
                """
            )

    def add_text(self, text, filename):
        print('[DB] Adding new user')
        with sqlite3.connect(Config.DATABASE_DIR) as cursor:
            cursor.execute(
                f"""
                INSERT INTO {self.table_name} (filename, content) VALUES (?, ?);
                """,
                (filename, text)
            )
            print('[DB] User added')

    def delete_cond(self, filename):
        print('[DB] Deleting User')
        with sqlite3.connect(Config.DATABASE_DIR) as cursor:
            result = cursor.execute(
                f"""
                DELETE FROM {self.table_name} WHERE filename="{filename}";
                """
            )

    def get_conv(self, filename):
        print('[DB] Pulling user')
        with sqlite3.connect(Config.DATABASE_DIR) as cursor:
            result = cursor.execute(
                f"""
                SELECT * FROM {self.table_name} WHERE filename="{filename}";
                """
            ).fetchall()

        print(f"[DB] User pulled: {result}")
        return result


def insert_data():
    for filename in os.listdir('../markdown_files'):
        if len(db.get_conv(filename)) == 0:
            db.add_text(
                normalize(open(os.path.join('../markdown_files', filename), 'r', encoding='utf-8').read()),
                filename=filename
            )

def normalize(x):
    pattern = re.compile(r'\s+')
    sentence = re.sub(pattern, '', x)
    return sentence.lower()

def compare(text, db_text):
    if db_text == None:
        return False
    return normalize(text) == db_text

db = TextDatabase()
db.create_table()
flow = RagAPP()