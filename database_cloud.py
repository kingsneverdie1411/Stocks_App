import mysql.connector
import os

# Function to store data in MySQL
def store_data_in_mysql(data, database_name, table_name,date):
    # Connect to MySQL server
    # connection = mysql.connector.connect(
    #     host='localhost',
    #     user='neil',
    #     password='neilhanda',
    #     database=database_name
    # )
    # connection = mysql.connector.connect(
    #         host='34.126.126.234',
    #         user='neil',
    #         password='neilhanda',
    #         database=database_name
    # )
    # Get the Cloud SQL instance connection name from the environment variable
    cloud_sql_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

    # Configure the database connection
    connection = mysql.connector.connect(
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host='/cloudsql/{}'.format(cloud_sql_connection_name),
        database=os.environ.get('DB_NAME'),
        unix_socket='/cloudsql/{}'.format(cloud_sql_connection_name)
    )

    # print(date)
    # Create a cursor
    # used for queries
    cursor = connection.cursor()
    
    # Check if data for the given date already exists in the database
    cursor.execute("SELECT 1 FROM stocks WHERE date=STR_TO_DATE(%s, '%d%m%y') LIMIT 1", (date,))
    exists = cursor.fetchone()

    if not exists:
        # Data for the given date does not exist, proceed with insertion
        for _, row in data.iterrows():
            cursor.execute(f"INSERT INTO {table_name} (code, name, open, high, low, close, prevclose, date) VALUES (%s, %s, %s, %s, %s, %s, %s, STR_TO_DATE(%s, '%d%m%y'))",
                        (row['SC_CODE'], row['SC_NAME'], row['OPEN'], row['HIGH'], row['LOW'], row['CLOSE'], row['PREVCLOSE'], date))
        
        # Commit the changes
        connection.commit()
        print(f"Data for date {date} inserted successfully.")
    else:
        print(f"Data for date {date} already exists in the database. Skipping insertion.")

    # Insert data into the table
    # for _, row in data.iterrows():
    #     # print(row['SC_CODE']);
    #     cursor.execute("SELECT 1 FROM stocks WHERE code=%s AND date=STR_TO_DATE(%s, '%d%m%y')", (row['SC_CODE'], date))
    #     exists = cursor.fetchone()
    #     if not exists:
    #         cursor.execute(f"INSERT INTO {table_name} (code, name, open, high, low, close,prevclose,date) VALUES (%s, %s, %s, %s, %s, %s,%s,STR_TO_DATE(%s, '%d%m%y'))",
    #                    (row['SC_CODE'], row['SC_NAME'], row['OPEN'], row['HIGH'], row['LOW'], row['CLOSE'],row['PREVCLOSE'],date))

    # Commit the changes
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()