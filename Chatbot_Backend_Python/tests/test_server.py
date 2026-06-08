from flask import Flask, request, jsonify
import subprocess
import re
import json
 
app = Flask(__name__)
 
@app.route('/generate', methods=['POST'])
def generate_response():
    data = request.json
    question = data.get('question')
    additional_text = "give me it's api and payload. When the user requests information, only return the API details and corresponding payloads. Avoid providing any additional steps, explanations, or summaries. If multiple APIs are involved, list them along with their respective payloads, but exclude any commentary or descriptive text."
    if not question:
        return jsonify({'error': 'Question is required'}), 400
 
    try:
        # Construct the command to run the GraphRAG Python script with the user's question
        command = f'python -m graphrag.query --root . --method local "{question} {additional_text}"'
        print(command)
        # Execute the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print("result",result)
        if result.returncode != 0:
            return jsonify({'error': 'Failed to generate response', 'details': result.stderr}), 500
 
        # Parse the output to extract relevant API details
        api_details = extract_response_only(result.stdout)
        print("api_details",api_details)
        # Return the extracted API details
        return jsonify({'result': api_details})
 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
 
def extract_response_only(response_text):
    # Identify the start of the response content after the logs and settings
    match = re.search(r'SUCCESS: Local Search Response:(.*)', response_text, re.DOTALL)
 
    if match:
        response_content = match.group(1).strip()
        return response_content
    else:
        return "No response content found."
 
 
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002)
