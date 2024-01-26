from flask import Flask, jsonify, request
import mysql.connector

def setup_api(app: Flask,database_name: str, table_name: str):
    @app.route("/")
    def hello():
        return "Hello, this is your Flask API!"
  

    def get_database_connection():
        connection = mysql.connector.connect(
            host='localhost',
            user='neil',
            password='neilhanda',
            database=database_name
        )
        return connection

    # /top/10 works not /top10
    @app.route("/top/<count>", methods=["GET"])
    def get_top_10_stocks(count):
        try:
            count = int(count)
            if count <= 0:
                raise ValueError('Invalid parameter: count must be a positive integer')
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor(dictionary=True)

        # Fetch top 10 stocks from the database
        query=f"select * from {table_name} order by date desc, close desc limit {count};"
        cursor.execute(query)
        top_10_stocks = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Return the result as JSON
        return jsonify(top_10_stocks)
    
    # stocks?name=XYZ
    # changed to findstocks/
    @app.route('/findstocks/<string:name>', methods=['GET'])
    def get_stocks_by_name(name):
        # Get the query parameter 'name' from the request URL
        if not name:
            return jsonify({'error': 'Stock name cannot be empty'}), 400
        name=name.upper()
        print(name)
        # Query the database for stocks with the given name
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        print(name)
        query = "SELECT * FROM stocks WHERE name LIKE %s"
        cursor.execute(query, (f'%{name}%',))
        print(query)
        stocks = cursor.fetchall()

        cursor.close()
        connection.close()

        # Check if stocks were found
        if not stocks:
            return jsonify({'error': 'No stocks found'}), 404

        # Return the list of stocks in JSON format
        return jsonify(stocks)

    # Add a route to handle cases where the name is missing
    @app.route('/findstocks/', methods=['GET'])
    def handle_missing_name():
        return jsonify({'error': 'Stock name is required'}), 400

    @app.route('/stock_history/', methods=['GET'])
    def handle_missing_name2():
        return jsonify({'error': 'Stock code is required'}), 400

    # Why using stock code - shorter and easier unlike string matching. We need for particular stock only.
    @app.route('/stock_history/<string:stock_code>', methods=['GET'])
    def get_stock_price_history(stock_code):
        # Validate the stock_code parameter
        if not stock_code:
            return jsonify({'error': 'Missing parameter: stock_code'}), 400

        # Query the database for historical stock price data
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        # ordering by date 
        query = "SELECT date, close FROM stocks WHERE code = %s ORDER BY date"
        cursor.execute(query, (stock_code,))

        stock_history = cursor.fetchall()

        cursor.close()
        connection.close()

        # Check if stock history was found
        if not stock_history:
            return jsonify({'error': 'No history found for the specified stock code'}), 404

        # Return the stock history in JSON format
        return jsonify(stock_history)

        # ... Other imports and setup ...

    # Why using stock code - shorter and easier unlike string matching. We need for particular stock only.
    # STILL WILL PROVIDE FOR NAME, if only 1 matches then do it 
    @app.route('/add_to_favourites/', methods=['POST'])
    def add_to_favorites():
        try:
            # Get the JSON data from the request
            data = request.json
            # print(data['code'.])
    
            
            # Validate required fields
            if 'code' not in data:
                return jsonify({'error': 'Missing required field: code'}), 400
            
            
            # Extract values from the JSON data
            code = data['code']
            
        #     # Connect to the database
            connection = get_database_connection()

        #     # Create a cursor
            cursor = connection.cursor(buffered=True)

        #     # Check if the stock exists in the stocks table
            cursor.execute("SELECT name FROM stocks WHERE code = %s", (code,))
            stock_name = cursor.fetchone()
        
            if not stock_name:
                return jsonify({'error': 'Stock with given code not found in stocks table'}), 404
           
            # return "adddf"
        #     # Check if the stock is already in favorites
            cursor.execute("SELECT * FROM favourites WHERE code = %s", (code,))
            exists = cursor.fetchone()
    
            if exists:
                return jsonify({'error': 'Stock is already in favorites'}), 400
            
            
            # Add the stock to favorites
            # print(code)
            # print(stock_name[0])
            cursor.execute("INSERT INTO favourites (code, name) VALUES (%s, %s)", (code, stock_name[0]))
        #     # Commit the changes
            connection.commit()

        #     # Close the cursor and connection
            cursor.close()
            connection.close()

            return jsonify({'message': 'Stock added to favorites successfully'}), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Get favourite stocks
    @app.route('/get_favourites', methods=['GET'])
    def get_favorites():
        try:
            # Connect to the database
            connection = get_database_connection()

            # Create a cursor
            cursor = connection.cursor(dictionary=True)

            # Fetch favorite stocks from the database
            query = "SELECT * FROM favourites"
            cursor.execute(query)
            favourite_stocks = cursor.fetchall()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            # Check if favorite stocks were found
            if not favourite_stocks:
                return jsonify({'message': 'No favourite stocks found'}), 404

            # Return the list of favorite stocks in JSON format
            return jsonify(favourite_stocks)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        # Add this route to api.py
    @app.route('/remove_from_favourites/<string:code>', methods=['GET', 'DELETE'])
    def remove_from_favourites(code):
        if not code:
            return jsonify({'error': 'Missing parameter: code'}), 400

        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM favourites WHERE code = %s", (code,))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Stock (IF EXISTED) removed from favourites successfully'}), 200
    
    @app.route('/remove_from_favourites/', methods=['GET'])
    def handle_missing_name3():
        return jsonify({'error': 'Stock code is required'}), 400