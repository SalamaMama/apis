from flask import Flask, jsonify, request
from flask_cors import CORS

from helpers import extract_json, get_chat_model, get_normal_model, to_markdown

app = Flask(__name__)
CORS(app)

chat_model = get_chat_model()
normal_model = get_normal_model()

@app.route("/",)
def index():
    return jsonify(
        {
            "message":'Welcome to Salama Mama',
        }
    ), 200

@app.route("/gen/motivation", methods=['POST'])
def gen_motivation():
    # Motivational quotes

    tone = ['joyful','hopeful']
    domain = 'post partum depression'
    mood = str(request.form['mood'].lower())
    preferences = ['simple language'] # TODO: Scaffold in frontend

    motivational_qoutes = f"Given the user's current emotion of {mood}, their preferences {preferences}, the desired response tone {tone} and the current domain is {domain} generate a json containing five motivational messages. Each message should be crafted to uplift the user, align with their preferences, and be delivered in the specified tone"


    response = normal_model.generate_content(motivational_qoutes)
    
    return extract_json(response.text), 200


if __name__ == "__main__":
    app.run(debug=True)