from flask import Flask, render_template, request, jsonify
import openai
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    print("index")
    return render_template("index.html")
@app.route('/questions')
def questions():
    data = request.json
    url = data['url']
    return render_template("questions.html?url=" + urllib.parse.urlencode(url))

@app.route('/generate-questions-from-url', methods=['POST'])
def generate_questions():
    pass
    
'''
def generate_questions():
    data = request.json
    current_url = data['url']
    content = data['content']
    user_id = data['userID']

    prompt = f"Based on the content at {current_url}, generate 3 multiple-choice questions to test knowledge."

    try:
        response = openai.Completion.create(
          engine="text-davinci-003",
          prompt=prompt,
          temperature=0.5,
          max_tokens=1024,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        return jsonify(response.choices[0].text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''
if __name__ == '__main__':
    app.run(debug=True)

    
    
    from openai import OpenAI
client = OpenAI()

