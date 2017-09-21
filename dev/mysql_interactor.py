#!/usr/bin/env python

import mysql.connector, hashlib, time
from datetime import datetime,timedelta
from conf import mysql_h_2,mysql_db_2,mysql_un_2,mysql_pw_2,secret_key

##########################################################
# FUNCTIONS FOR MANAGING USER SESSIONS AND QUERY HISTORY #
##########################################################

def connect_mysql():

    config = {
        'user': mysql_un_2,
        'password': mysql_pw_2,
        'host': mysql_h_2,
        'database': mysql_db_2
    }

    try:
        cnx = mysql.connector.connect(**config) # open connection/cursor
        cnx.autocommit = True
        cursor = cnx.cursor(buffered=True)
        return cnx,cursor
    except mysql.connector.Error as err:
        print("Error while connecting to MySQL: {}".format(err))
        return None,None

def disconnect_mysql(connection,cursor):

    try:
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print("Error while disconnecting from MySQL: {}".format(err))

def execute_mysql(cursor,statement,values):

    all_statements = {
        'get_user_id': "SELECT id FROM user WHERE username=%s",
        'get_user_id_from_session_key': "SELECT user_id FROM sessions WHERE session_key=%s",
        'add_user': "INSERT INTO user (username) VALUES (%s)",
        'get_session_id': "SELECT session_id FROM sessions WHERE session_key=%s",
        'add_session': "INSERT INTO sessions (user_id,session_key) VALUES (%s,%s)",
        'delete_session': "DELETE FROM sessions WHERE session_key=%s",
        'delete_old_sessions': (
            "DELETE FROM sessions WHERE session_id IN "
            "(SELECT * FROM "
                "(SELECT session_id from sessions WHERE user_id=%s "
                "ORDER BY timestamp DESC LIMIT 100000 OFFSET 2) "
            "AS id)"         
        ),
        'add_saved_query_sample_data': (
            "INSERT INTO query (user_id,query,query_url,sample_count,comment,file_count) "
            "VALUES (%s,%s,%s,%s,%s,%s)"
        ),
        'add_saved_query_file_data': (
            "UPDATE query SET file_count=%s "
            "WHERE user_id=%s AND query_url=%s"
        )
    }

    try:
        cursor.execute(all_statements[statement],values)
    except mysql.connector.Error as err:
        print("Error during {}: {}".format(statement,err))
        return 'error'

def establish_session(username):

    cnx,cursor = connect_mysql()
    if cursor:
        execute_mysql(cursor,'get_user_id',(username,))
        user_id = cursor.fetchone()

        if not user_id:
            execute_mysql(cursor,'add_user',(username,))
            execute_mysql(cursor,'get_user_id',(username,))
            user_id = cursor.fetchone()[0]
        else:
            user_id = user_id[0]

        session_key = hashlib.sha256(username+str(time.time())).hexdigest()
        unique_session = True # loop until we get a unique session_id regardless of user
        while unique_session:
            execute_mysql(cursor,'get_session_id',(session_key,))
            session_id = cursor.fetchone()
            if not session_id:
                execute_mysql(cursor,'add_session',(user_id,session_key))
                unique_session = False
            else:
                session_key = hashlib.sha256(username+str(time.time())).hexdigest()    

        execute_mysql(cursor,'delete_old_sessions',(user_id,))

        disconnect_mysql(cnx,cursor)
        return session_id

def disconnect_session(session_key):

    cnx,cursor = connect_mysql()
    if cursor:
        execute_mysql(cursor,'delete_session',(session_key,))

        disconnect_mysql(cnx,cursor)
        return

def save_query_sample_data(session_key,reference_url,query,sample_count,comment,file_count):

    cnx,cursor = connect_mysql()
    if cursor:

        execute_mysql(cursor,'get_user_id_from_session_key',(session_key,))
        user_id = cursor.fetchone()   

        if user_id: # rare case where a session has expired
            user_id = user_id[0]
        else:
            return

        execute_mysql(cursor,
            'add_saved_query_sample_data',
                (user_id,
                query,
                reference_url.replace('save=yes',''),
                sample_count,
                comment,
                file_count
                )
        )

        disconnect_mysql(cnx,cursor)
        return

def save_query_file_data(session_key,reference_url,file_count):

    cnx,cursor = connect_mysql()
    if cursor:

        execute_mysql(cursor,'get_user_id_from_session_key',(session_key,))
        user_id = cursor.fetchone()   

        if user_id: # rare case where a session has expired
            user_id = user_id[0]
        else:
            return

        for attempt in range(10):

            time.sleep(1)

            res = execute_mysql(cursor,
                'add_saved_query_file_data',
                    (file_count,
                    user_id,
                    reference_url.replace('save=yes','')
                    )
            )

            if res != 'error':
                break

        disconnect_mysql(cnx,cursor)
        return

# Given a session ID and see if it checks out with what was set in the cookies
def get_user_info(session_id):

    cnx = mysql.connector.connect(**config) # open connection/cursor
    cursor = cnx.cursor()

    user_info = {
        'username':"",
        'queries':[],
        'hrefs':[],
        'scounts':[],
        'fcounts':[],
        'comments':[],
        'last_calc':[]
    }

    pull_user_info = "SELECT TIMESTAMP FROM sessions"
    try:

        cursor.execute(delete_session,(session_id,))
        for (username,query,href,scount,fcount,comment,timestamp) in cursor:

                # check if any history is present
                user_info['username'] = username
                user_info['queries'].append(query)
                user_info['hrefs'].append(href)
                user_info['scounts'].append(scount)
                user_info['fcounts'].append(fcount)
                user_info['comments'].append(comment)
                day_diff = (datetime.today() - timedelta(days=datetime.strptime(val, '%Y-%m-%d %H:%M:%S').day)).day
                user_info['last_calc'].append("{} days ago".format(day_diff))

    except mysql.connector.Error as err:
        print("Error while pulling user info: {}".format(err))

    cursor.close() # close connection/cursor
    cnx.close()

    return user_info

def pull_data(table):

    cnx = mysql.connector.connect(**config) # open connection/cursor
    cursor = cnx.cursor()
    pull_user_info = "SELECT * FROM "
    pull_user_info += table
    cursor.execute(pull_user_info)
    row = cursor.fetchone()
    while row is not None:
        print(row)
        row = cursor.fetchone()
    cursor.close() # close connection/cursor
    cnx.close()

def reset_db():

    cnx = mysql.connector.connect(**config) # open connection/cursor
    cursor = cnx.cursor()
    tables = ['sessions','user','query']
    for table in tables:
        cursor.execute("TRUNCATE TABLE {}".format(table))
    cursor.close() # close connection/cursor
    cnx.close()

save_query_file_data('93231ac17a71785642ff844b6853434e6a783e2395d7ac1cbba20f0832c333c4','ref_url',5678)