import textwrap

import google.generativeai as genai

import re
import json

GOOGLE_API_KEY = 'AIzaSyBeYvYSCPyPSLzrA67Uz4APOy2qPVbWOMs'

def model_setup():
    genai.configure(api_key=GOOGLE_API_KEY)

def get_chat_model():
    model_setup()
    model = genai.GenerativeModel('gemini-pro')
    return model.start_chat(history=[])

def get_normal_model(): # one off generator
    model_setup()
    return genai.GenerativeModel('gemini-pro')

def extract_json(text_response):
    # Find the first '{' to identify the start of a JSON object
    start = text_response.find('{')
    if start == -1:
        return None  # No JSON object found

    # Track the nesting level of curly braces
    nest_count = 0
    end = start
    while end < len(text_response):
        if text_response[end] == '{':
            nest_count += 1
        elif text_response[end] == '}':
            nest_count -= 1
            if nest_count == 0:
                # We've found the matching '}' for the initial '{'
                break
        end += 1

    # Extract the JSON string
    json_str = text_response[start:end+1]

    # Attempt to parse the JSON string
    try:
        json_obj = json.loads(json_str)
        return json_obj
    except json.JSONDecodeError:
        return None  # Handle invalid JSON or further refine error handling