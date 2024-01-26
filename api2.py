from flask import Flask, jsonify, request, render_template, redirect, url_for
import mysql.connector
from flask_caching import Cache
# from flask_cache_stats import Cache, CacheStats
import subprocess
import os

def setup_api(app: Flask,database_name: str, table_name: str):
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    @app.route("/")
    def home():
        return render_template('home.html')

    def get_database_connection():
        connection = mysql.connector.connect(
            host='localhost',
            user='neil',
            password='neilhanda',
            database=database_name
        )
        # connection = mysql.connector.connect(
        #     host='34.126.126.234',
        #     user='neil',
        #     password='neilhanda',
        #     database=database_name
        # )
        # Get the Cloud SQL instance connection name from the environment variable
        # cloud_sql_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

        # # Configure the database connection
        # connection = mysql.connector.connect(
        #     user=os.environ.get('DB_USER'),
        #     password=os.environ.get('DB_PASSWORD'),
        #     host='/cloudsql/{}'.format(cloud_sql_connection_name),
        #     database=os.environ.get('DB_NAME'),
        #     unix_socket='/cloudsql/{}'.format(cloud_sql_connection_name)
        # )
        

        
        return connection

    @app.route('/check_top_stocks/', methods=['GET'])
    def topstocks():
        return render_template('topstocks.html')
    
    # /top/10 works not /top10
    # ISSUE WITH FORM- only parameter is passed
    @app.route("/top", methods=["GET"])
    @cache.cached(timeout=60,key_prefix=lambda:request.full_path)
    def get_top_10_stocks():
        # Getting paramter from URL     
        count = request.args.get('count')
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
    
    @app.route('/find_stocks/', methods=['GET'])
    def findstocks():
        return render_template('findstocks.html')
    
    # stocks?name=XYZ
    # changed to findstocks/
    @app.route('/findstocks', methods=['GET'])
    @cache.cached(timeout=60,key_prefix=lambda:request.full_path)
    def get_stocks_by_name():
        # Get the query parameter 'name' from the request URL
        # Now get from FORM 
        name=request.args.get('name')
        print(name)
        if not name:
            return jsonify({'error': 'Stock name cannot be empty'}), 400
        name=name.upper()
        print(name)
        # Query the database for stocks with the given name
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        print(name)
        # query = "SELECT * FROM stocks WHERE name LIKE %s ORDER BY DATE DESC"
        ## UPDATED QUERY 
        query="SELECT s1.* FROM stocks s1 LEFT JOIN stocks s2 ON s1.name = s2.name AND s1.date < s2.date WHERE s2.date IS NULL AND s1.name LIKE %s ORDER BY s1.date DESC;"
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
    # NO NEED NOW AFTER FORM 
    # @app.route('/findstocks/', methods=['GET'])
    # def handle_missing_name():
    #     return jsonify({'error': 'Stock name is required'}), 400

    @app.route('/get_stock_history/', methods=['GET'])
    def get_stock_history():
        return render_template('stockhistory.html')

    # Why using stock code - shorter and easier unlike string matching. We need for particular stock only.
    @app.route('/stock_history', methods=['GET'])
    @cache.cached(timeout=60,key_prefix=lambda:request.full_path)
    def get_stock_price_history():
        # Validate the stock_code parameter
        stock_code=request.args.get('stock_code')

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
    @app.route('/add_to_favourites/', methods=['POST','GET'])
    def add_to_favorites():
        if request.method == 'GET':
            return render_template('addfav.html')
        try:
            # Get the JSON data from the request
            print(request)
            if request.is_json:
                # Handle JSON data
                data = request.json
                # Validate required fields
                if 'code' not in data:
                    return jsonify({'error': 'Missing required field: code'}), 400
            else:
                # Handle form data
                data = request.form
                # Validate required fields
                if 'code' not in data:
                    return jsonify({'error': 'Missing required field: code'}), 400
          
            
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

            # return jsonify({'message': 'Stock added to favorites successfully'}), 201
            print("Stock added to favorites successfully")
            return redirect(url_for('get_favourites'))
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Get favourite stocks
    @app.route('/get_favourites', methods=['GET'])
    def get_favourites():
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
    @app.route('/remove_from_favourites/<string:code>', methods=['DELETE','GET'])
    def remove_from_favourites(code):
        try:
            print(code)
            if not code:
                return jsonify({'error': 'Missing parameter: code'}), 400

            connection = get_database_connection()
            cursor = connection.cursor()
            # Check if the stock exists in favorites
            cursor.execute("SELECT 1 FROM favourites WHERE code = %s", (code,))
            exists = cursor.fetchone()
            if not exists:
                return jsonify({'error': 'Stock not found in favorites'}), 404
            
            # If exists then delete and redirect
            cursor.execute("DELETE FROM favourites WHERE code = %s", (code,))

            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({'message': 'Stock (IF EXISTED) removed from favourites successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/remove_from_favourites/', methods=['GET'])
    def take_input():
        return render_template('remfav.html')
        return jsonify({'error': 'Stock code is required'}), 400
    
    @app.route('/update_data', methods=['GET'])
    def update_data():
        try:
            # Run the data_processing.py script with choice 1
            # subprocess.run(['python3', 'data_processing.py','1'], check=True)
            subprocess.run(['python3', 'data_processing.py','1'], check=True)
            # testing on cloud only for latest data
            return jsonify({'message': 'Data updated successfully'}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Error running script: {e}'}, 500)
