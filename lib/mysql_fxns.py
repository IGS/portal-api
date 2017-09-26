#!/usr/bin/env python

import mysql.connector, hashlib, time
from datetime import datetime,timedelta
from conf import mysql_h,mysql_db,mysql_un,mysql_pw
from conf import mysql_h_2,mysql_db_2,mysql_un_2,mysql_pw_2

##########################################
# FUNCTIONS FOR BASE MySQL FUNCTIONALITY #
##########################################

def connect_mysql(user,password,host,database):

    config = {
        'user': user,
        'password': password,
        'host': host,
        'database': database
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
        'add_saved_query_sample_data': (
            "INSERT INTO query (user_id,query,query_url,sample_count,comment,file_count) "
            "VALUES (%s,%s,%s,%s,%s,%s)"
        ),
        'add_session': "INSERT INTO sessions (user_id,session_key) VALUES (%s,%s)",
        'add_user': "INSERT INTO user (username) VALUES (%s)",
        'delete_old_sessions': (
            "DELETE FROM sessions WHERE session_id IN "
            "(SELECT * FROM "
                "(SELECT session_id from sessions WHERE user_id=%s "
                "ORDER BY timestamp DESC LIMIT 100000 OFFSET 2) "
            "AS id)"         
        ),
        'delete_session': "DELETE FROM sessions WHERE session_key=%s",
        'get_saved_queries': (
            "SELECT query, query_url, sample_count, "
            "file_count, comment, timestamp "
            "FROM query WHERE user_id=%s"
        ),
        'get_session_id': "SELECT session_id FROM sessions WHERE session_key=%s",
        'get_single_saved_query': (
            "SELECT sample_count "
            "FROM query WHERE query=%s AND user_id=%s"
        ),
        'get_user_id': "SELECT id FROM user WHERE username=%s",
        'get_user_id_from_session_key': "SELECT user_id FROM sessions WHERE session_key=%s",
        'get_username_from_session_key': (
            "SELECT username FROM user,sessions "
            "WHERE user.id=sessions.user_id "
            "AND sessions.session_key=%s"
        ),
        'login': "SELECT password FROM hmp_portal WHERE username=%s",
        'update_saved_query_comment_data': (
            "UPDATE query SET comment=%s, timestamp=timestamp "
            "WHERE user_id=%s AND query=%s"
        ),
        'update_saved_query_file_data': (
            "UPDATE query SET file_count=%s "
            "WHERE user_id=%s AND query_url=%s"
        ),
        'update_saved_query_sample_data': (
            "UPDATE query SET sample_count=%s "
            "WHERE user_id=%s AND query=%s"
        )
    }

    try:
        cursor.execute(all_statements[statement],values)
    except mysql.connector.Error as err:
        print("Error during {}: {}".format(statement,err))
        return 'error'

########################################
# FUNCTIONS FOR LOGGING IN / SESSIONS #
########################################

def login(username):

    cnx,cursor = connect_mysql(mysql_un,mysql_pw,mysql_h,mysql_db)
    if cursor:
        execute_mysql(cursor,'login',(username,))

        pw = cursor.fetchone()

        if pw:
            pw = str(pw[0]) # convert from tuple/unicode to plain string if we got a record

        disconnect_mysql(cnx,cursor)

        return pw

def establish_session(username):

    cnx,cursor = connect_mysql(mysql_un_2,mysql_pw_2,mysql_h_2,mysql_db_2)
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
        return session_key

def disconnect_session(session_key):

    cnx,cursor = connect_mysql(mysql_un_2,mysql_pw_2,mysql_h_2,mysql_db_2)
    if cursor:
        execute_mysql(cursor,'delete_session',(session_key,))

        disconnect_mysql(cnx,cursor)
        return

###############################
# FUNCTIONS FOR QUERY HISTORY #
################################

def save_query_comment_data(session_key,query,comment):

    cnx,cursor = connect_mysql(mysql_un_2,mysql_pw_2,mysql_h_2,mysql_db_2)
    if cursor:

        execute_mysql(cursor,'get_user_id_from_session_key',(session_key,))
        user_id = cursor.fetchone()   

        if user_id: # rare case where a session has expired
            user_id = user_id[0]
        else:
            return

        res = execute_mysql(cursor,
            'update_saved_query_comment_data',
                (comment,
                user_id,
                query
                )
        )

        disconnect_mysql(cnx,cursor)
        return

def save_query_sample_data(session_key,reference_url,query,sample_count):

    cnx,cursor = connect_mysql(mysql_un_2,mysql_pw_2,mysql_h_2,mysql_db_2)
    if cursor:

        execute_mysql(cursor,'get_user_id_from_session_key',(session_key,))
        user_id = cursor.fetchone()   

        if user_id: # rare case where a session has expired
            user_id = user_id[0]
        else:
            return

        # if this query is already saved, only update sample count
        execute_mysql(cursor,'get_single_saved_query',(query,user_id))
        existing_query = cursor.fetchone()

        if existing_query: 
            execute_mysql(cursor,'update_saved_query_sample_data',(sample_count,user_id,query))

        else:
            # note dummy values for comment/file_count
            execute_mysql(cursor,
                'add_saved_query_sample_data',
                    (user_id,
                    query,
                    reference_url.replace('save=yes',''),
                    sample_count,
                    '',
                    0
                    )
            )

        disconnect_mysql(cnx,cursor)
        return

def save_query_file_data(session_key,reference_url,file_count):

    cnx,cursor = connect_mysql(mysql_un_2,mysql_pw_2,mysql_h_2,mysql_db_2)
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
                'update_saved_query_file_data',
                    (file_count,
                    user_id,
                    reference_url.replace('save=yes','')
                    )
            )

            if res != 'error':
                break

        disconnect_mysql(cnx,cursor)
        return

def get_user_info(session_key):

    cnx,cursor = connect_mysql(mysql_un_2,mysql_pw_2,mysql_h_2,mysql_db_2)
    if cursor:

        execute_mysql(cursor,'get_username_from_session_key',(session_key,))
        username = cursor.fetchone()   

        if username: # rare case where a session has expired
            username = username[0]
        else:
            return

        user_info = {
            'username':str(username),
            'queries':[],
            'hrefs':[],
            'scounts':[],
            'fcounts':[],
            'comments':[],
            'timestamps':[]
        }

        execute_mysql(cursor,'get_user_id_from_session_key',(session_key,))
        user_id = cursor.fetchone()   

        if user_id: # rare case where a session has expired
            user_id = user_id[0]
        else:
            return

        execute_mysql(cursor,'get_saved_queries',(user_id,))

        for (query,href,scount,fcount,comment,timestamp) in cursor:

                # check if any history is present
                user_info['queries'].append(str(query))
                user_info['hrefs'].append(str(href))
                user_info['scounts'].append(scount)
                user_info['fcounts'].append(fcount)
                user_info['comments'].append(str(comment))
                user_info['timestamps'].append("{} days ago".format((datetime.today()-timestamp).days))

        disconnect_mysql(cnx,cursor)

        if user_info['username']:
            return user_info
            