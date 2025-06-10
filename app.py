from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from Routes import Routes

app = Flask(__name__)
CORS(app)
api = Api(app)
Routes(api)


if(__name__ == '__main__'):
    app.run(debug=True, port=3900, host='0.0.0.0')