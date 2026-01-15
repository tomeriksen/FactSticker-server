"""
FactSticker Server - Flask Application

A quiz application that generates questions from web articles using OpenAI.
Users provide a URL, and the app scrapes the article content, sends it to OpenAI
to generate quiz questions, and presents them in an interactive UI.

Routes:
    - /              : Home page with URL input form
    - /questions     : Generate and display quiz questions from a URL
    - /submit_answer : Legacy route for batch answer submission
    - /fetch_answer  : AJAX endpoint for single answer feedback
    - /quiz          : New Codecademy-style quiz UI (single question at a time)
    - /api/quiz/start: API to start quiz, returns first question + total count
    - /api/quiz/next : API to get next question or completion status
"""

from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, session
from forms import URLForm

import openai
from dotenv import load_dotenv
import os
import urllib.parse
from openai_response import openai_generate_questions, openai_send_answer, split_questions, generate_quiz_questions
from article_scraper import extract_article

# Load environment variables from .env file (contains OPENAI_API_KEY)
load_dotenv()

app = Flask(__name__)
app.secret_key = 'dr.dre%the§cronIQ'  # Used for session cookie signing
openai.api_key = os.getenv("OPENAI_API_KEY")


# =============================================================================
# Helper Functions
# =============================================================================

def form_field_name(pos):
    """Get the field name at position `pos` from the submitted form data."""
    return list(request.form.items())[pos][0]


def form_field_value(pos):
    """Get the field value at position `pos` from the submitted form data."""
    return list(request.form.items())[pos][1]


def extract_questions_from_form(form_txt):
    """
    Parse HTML form text and extract question paragraphs.
    Used to retrieve questions from session for answer display.

    Args:
        form_txt: HTML string containing question forms

    Returns:
        List of BeautifulSoup paragraph elements
    """
    questions = []
    soup = BeautifulSoup(form_txt, 'html.parser')
    try:
        questions = soup.find_all("p")
    except Exception as e:
        print(print("Error:Exception while parsing: " + e))
    return questions


# =============================================================================
# Legacy Routes (Original multi-question flow)
# =============================================================================

@app.route('/')
def index():
    """
    Home page - displays URL input form.
    Clears any previous quiz questions from session.
    """
    session['questions'] = ""
    url_form = URLForm(request.form)
    print("index")
    return render_template("index.html", url_form=url_form)


@app.route('/questions', methods=['GET', 'POST'])
def questions():
    """
    Generate quiz questions from a URL.

    Accepts URL via:
        - GET: ?url=https://example.com/article
        - POST: Form submission from index page

    Process:
        1. Extract article content from URL
        2. Send to OpenAI to generate questions
        3. Store questions in session for answer validation
        4. Render questions page
    """
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
    """
    Legacy route: Submit all answers at once and get feedback.
    Renders a page showing all questions with OpenAI's response for each answer.

    Note: This route is largely unused - the current flow uses /fetch_answer
    via AJAX for real-time feedback on individual answers.
    """
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
    """
    AJAX endpoint for single answer feedback.
    Called by questions.js when user selects a radio button answer.

    Returns:
        Plain text response from OpenAI explaining if answer is correct/incorrect
    """
    if len(request.form) == 1:
        result = openai_send_answer(form_field_name(0), form_field_value(0))
        return result


# =============================================================================
# New Quiz API (Codecademy-style single-question flow)
# =============================================================================

# Mock data for UI development - will be replaced with OpenAI-generated questions
# Each question includes pre-computed explanations for instant feedback (no API call needed)
MOCK_QUESTIONS = [
    {
        "question": "Who designed the Python programming language?",
        "options": {
            "a": "Guido van Rossum",
            "b": "James Gosling",
            "c": "Bjarne Stroustrup"
        },
        "correct": "a",
        "explanations": {
            "a": "Correct! Guido van Rossum started Python as a hobby project in 1989 and released it in 1991.",
            "b": "Incorrect. James Gosling created Java at Sun Microsystems, not Python.",
            "c": "Incorrect. Bjarne Stroustrup created C++, not Python."
        }
    },
    {
        "question": "When was Python first released?",
        "options": {
            "a": "1985",
            "b": "1991",
            "c": "1995"
        },
        "correct": "b",
        "explanations": {
            "a": "Incorrect. Python wasn't released until 1991. In 1985, C++ was just being standardized.",
            "b": "Correct! Python 0.9.0 was released in February 1991.",
            "c": "Incorrect. By 1995, Python was already at version 1.2. Java was released in 1995."
        }
    },
    {
        "question": "What programming paradigm does Python support?",
        "options": {
            "a": "Only object-oriented",
            "b": "Only functional",
            "c": "Multi-paradigm"
        },
        "correct": "c",
        "explanations": {
            "a": "Incorrect. While Python supports OOP, it also supports functional and procedural programming.",
            "b": "Incorrect. Python supports functional programming but isn't limited to it.",
            "c": "Correct! Python is multi-paradigm, supporting object-oriented, functional, and procedural styles."
        }
    }
]


@app.route('/api/quiz/start', methods=['POST'])
def api_quiz_start():
    """
    Start a new quiz session.

    Accepts JSON body:
        {
            "url": "https://example.com/article",
            "content": "Article text from browser DOM (optional)",
            "title": "Article title (optional)"
        }

    If content is provided (from Chrome Extension), uses it directly.
    Otherwise, falls back to server-side scraping of the URL.

    Returns:
        JSON: {question, options, correct, explanations, total_questions}
    """
    data = request.get_json() or {}
    url = data.get('url', '')
    content = data.get('content', '')
    title = data.get('title', '')

    # Log what we received
    print(f"Quiz start - URL: {url}")
    print(f"Quiz start - Content length: {len(content)} chars")
    print(f"Quiz start - Title: {title}")

    # If no content from Chrome Extension, try server-side scraping
    if not content and url:
        print("No content from extension, falling back to server-side scraping...")
        article = extract_article(url)
        if isinstance(article, dict):
            content = article.get('content', '')
            title = title or article.get('title', '')
        else:
            # extract_article returned an error string
            return jsonify({"error": f"Could not fetch article: {article}"}), 400

    # Generate questions using OpenAI
    if content:
        questions = generate_quiz_questions(content, title=title, url=url, num_questions=3)

        # Check for errors
        if isinstance(questions, dict) and "error" in questions:
            print(f"OpenAI error: {questions['error']}")
            # Fall back to mock data on error
            questions = MOCK_QUESTIONS
    else:
        # No content available, use mock data
        print("No content available, using mock data")
        questions = MOCK_QUESTIONS

    # Store questions in session
    session['quiz_questions'] = questions
    session['current_question'] = 0
    session['article_url'] = url
    session['article_title'] = title

    # Return first question with total count
    first_question = questions[0]
    response = {**first_question, 'total_questions': len(questions)}
    return jsonify(response)


@app.route('/api/quiz/next', methods=['POST'])
def api_quiz_next():
    """
    Get the next question in the quiz.

    Increments question counter stored in session. If all questions
    have been answered, returns completion status.

    Returns:
        JSON: {question, options, correct, explanations} or {done: True}
    """
    # Get questions from session (generated by /api/quiz/start)
    questions = session.get('quiz_questions', MOCK_QUESTIONS)

    current = session.get('current_question', 0) + 1
    session['current_question'] = current

    if current >= len(questions):
        return jsonify({"done": True, "message": "Quiz complete!"})

    return jsonify(questions[current])


@app.route('/quiz')
def quiz():
    """
    Render the new Codecademy-style quiz page.

    Accepts optional URL parameter from Chrome Extension:
        /quiz?url=https://example.com/article

    Features:
        - Single question at a time
        - Card-style clickable options
        - Instant feedback with explanations
        - Progress bar
        - Score tracking
    """
    article_url = request.args.get('url', '')
    return render_template("quiz.html", article_url=article_url)


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5001)
