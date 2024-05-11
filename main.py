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

    motivational_qoutes = f"Given the user's current emotion of '{mood}', their preferences {preferences}, the desired response tone {tone}, and the current domain is '{domain}', generate a JSON object containing five motivational messages. The JSON should have a key named 'messages' where the value is an array of message objects. Each object should include keys for 'message' and 'additional_info', with the 'message' key containing the motivational text crafted to uplift the user, align with their preferences, and be delivered in the specified tone."

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

@app.route("/feed", methods=['POST'])
def feed():
    # Constants
    domain = 'post partum depression'
    mood = str(request.form['mood'].lower())
    preferences = ['simple language']  # TODO: Scaffold in frontend

    # Crafting the AI prompt
    content = f"Given the user's current mood, which is '{mood}', and their preferences that include {preferences}, generate a detailed JSON object containing personalized content for their feed. This JSON should have three main keys: 'activities', 'articles', and 'informative_material', each containing at least three items. Each item in these categories should include keys for 'title', 'description', 'detailed_info', 'image_url', and 'benefit'. The content should be tailored to uplift, educate, and positively influence the user's emotional state in the context of {domain}. Include relevant images for each content type to enhance visual engagement and ensure all information is practical, supportive, and aligns with the latest research on postpartum care."

    # Sending the message to the AI model
    response = normal_model.generate_content(content)

    
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

@app.route("/generate_story", methods=['POST'])
def generate_story():
    # Check if required data is present
    if 'mood' not in request.form or 'preferences' not in request.form:
        return jsonify({'error': 'Missing required parameters: mood and preferences'}), 400

    # Extract mood and preferences from the form
    mood = request.form['mood']
    preferences = request.form['preferences']

    # Generate the prompt for the story
    prompt = f"Given the user's current mood, which is '{mood}', and their specific preferences, which include {preferences}, generate a detailed and engaging story. This story should be tailored specifically for a user dealing with postpartum depression. It should include practical coping mechanisms, motivational messages that inspire hope and strength, and accurate educational information about postpartum depression. The story should help the user feel understood and supported, and encourage positive emotional engagement."

    response = normal_model.generate_content(prompt)

    # Return the generated story in a JSON response
    return jsonify({'story': response.text}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)