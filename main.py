import mysql.connector
from mysql.connector import Error

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kaviya2004',
    'database': 'Social_Media_Influencer_Game'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def voting_details(username, password):
    connection = get_db_connection()
    if connection is None:
        return None  # Return None if connection fails
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to check credentials against users table
        query = "SELECT * FROM votes_month1 where viral_trend_riding =='l1' "
        query="select * from votes_month1 where "
        cursor.execute(query, (username.lower(), password))
        
        user = cursor.fetchone()
        
        return user  # Return user details if found
    except Error as e:
        print(f"Error in query execution: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
