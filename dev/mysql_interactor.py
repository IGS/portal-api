#!/usr/bin/env python

import mysql.connector, hashlib, time
from datetime import datetime,timedelta
from conf import mysql_h_2,mysql_db_2,mysql_un_2,mysql_pw_2,secret_key

config = {
    'user': mysql_un_2,
    'password': mysql_pw_2,
    'host': mysql_h_2,
    'database': mysql_db_2
}

##########################################################
***REMOVED***FUNCTIONS FOR MANAGING USER SESSIONS AND QUERY HISTORY #
##########################################################

***REMOVED***Establish a "session" node in the Neo4j DB to consider the user logged in. 
***REMOVED***Note that only TWO sessions will be allowed per user at a given time. 
def establish_session(username):

    ***REMOVED***MySQL statements
    get_user_id = "SELECT id FROM user WHERE username=%s"
    add_user = "INSERT INTO user (username) VALUES (%s)"
    get_session_id = "SELECT session_id FROM sessions WHERE session_key=%s"
    add_session = "INSERT INTO sessions (user_id,session_key) VALUES (%s,%s)"
    delete_old_sessions = ("DELETE FROM sessions WHERE session_id IN "
        "(SELECT * FROM "
            "(SELECT session_id from sessions WHERE username=%s "
            "ORDER BY timestamp DESC LIMIT 100000 OFFSET 2) "
        "AS id)") ***REMOVED***delete all but the two most recent sessions

    cnx = mysql.connector.connect(**config) ***REMOVED***open connection/cursor
    cnx.autocommit = True
    cursor = cnx.cursor(buffered=True)

    cursor.execute(get_user_id,(username,))
    user_id = cursor.fetchone()

    if not user_id:
        cursor.execute(insert_user,(username,))
        cursor.execute(get_user_id,(username,))
        user_id = cursor.fetchone()[0]
    else:
        user_id = user_id[0]

    session_key = hashlib.sha256(username+str(time.time())).hexdigest()
    unique_session = True ***REMOVED***loop until we get a unique session_id regardless of user
    while unique_session:
        cursor.execute(get_session_id,(session_key,))
        session_id = cursor.fetchone()
        if not session_id:
            cursor.execute(add_session,(user_id,session_key))
            unique_session = False
        else:
            session_key = hashlib.sha256(username+str(time.time())).hexdigest()    

    try:
        cursor.execute(delete_old_sessions,(username,))
    except mysql.connector.Error as err:
        print("Error while deleting past history: {}".format(err))

    cursor.close() ***REMOVED***close cursor/connection
    cnx.close()

    return session_id

***REMOVED***If the user logs out, then disconnect deliberately here. The auto-loader
***REMOVED***should handle timeout disconnects.
def disconnect_session(session_id):

    cnx = mysql.connector.connect(**config) ***REMOVED***open connection/cursor
    cursor = cnx.cursor()

    delete_session = "DELETE FROM sessions WHERE session_id=%s"
    try:
        cursor.execute(delete_session,(session_id,))
    except mysql.connector.Error as err:
        print("Error while logging out: {}".format(err))

    cursor.close() ***REMOVED***close connection/cursor
    cnx.close()

    return

***REMOVED***Given a session ID and see if it checks out with what was set in the cookies
def get_user_info(session_id):

    cnx = mysql.connector.connect(**config) ***REMOVED***open connection/cursor
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

                ***REMOVED***check if any history is present
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

    cursor.close() ***REMOVED***close connection/cursor
    cnx.close()

    return user_info

def pull_data(table):

    cnx = mysql.connector.connect(**config) ***REMOVED***open connection/cursor
    cursor = cnx.cursor()
    pull_user_info = "SELECT * FROM "
    pull_user_info += table
    cursor.execute(pull_user_info)
    row = cursor.fetchone()
    while row is not None:
        print(row)
        row = cursor.fetchone()
    cursor.close() ***REMOVED***close connection/cursor
    cnx.close()

def reset_db():

    cnx = mysql.connector.connect(**config) ***REMOVED***open connection/cursor
    cursor = cnx.cursor()
    tables = ['sessions','user','query']
    for table in tables:
        cursor.execute("TRUNCATE TABLE {}".format(table))
    cursor.close() ***REMOVED***close connection/cursor
    cnx.close()
