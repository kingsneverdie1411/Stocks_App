from flask import Flask, render_template
from api2 import setup_api
from flask_caching import Cache

app = Flask(__name__)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Initialize the API, setup_api will be defined in api.py
setup_api(app,"Stocks","stocks")

if __name__ == "__main__":
    app.run(debug=True)
