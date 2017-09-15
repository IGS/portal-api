#!/usr/bin/env python

from Crypto.Cipher import AES
from Crypto import Random
import mysql.connector, hashlib
import base64
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

def encode(message):
    obj = AES.new(secret_key, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))

def decode(cipher):
    obj = AES.new(secret_key, AES.MODE_CFB, iv)
    return obj.decrypt(base64.urlsafe_b64decode(cipher))


# Establish a "session" node in the Neo4j DB to consider the user logged in. 
# Note that only TWO sessions will be allowed per user at a given time. 
def establish_session(username):

    cnx = mysql.connector.connect(**config) # open connection/cursor
    cursor = cnx.cursor(buffered=True)

    add_user = "INSERT IGNORE INTO user (username) VALUES (%s)"
    cursor.execute(add_user,(username,))

    add_session = "INSERT INTO sessions (username) VALUES (%s)"
    cursor.execute(add_session,(username,))

    cursor.execute("SELECT LAST_INSERT_ID()")
    cnx.commit()

    session_id = encode(str(cursor.fetchone()[0]))

    # delete all but the two most recent sessions

    delete_old_sessions = ("DELETE FROM sessions WHERE session_id IN "
        "(SELECT * FROM "
            "(SELECT session_id from sessions WHERE username=%s "
            "ORDER BY timestamp DESC LIMIT 100000 OFFSET 2) "
        "AS id)")

    cursor.execute(delete_old_sessions,(username,))
    
    cnx.commit()
    cursor.close() # close connection/cursor
    cnx.close()

    return session_id

# If the user logs out, then disconnect deliberately here. The auto-loader
# should handle timeout disconnects.
def disconnect_session(session_id):

    cnx = mysql.connector.connect(**config) # open connection/cursor
    cursor = cnx.cursor()

    delete_session = "DELETE FROM sessions WHERE session_id=%s"
    cursor.execute(delete_session,(decode(session_id),)

    cnx.commit()
    cursor.close() # close connection/cursor
    cnx.close()

    return
