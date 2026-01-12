from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, session
from forms import URLForm

import openai
from dotenv import load_dotenv
import os
import urllib.parse
from openai_response import openai_generate_questions, openai_send_answer, split_questions

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'dr.dre%the§cronIQ'
openai.api_key = os.getenv("OPENAI_API_KEY")


def form_field_name(pos):
    return list(request.form.items())[pos][0]

def form_field_value(pos):
    return list(request.form.items())[pos][1]


@app.route('/')
def index():
    session['questions'] = ""
    url_form = URLForm(request.form)
    print("index")
    return render_template("index.html", url_form=url_form)
@app.route('/questions', methods=['GET', 'POST'])
def questions():
    # Handle GET request with URL parameter
    if request.method == 'GET':
        url = request.args.get('url')
        if not url:
            return render_template("index.html", url_form=URLForm(), error="Error: No URL provided")
    else:
        url_form = URLForm(request.form)
        if not url_form.validate_on_submit():
            return render_template("index.html", url_form=url_form)
        url = url_form.url.data

    questions = openai_generate_questions(url)
    if questions.startswith("Error:"):
        return render_template("index.html", url_form=URLForm(), error=questions)
    question_list = split_questions(questions)
    session['questions'] = questions
    return render_template("questions.html", question_list=question_list)

@app.route('/submit_answer', methods=['GET', 'POST'])
def submit_answer():
    # Get answers from either GET params or POST form
    if request.method == 'GET':
        answers = list(request.args.items())
    else:
        answers = list(request.form.items())

    if len(answers) > 0:
        response_list = []
        question_list = extract_questions_from_form(session.get('questions', ''))
        for q_name, q_value in answers:
            response_list.append(openai_send_answer(q_name, q_value))
        return render_template("answer.html", responses=response_list, questions=question_list, answers=answers)

@app.route('/fetch_answer', methods=['POST'])
def fetch_answer():
    if len (request.form) == 1:
        result = openai_send_answer(form_field_name(0), form_field_value(0))
        return result

@app.route('/generate-questions-from-url', methods=['POST'])
def generate_questions_from_url():
    pass


from bs4 import BeautifulSoup
def extract_questions_from_form(form_txt):
    questions = []
    soup = BeautifulSoup(form_txt, 'html.parser')
    try:
        questions = soup.find_all("p")
    except Exception as e:
        print(print("Error:Exception while parsing: " + e))
    return questions

if __name__ == '__main__':
    app.run(debug=True, port=5001)


