import logging
import os
import sqlite3

DB_DIR = 'db'
# DB_NAME = 'gpt_helper.db'
DB_NAME = 'prompts_database.db'
DB_TABLE_PROMPTS_NAME = 'table_prompts'


# logging.basicConfig(filename='log.txt', level=logging.DEBUG,
#                   format="%(asctime)s %(message)s",filemode="w")

# Функция для подготовки базы данных
# Создает/подключается к БД

# Функция для выполнения любого sql-запроса для получения данных (возвращает значения)
def execute_selection_query(sql_query, data=None, db_path=f'{DB_NAME}'):
    try:
        logging.info(f"DATABASE: Execute query: {sql_query}")

        connection = sqlite3.connect(db_path)
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



'''
# Функция для выполнения любого sql-запроса для получения данных (возвращает значение)
def execute_selection_query(sql_query, data = None, db_path=f'{DB_DIR}/{DB_NAME}'):
    try:
        logging.info(f"DATABASE: Execute query: {sql_query}")

        with sqlite3.connect(db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            if data:
                cursor.execute(sql_query, data)
            else:
                cursor.execute(sql_query)
            rows = cursor.fetchall()
        return rows
    except Exception as e:
        logging.error(f"DATABASE ERROR: {e}")
'''

# Функция для создания новой таблицы (если такой еще нет)
# Получает название и список колонок в формате ИМЯ: ТИП
# СОздает запрос CREATE TABLE IF NOT EXISTS имя_таблицы (колонка1 ТИП, колонка2 ТИП)
'''
def create_table(table_name, table_columns):
    sql_query = f'CREATE TABLE IF NOT EXISTS {table_name} '
    sql_query += '('

    cols = []
    for name, type in table_columns.items():
        cols.append(f'{name} {type}')
    sql_query += ', '.join(cols) + ')'

    execute_query(sql_query)
'''
# Функция для создания новой таблицы (если такой еще нет)
# Получает название и список колонок в формате ИМЯ: ТИП
# Создает запрос CREATE TABLE IF NOT EXISTS имя_таблицы (колонка1 ТИП, колонка2 ТИП)
def create_table(table_name):
    sql_query = f'CREATE TABLE IF NOT EXISTS {table_name}' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INTEGER, ' \
                f'role TEXT, ' \
                f'content TEXT, ' \
                f'date DATETIME, ' \
                f'tokens INTEGER, ' \
                f'session_id INTEGER)'
    execute_query(DB_NAME, sql_query)
    logging.info(f"DATABASE: Output: Таблица {table_name} в БД {DB_NAME} успешно создана")
    print(table_name)

'''    
    create_table(DB_TABLE_PROMPTS_NAME,
                 table_columns={
                     "id": 'INTEGER PRIMARY KEY',
                     'user_id': "INTEGER",
                     'role': "TEXT",
                     'content': "TEXT",
                     'date': "DATETIME",
                     'tokens': "INTEGER",
                     'session_id': "INTEGER"
                 })
'''
# Функция для удаления всех записей из таблицы
# Создает запрос DELETE FROM имя_таблицы
def clean_table(table_name):
    execute_query(f'DELETE FROM {table_name}')



'''
# Функция для вставки новой строки в таблицу
# Принимает список значений для каждой колонки и название колонок
# Создает запрос INSERT INTO имя_таблицы (колонка1, колонка2) VALUES (?,?)[значение1, значение2]
def insert_row(values):
    columns = '(user_id, role, content, date, tokens, session_id)'
    sql_query = f"INSERT INTO {DB_TABLE_PROMPTS_NAME} {columns} VALUES (?,?,?,?,?,?)"
    execute_query(sql_query, values)
'''

# Функция для проверки, есть ли элемент в указанном столбце таблицы
# Создает запрос SELECT колонка FROM имя_таблицы WHERE колонка == значение LIMIT 1
def is_value_in_table(table_name, column_name, value):
    sql_query = f'SELECT {column_name} FROM {table_name} WHERE {column_name} = ? ORDER BY DATE DESC'
    rows = execute_selection_query(sql_query, [value])
    print(rows)
    return rows

# Функция для проверки, есть ли элемент в указанном столбце таблицы
# Создает запрос SELECT колонка FROM имя_таблицы WHERE колонка == значение LIMIT 1
def get_users_amount(table_name):
    sql_query = f'SELECT {'user_id'} FROM {table_name} WHERE {'user_id'} = ? ORDER BY DATE DESC'
    rows = execute_selection_query(sql_query)
    print(rows)
    if rows == None:
        rows = 0
    return rows
# Функция для вставки новой строки в таблицу
# Принимает список значений для каждой колонки и названия колонок
# Создает запрос INSERT INTO имя_таблицы (колонка1, колонка2)VALUES (?,?)[значение1, значение2]

def insert_row(table_name, values, columns=''):
    print(table_name, values, columns)
    if columns != '':
        columns = '(' + ', '.join(columns) + ')'
    sql_query = f"INSERT INTO {table_name} {columns}VALUES ({', '.join(['?'] * len(values))})"
    execute_query(sql_query, values)
    print(table_name, values, columns)

# Функция, записывающая историю запросов в таблицу
def add_record_to_table(user_id, role, content, date, tokens, session_id):
    print(user_id, role, content, date, tokens, session_id)
    execute_query(DB_NAME," INSERT INTO {DB_TABLE_PROMPTS_NAME} (user_id, role, content, date, tokens, session_id) "
               f"VALUES({user_id}, '{role}', '{content}', {date}, {tokens}, {session_id})")

# Получить диалог с пользователем для данного user_id и session_id
def get_dialogue_for_user(user_id, session_id):
    sql_query = f'SELECT {'user_id'} FROM {DB_TABLE_PROMPTS_NAME} WHERE {'user_id'} = ? AND {'session_id'} = ?'
    rows = execute_selection_query(sql_query)
    print(rows)
    return rows
'''    
# Функция, записывающая историю запросов в таблицу
def add_record_to_table(user_id, role, content, date, tokens, session_id):
    print(user_id, role, content, date, tokens, session_id)
    insert_row(DB_TABLE_PROMPTS_NAME,
               [user_id, role, content, date, tokens, session_id],
                ['user_id', 'role', 'content', 'date', 'tokens', 'session_id'])
'''
'''
def prepare_db(clean_if_exists=False):
    create_db()
    create_table(DB_TABLE_PROMPTS_NAME,
                 table_columns={
                     "id": 'INTEGER PRIMARY KEY',
                     'user_id': "INTEGER",
                     'role': "TEXT",
                     'content': "TEXT",
                     'date': "DATETIME",
                     'tokens': "INTEGER",
                     'session_id': "INTEGER"
                 })
    # Для дебага
    # if clean_if_exists:
    #    clean_table(DB_TABLE_PROMPTS_NAME)
'''

# Функция для получения последнего значения из таблицы пользователя
def get_value_from_table(value, user_id):
    sql_query = f'SELECT {value} FROM {DB_TABLE_PROMPTS_NAME} WHERE user_id =? ORDER BY DATE DESC'
    rows = execute_selection_query(sql_query, [user_id])
    print("rows", rows)
    print("rows[0]", rows[0])
    return rows[0]
# вот тут все --------------------
# Функция для подключения к базе данных или создание новой, если ее еще нет
def create_db(database_name=DB_NAME):
    db_path = f'{database_name}'
    connection = sqlite3.connect(db_path)
    connection.close()

    logging.info(f"DATABASE: Output: База данных {DB_NAME} path = {db_path} успешно создана")

# Функция для выполнения любого sql-запроса для изменения данных
def execute_query(db_file, query, data=None):

#    Функция для выполнения запроса к базе данных.
#    Принимает имя файла базы данных, SQL-запрос и опциональные данные для вставки

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

'''





# Функция для создания новой таблицы (если такой еще нет)
# Получает название и список колонок в формате ИМЯ: ТИП
# Создает запрос CREATE TABLE IF NOT EXISTS имя_таблицы (колонка1 ТИП, колонка2 ТИП)
def create_table(table_name):
    sql_query = f'CREATE TABLE IF NOT EXISTS {table_name}' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INTEGER, ' \
                f'genre TEXT, ' \
                f'hero TEXT, ' \
                f'setting TEXT, ' \
                f'role TEXT, ' \
                f'content TEXT, ' \
                f'date TEXT, ' \
                f'tokens INTEGER, ' \
                f'session_id INTEGER, ' \
                f'task TEXT, ' \
                f'answer TEXT, ' \
                f't_start INTEGER, ' \
                f'content TEXT, ' \
                f'whole_story TEXT)'

    execute_query(DB_NAME, sql_query)
    logging.info(f"DATABASE: Output: Таблица {table_name} в БД успешно создана")


# Функция для вывода всей таблицы (для проверки)
# Создает запрос SELECT * FROM имя_таблицы
def print_all_rows(table_name):
    rows = execute_selection_query(f'SELECT * FROM {table_name}')
    for row in rows:
        print(row)


# Функция для удаления всех записей из таблицы
# Создает запрос DELETE FROM имя_таблицы
def clean_table(table_name):
    execute_query(DB_NAME, f'DELETE FROM {table_name}')


# Функция для вставки новой строки в таблицу
# Принимает список значений для каждой колонки и название колонок
# Создает запрос INSERT INTO имя_таблицы (колонка1, колонка2) VALUES (?,?)[значение1, значение2]
def insert_row(values):
    columns = '(user_id, role, content, date, tokens, session_id)'
    sql_query = f"INSERT INTO {DB_TABLE_PROMPTS_NAME} {columns} VALUES (?,?,?,?,?,?)"
    execute_query(sql_query, values)


# Функция для проверки, есть ли элемент в указанном столбце таблицы
# Создает запрос SELECT колонка FROM имя_таблицы WHERE колонка == значение LIMIT 1
def is_value_in_table(table_name, column_name, value):
    sql_query = f'SELECT {column_name} FROM {table_name} WHERE {column_name} =?'
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


def prepare_db():
    create_db()
    create_table(TABLE_NAME)
    insert_test_data_in_table(TABLE_NAME)

def insert_test_data_in_table(table_name):
    insert_row(TABLE_NAME, [1, 10001, 'system_prompt', 'Ты - помощник для написания сценариев. Напиши историю про Ферзя', '2024-02-17 15:45:00', 8, 1])
    insert_row(TABLE_NAME, [2, 10001, 'user_prompt', 'Далеко на севере есть край под названием Эдилада,', '2024-02-17 15:46:00', 14, 1])
    insert_row(TABLE_NAME, [3, 10001, 'assistant_prompt', 'Что означает "Полная Луна"', '2024-02-17 15:46:15', 15, 1])

    insert_row(TABLE_NAME, [4, 10002, 'system_prompt', 'Ты - помощник для написания сценариев. Напиши историю про Валета', '2024-03-01 22:00:00', 9, 1])
    insert_row(TABLE_NAME, [5, 10002, 'user_prompt', 'Валериан Валет - личный защитник Короля,', '2024-03-01 22:00:30', 17, 1])
    insert_row(TABLE_NAME, [6, 10002, 'assistant_prompt', 'по долгу службы вынужденный сопровождать его во всех похождениях', '2024-03-01 22:00:35', 23, 1])
    insert_row(TABLE_NAME, [7, 10002, 'assistant_prompt', 'и не давать попадать в неприятности,', '2024-03-01 22:00:40', 31, 1])
    insert_row(TABLE_NAME, [8, 10002, 'assistant_prompt', 'хотя его собственная жажда приключений ничуть не меньше.', '2024-03-01 22:00:45', 36, 1])

    insert_row(TABLE_NAME, [9, 10001, 'system_prompt', 'Ты - помощник для написания сценариев. Напиши историю про Короля', '2024-03-05 12:23:00', 8, 2])
    insert_row(TABLE_NAME, [10, 10001, 'user_prompt', 'Однажды Король выглянул в окно и увидел в роще блуждающий огонёк.', '2024-03-05 12:23:20', 14, 2])
    insert_row(TABLE_NAME, [11, 10001, 'assistant_prompt', 'Он был непохож на обычные местерские огни.', '2024-03-05 12:24:00', 16, 2])

    insert_row(TABLE_NAME, [12, 10001, 'system_prompt', 'Ты - помощник для написания сценариев. Напиши историю про Жара', '2024-03-10 11:14:00', 8, 3])
    insert_row(TABLE_NAME, [13, 10001, 'user_prompt', 'В далёкой-далёкой стране жил-был маленький принц по имени Жар Мрамор.', '2024-03-10 11:40:00', 15, 3])
    insert_row(TABLE_NAME, [14, 10001, 'assistant_prompt', 'Он был рождён богиней весны и умел превращаться в золотую птицу.', '2024-03-10 11:41:00', 17, 3])

'''
