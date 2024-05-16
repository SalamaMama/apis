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
    tone_of_ai = f"""
    Given the user's current emotion of '{mood}', their preferences '{preferences}', the desired response tone '{tone}', and the ongoing conversation context: '{chat_text}' within the {domain} domain, generate a JSON object containing the following keys:

        1. response: A supportive and insightful message crafted in the specified tone that acknowledges both the user's current emotion and the ongoing conversation context. If there is a discrepancy between the user's stated mood ('{mood}') and the emotional tone of the chat context ('{chat_text}'), address the chat context first while gently guiding the user towards content that aligns with their stated mood.
        2. emotion_addressed: The specific emotion being addressed based on the chat context.
        3. tone_used: The tone used in the response, ensuring it matches the user's specified tone (e.g., comforting, encouraging, informative).
        4. additional_info: Any other relevant user interaction data or suggestions for further support.

    Ensure the response:

        Balances the user's mood and the context of the conversation.
        Validates the user's feelings expressed in the chat context and provides appropriate support or resources.
        Aligns with the user's preferences and desired tone.
        Is actionable, offering practical advice or steps where appropriate.
    """

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
    content = f"""
    Given the user's current mood, which is '{mood}', and their preferences that include {preferences}, generate a comprehensive JSON object containing personalized content for their feed. This JSON should have three main keys: 'activities', 'articles', and 'informative_material'. Each category should contain at least three items, with each item including the following keys:

        title: A concise and engaging title that captures the essence of the content.
        description: A brief summary that provides an overview of the content.
        detailed_info: In-depth information or instructions that offer valuable insights or steps.
        image_url: A URL linking to a high-quality and relevant image to enhance visual appeal.
        benefit: A description of how this content will positively impact the user's emotional state and well-being.

    The content should be designed to uplift, educate, and positively influence the user's emotional state within the context of {domain}. Ensure that:

        Activities: Include interactive and engaging activities that the user can participate in to boost their mood and well-being.
        Articles: Provide informative and insightful articles that offer support, education, and encouragement, backed by the latest research on postpartum care.
        Informative Material: Offer practical tips, advice, and resources that are easy to implement and beneficial for the user's mental and emotional health.

    Each piece of content should be tailored to the user's preferences, incorporating elements that resonate with them personally. Use a warm, empathetic tone to ensure the content feels supportive and encouraging. The information provided should be practical, relevant, and aligned with the latest research on postpartum care. Ensure visual engagement by including relevant and high-quality images for each content type.
    """

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