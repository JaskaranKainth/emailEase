import mysql.connector
from mysql.connector import Error

"""
    Function: create_connection()
    Desctiption: Create a connection to the MySQL database.
    Parameters: none
    Returns: connection: MySQL database connection object.
            None if there is an error in establishing the connection.
   """
def create_connection():  
    try:
        connection = mysql.connector.connect(
            host="DESKTOP-44F320G",
            port=3306,
            user="emailease",
            password="Password!",
            database="email_database"
        )
        return connection
    except Error as e:
        print(f"Error connecting to the database: {str(e)}")
        return None
    
"""
    Function: create_tables(connection)
    Description: Create database tables if they do not exist.
    Parameters: connection: MySQL database connection object.
    Returns: none
    """
def create_tables(connection):
    
    if connection is not None:
        try:
            #create a cursor
            cursor = connection.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email_address VARCHAR(255) NOT NULL
                )
            """)

            # Folders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    folder_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    user_id INT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Emails table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    email_id INT AUTO_INCREMENT PRIMARY KEY,
                    subject VARCHAR(255) NOT NULL,
                    content TEXT,
                    sender VARCHAR(255) NOT NULL,
                    timestamp DATETIME NOT NULL,
                    folder_id INT,
                    FOREIGN KEY (folder_id) REFERENCES folders(folder_id)
                )
            """)

            #commit changes to database
            connection.commit()

            #close cursor
            cursor.close()
        except Error as e:
            print(f"Error creating tables: {str(e)}")

"""
    Function: insert_data(connection, table, data)
    Description: Insert data into the specified table.
    Parameters:
        connection: MySQL database connection object.
        table (str): Name of the table.
        data (dict): Data to be inserted into the table.
    Returns: none
    """
def insert_data(connection, table, data):
    
    if connection is not None:
        try:
            #create cursor
            cursor = connection.cursor()

            #construct sql query w/ placeholders for values
            placeholders = ', '.join(['%s'] * len(data))
            columns = ', '.join(data.keys())
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            #exec query with data 
            cursor.execute(query, list(data.values()))

            #commit changes to database
            connection.commit()

            #close
            cursor.close()
        except Error as e:
            print(f"Error inserting data: {str(e)}")

def fetch_user(connection, username):
    """
    Function: fetch_user(connection, username)
    Description: Fetch user information from the 'users' table based on the username.
    Parameters:
        connection: MySQL database connection object.
        username (str): Username of the user to fetch.
    Returns: user_data (dict): User information as a dictionary if found, None otherwise.
    """
    if connection is not None:
        try:
            # Create a cursor
            cursor = connection.cursor(dictionary=True)

            # Construct SQL query to select user by username
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))

            # Fetch the user data
            user_data = cursor.fetchone()

            # Close the cursor
            cursor.close()

            return user_data

        except Error as e:
            print(f"Error fetching user data: {str(e)}")
            return None
        
def wipe_table(connection, table_name):
    if connection is not None:
        try:
            cursor = connection.cursor()

            # Delete all rows from the table
            cursor.execute(f"DELETE FROM {table_name}")

            # Commit the changes
            connection.commit()

            print(f"All rows deleted from {table_name}.")

            cursor.close()
        except Error as e:
            print(f"Error wiping table: {str(e)}")
