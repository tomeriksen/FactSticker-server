from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, session
from forms import URLForm

import openai
from dotenv import load_dotenv
import os
import urllib.parse
from openai_response import openai_generate_questions, openai_send_answer, clean_up_questions

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
@app.route('/questions', methods=['POST'])
def questions():
    url_form = URLForm(request.form)
    if url_form.validate_on_submit():
        questions  = openai_generate_questions(url_form.url.data)
        questions = clean_up_questions(questions)
        session['questions'] = questions
        return render_template("questions.html", questions=questions)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    def field_name(pos):
        return list(request.form.items())[pos][0]
    def field_value(pos):
        return list(request.form.items())[pos][1]

    if len (request.form) >0:
        #generate_answer (answers[0][0], answers[0][1])
        response_list = []
        question_list = extract_questions_from_form (session['questions'])
        response_list.append(openai_send_answer(field_name(0), field_value(0)))
        response_list.append(openai_send_answer(field_name(1), field_value(1)))
        response_list.append(openai_send_answer(field_name(2), field_value(2)))
        # eg 'q1', 'c'
        return render_template("answer.html", responses=response_list, questions=question_list, answers=list(request.form.items()))

@app.route('/fetch_answer', methods=['POST'])
def fetch_answer():
    if len (request.form) == 1:
        result = openai_send_answer(form_field_name(0), form_field_value(0))
        return result["openai_response"]

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
    app.run(debug=True)


