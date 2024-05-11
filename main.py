from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/",)
def index():
    return jsonify(
        {
            "message":'Welcome to Salama Mama',
        }
    ), 200


if __name__ == "__main__":
    app.run(debug=True)