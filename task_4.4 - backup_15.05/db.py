import sqlite3

from config import MAX_USERS

TABLE_NAME = 'users'
DB_NAME = 'db.db'


def execute_query(query, data=None):
    cur, connection = get_cursor()
    if data:
        result = cur.execute(query, data).fetchall()
    else:
        result = cur.execute(query).fetchall()
    connection.commit()
    connection.close()
    return result


def get_cursor():
    connection = sqlite3.connect(DB_NAME)
    return connection.cursor(), connection


def create_db():
    cur, connection = get_cursor()
    connection.close()


def create_table():
    query = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME}
    (id INTEGER PRIMARY KEY, 
    user_id INTEGER, 
    role TEXT, 
    content TEXT,
    tokens INTEGER, 
    session_id INTEGER)
    '''
    execute_query(query)


def insert_row(values):
    query = f'''
    INSERT INTO {TABLE_NAME} 
    (user_id, role, content, tokens, session_id)
    VALUES (?, ?, ?, ?, ?)
    '''

    execute_query(query, values)


def select_user_rows(user_id):
    query = f'''
    SELECT *
    FROM {TABLE_NAME}
    WHERE user_id = '{user_id}'
    '''

    return execute_query(query)


def count_tokens_for_user_in_session(user_id, session_id):
    query = f'''
    SELECT SUM(tokens)
    FROM {TABLE_NAME}
    WHERE user_id = '{user_id}' AND session_id = '{session_id}'
    GROUP BY user_id
    '''

    return execute_query(query)[0][0]


def get_all_unique_messages_in_session(user_id, session_id):
    query = f'''
    SELECT DISTINCT role, content
    FROM {TABLE_NAME}
    WHERE user_id = '{user_id}' AND session_id = '{session_id}'
    ORDER BY session_id
    '''

    return execute_query(query)


def get_last_session(user_id):
    query = f'''
    SELECT session_id
    FROM {TABLE_NAME}
    WHERE user_id = '{user_id}'
    ORDER BY session_id DESC
    LIMIT 1
    '''
    result = execute_query(query)
    if not result:
        return 0
    return result[0][0]


def is_max_amount_of_users():
    query = f'''
    SELECT COUNT(DISTINCT user_id)
    FROM {TABLE_NAME}
    '''
    result = execute_query(query)
    if not result:
        return False
    return result[0][0] >= MAX_USERS


def is_user_in_db(user_id):
    query = f'''
    SELECT user_id
    FROM {TABLE_NAME}
    WHERE user_id = '{user_id}'
    '''
    result = execute_query(query)
    return bool(result)
