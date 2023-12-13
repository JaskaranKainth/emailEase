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
            host="your_mysql_host",
            user="your_mysql_user",
            password="your_mysql_password",
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


def show_table_contents(connection, table):
    if connection is not None:
        try:
            cursor = connection.cursor(dictionary=True)

            # Select all rows from the specified table
            cursor.execute(f"SELECT * FROM {table}")

            # Fetch all rows
            rows = cursor.fetchall()

            # Print the header
            print(f"Contents of the '{table}' table:")
            print("-" * 40)

            # Print each row
            for row in rows:
                print(row)

            print("-" * 40)

            # Close the cursor
            cursor.close()

        except Error as e:
            print(f"Error retrieving data: {str(e)}")

            show_table_contents(connection, 'users')

