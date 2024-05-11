from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
import os

from helpers import extract_json, get_chat_model, get_normal_model, text_to_speech

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

@app.route("/chat/response", methods=['POST'])
def chat_response():
    # Constants
    tone = ['joyful', 'hopeful']
    domain = 'post partum depression'
    mood = str(request.form['mood'].lower())
    preferences = ['simple language']  # TODO: Scaffold in frontend
    chat_text = str(request.form['chat-text'].lower())

    # Crafting the AI prompt
    tone_of_ai = f"Given the user's current emotion of {mood}, their preferences {preferences}, the desired response tone {tone}, and the ongoing conversation context: '{chat_text}' within the {domain} domain, generate a json containing keys for 'response', 'emotion_addressed', 'tone_used', and 'additional_info'. The values should provide a supportive and insightful message in the specified tone, detail the emotion being addressed, the tone used, and include any other relevant user interaction data."

    # Sending the message to the AI model
    response = chat_model.send_message(tone_of_ai)

    
    # Assuming 'extract_json' is a function you've defined to parse the AI's response
    return extract_json(response.text), 200

@app.route("/speech", methods=['POST'])
def speech():
    # Check if 'text' key exists in form data
    if 'text' not in request.form:
        return jsonify({'error': 'Missing text parameter'}), 400

    # Safely extract and process text input
    text = request.form['text'].strip().lower()
    if not text:
        return jsonify({'error': 'Text parameter is empty'}), 400

    try:
        # Assuming text_to_speech is a function that returns the filename of the generated speech file
        speech_file = 'speech_files/'+text_to_speech(text=text)

        print(speech_file)
        if not speech_file:
            return jsonify({'error': 'Failed to generate speech'}), 500

        # Construct the full URL to access the generated speech file
        speech_url = url_for('static', filename=speech_file, _external=True)

        # Return the URL to the speech file in a JSON response
        return jsonify({'speech_url': speech_url}), 200

    except Exception as e:
        # Log the exception or handle it as appropriate
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)