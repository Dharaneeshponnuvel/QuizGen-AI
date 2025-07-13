from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load the predefined response JSON structure
with open("Response.json", "r") as f:
    RESPONSE_JSON = json.load(f)

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

@app.route('/generate', methods=['POST'])
def generate_mcq():
    try:
        data = request.get_json()

        text = data.get('text')
        subject = data.get('subject')
        tone = data.get('tone')
        number = data.get('number')

        if not all([text, subject, tone, number]):
            return jsonify({'error': 'Missing required fields'}), 400

        result = generate_evaluate_chain({
            "text": text,
            "subject": subject,
            "tone": tone,
            "number": number,
            "response_json": json.dumps(RESPONSE_JSON),
        })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8501, debug=True)
