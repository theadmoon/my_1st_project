import logging
import os
import sqlite3

DB_DIR = 'db'
DB_NAME = 'gpt_helper.db'
DB_TABLE_USERS_NAME = 'users'

logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                    format="%(asctime)s %(message)s",filemode="w")

# Функция для подключения к базе данных или создание новой, если ее еще нет
def create_db(database_name=DB_NAME):
    db_path = f'{database_name}'
    connection = sqlite3.connect(db_path)
    connection.close()

    logging.info(f"DATABASE: Output: База данных успешно создана")

#Функция для выполнения любого sql-запроса для изменения данных
def execute_query(db_file, query, data=None):
    '''
    Функция для выполнения запроса к базе данных.
    Принимает имя файла базы данных, SQL-запрос и опциональные данные для вставки
    '''
    try:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        connection.commit()

        return cursor
    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса:", e)

    finally:
        connection.close()

# Функция для выполнения любого sql-запроса для получения данных (возвращает значения)
def execute_selection_query(sql_query, data=None, db_path=f'{DB_NAME}'):
    try:
        logging.info(f"DATABASE: Execute query: {sql_query}")

        connection =sqlite3.connect(db_path)
        cursor = connection.cursor()

        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)

        rows = cursor.fetchall()
        connection.close()
        return rows
    except sqlite3.Error as e:
        logging.error(f'DATABASE: Ошибка при запросе: {e}')
        print("Ошибка при выполнении запроса:", e)

# Функция для создания новой таблицы (если такой еще нет)
# Получает название и список колонок в формате ИМЯ: ТИП
# Создает запрос CREATE TABLE IF NOT EXIST имя_таблицы (колонка1 ТИП, колонка2 ТИП)
def create_table(table_name):
    sql_query = f'CREATE TABLE IF NOT EXIST {table_name}' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INTEGER, ' \
                f'subject TEXT, ' \
                f'level TEXT, ' \
                f'task TEXT, ' \
                f'answer TEXT)'
    execute_query(sql_query)

# Функция для вывода всей таблицы (для проверки)
# Создает запрос SELECT * FROM имя_таблицы
def print_all_rows(table_name):
    rows = execute_selection_query(f'SELECT * FROM {table_name}')
    for row in rows:
        print(row)

# Функция для удаления всех записей из таблицы
# Создает запрос DELETE FROM имя_таблицы
def clean_table(table_name):
    execute_query(f'DELETE FROM {table_name}')

# Функция для вставки новой строки в таблицу
# Принимает список значений для каждой колонки и название колонок
# Создает запрос INSERT INTO имя_таблицы (колонка1, колонка2) VALUES (?,?)[значение1, значение2]
def insert_row(values):
    columns = '(user_id, subject, level, task, answer)'
    sql_query = f"INSERT INTO {DB_TABLE_USERS_NAME} {columns} VALUES (?,?,?,?,?)"
    execute_query(sql_query,values)

# Функция для проверки, есть ли элемент в указанном столбце таблицы
# Создает запрос SELECT колонка FROM имя_таблицы WHERE колонка == значение LIMIT 1
def is_value_in_table(table_name, column_name, value):
    sql_query = f'SELECT {column_name} FROM {table_name} WHERE {column_name} =? ORDER BY DATE DESC'
    rows = execute_selection_query(sql_query, [value])
    return rows

# Обновить значение в указанной строке и колонки
def update_row_value(user_id, column_name, new_value):
    if is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        sql_query = f'UPDATE {DB_TABLE_USERS_NAME} SET {column_name} =? WHERE user_id = {user_id}'
        execute_query(sql_query, [new_value])
    else:
        logging.info(f'DATABASE: Пользователь с id = {user_id} не найден')
        print("Такого пользователя нет :( ")

