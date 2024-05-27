import os
from flask import Flask, request, jsonify, render_template_string
from transformers import pipeline

# Define the classes
classes = ["fire", "water", "air"]

# Load pre-trained zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Initialize Flask app
app = Flask(__name__)

# Define your authentication key from environment variable
AUTH_KEY = os.getenv('AUTH_KEY')

# Define the HTML template for the interactive interface
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Text Classification</title>
</head>
<body>
    <h1>Text Classification</h1>
    <form id="classify-form">
        <label for="text">Enter text:</label><br><br>
        <input type="text" id="text" name="text" size="50"><br><br>
        <input type="submit" value="Classify">
    </form>
    <h2>Result:</h2>
    <p id="result"></p>
    <script>
        document.getElementById('classify-form').onsubmit = async function(event) {
            event.preventDefault();
            const text = document.getElementById('text').value;
            const response = await fetch('/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': '{{ auth_key }}'
                },
                body: JSON.stringify({ text: text })
            });
            const result = await response.json();
            document.getElementById('result').innerText = result.class ? `Class: ${result.class}` : `Error: ${result.error}`;
        }
    </script>
</body>
</html>
"""

# Define the classification function
def classify_text(text, candidate_labels):
    result = classifier(text, candidate_labels)
    predicted_class = result['labels'][0]
    return predicted_class

# Serve the HTML interface
@app.route('/')
def index():
    return render_template_string(html_template, auth_key=AUTH_KEY)

# Define the API endpoint
@app.route('/classify', methods=['POST'])
def classify():
    auth_key = request.headers.get('Authorization')
    if auth_key != AUTH_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401

    data = request.get_json()
    text = data.get('text', '')
    if text:
        predicted_class = classify_text(text, classes)
        return jsonify({'class': predicted_class})
    else:
        return jsonify({'error': 'No text provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
