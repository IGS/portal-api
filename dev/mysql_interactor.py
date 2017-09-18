#!/usr/bin/env python

import mysql.connector, hashlib
from conf import mysql_h_2,mysql_db_2,mysql_un_2,mysql_pw_2,secret_key,iv

config = {
    'user': mysql_un_2,
    'password': mysql_pw_2,
    'host': mysql_h_2,
    'database': mysql_db_2
}

##########################################################
# FUNCTIONS FOR MANAGING USER SESSIONS AND QUERY HISTORY #
##########################################################

# Establish a "session" node in the Neo4j DB to consider the user logged in. 
# Note that only TWO sessions will be allowed per user at a given time. 
def establish_session(username):

    cnx = mysql.connector.connect(**config) # open connection/cursor
    cursor = cnx.cursor(buffered=True)

    session_id = hashlib.sha256(username+str(time.time())).hexdigest()
    unique_session = True # loop until we get a unique session_id regardless of user
    while unique_session:
        try:
            session_id = hashlib.sha256(username+str(time.time())).hexdigest()
            add_session = "INSERT INTO sessions (session_key,username) VALUES (%s,%s)"
            cursor.execute(add_session,(session_id,username,))
            unique_session = False
        except mysql.connector.IntegrityError as err:
            print("Session key already existed, generating a new one. Error: {}".format(err))

    # Whether or not the user has logged in before, try add them
    add_user = "INSERT INTO user (username) VALUES (%s)"
    try:
        cursor.execute(add_user,(username,))
    except mysql.connector.IntegrityError:
        print("User already in the database.")

    # delete all but the two most recent sessions
    delete_old_sessions = ("DELETE FROM sessions WHERE session_id IN "
        "(SELECT * FROM "
            "(SELECT session_id from sessions WHERE username=%s "
            "ORDER BY timestamp DESC LIMIT 100000 OFFSET 2) "
        "AS id)")
    try:
        cursor.execute(delete_old_sessions,(username,))
    except mysql.connector.Error as err:
        print("Error while deleting past history: {}".format(err))

    cursor.close() # close connection/cursor
    cnx.close()

    return session_id

# If the user logs out, then disconnect deliberately here. The auto-loader
# should handle timeout disconnects.
def disconnect_session(session_id):

    cnx = mysql.connector.connect(**config) # open connection/cursor
    cursor = cnx.cursor()

    delete_session = "DELETE FROM sessions WHERE session_id=%s"
    try:
        cursor.execute(delete_session,(session_id,))
    except mysql.connector.Error as err:
        print("Error while logging out: {}".format(err))

    cursor.close() # close connection/cursor
    cnx.close()

    return