from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/generateQuestions', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
