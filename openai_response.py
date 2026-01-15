import sys
from openai import OpenAI
from dotenv import load_dotenv
from article_scraper import extract_article
import re
import json

load_dotenv()

openai_conversation_history = [] #global variable that keeps track of the conversation with openai
openai_max_request_len = 8192 #the maximum length of the request prompt

def main():
    # Check if a URL is provided as a command-line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url=input("Please paste in an URL (with https:// included")

    questions = openai_generate_questions(url)

    print(f"Here are the questions: {questions}")



    #which_question = input("Name of First answer:")
    answer1 = input("Value of First answer:")
    solution1 = openai_send_answer("q1", answer1)
    print(f"answer: {solution1}")

    #which_question = input("Name of 2nd answer:")
    answer2 = input("Value of 2nd answer:")
    solution2 = openai_send_answer("q2", answer2)
    print(f"answer: {solution2}")

    #which_question = input("Name of 3rd answer:")
    answer3 = input("Value of 3rd answer:")
    solution3 = openai_send_answer("q3", answer3)
    print(f"answer: {solution3}")

def calculate_length_of_conversation():
    return len(json.dumps(openai_conversation_history))
def shorten_article (how_much):
    how_much = max(how_much, 0) #should be a positive number
    for msg in openai_conversation_history:
        if msg.get("role") == "user": #find the first propmpt based on the article
            msg["content"] = msg["content"][:-how_much] #shorten the article
            break

def openai_generate_questions(url):#, content = None):
    try:
        if True:#not content:
            article = extract_article(url) #{'title', 'content}
            if isinstance(article, str):
                # extract_article returned an error string
                return f"Error: {article}"
            content = article.get("content")
            title = article.get("title")
            if len(content) > openai_max_request_len-2000:
                content = content[:openai_max_request_len-2000]
        #print(f"Fetch page as article: {article}")
        #start buidling the converstation history
        client = OpenAI()
        system_prompt= "Act like a programmer and generate your answers in HTML format."
        initial_prompt = f'''
        Generate three multiple-choice questions based on the content found last in this message. 
        The content is from a webpage found at {url}  with the title: "{title}"
        Give the answer as three separate FORM. Omit all other HTML code in your answer. 
        You MUST stick to this format:
        <form id = "q1">
        <p><!-- question 1 --></p>
        <input type="radio" name="q1" value="a" id="q1a"> 
        <label for="q1a"><!--answer a--></label>
        <input type="radio" name="q1" value="b" id="q1b"> 
        <label for="q1b"><!--answer b--></label>
        <input type="radio" name="q1" value="c" id="q1c"> 
        <label for="q1c"><!--answer c--></label>
        <input type="submit" value="Submit">
        <input type="hidden" id="solution q1"  value="<!--Correct solution-->">
        </form>
        <form id= "q2">
        ...
                            
        Here is the content from the mentioned web page:
        {content}
                    '''
        openai_conversation_history.append({ "role": "system", "content": system_prompt})
        openai_conversation_history.append({ "role": "user", "content":initial_prompt})


        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages= openai_conversation_history,
            temperature=0.2,
            max_tokens=1065,
            seed=42
        )
        assistant_response = response.choices[0].message.content
        openai_conversation_history.append({ "role": "assistant", "content": assistant_response}) #add openai's resonse to the conversation history
        #truncate msg hsitroy if the convesaton history runs too long
        length_of_conversation = calculate_length_of_conversation()
        if length_of_conversation > openai_max_request_len:
            shorten_article (length_of_conversation - openai_max_request_len +100)
        return assistant_response
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error: An issue occurred while generating questions."


def old_openai_generate_questions(url):  # , content = None):
    try:
        if True:  # not content:
            article = extract_article(url)
            if len(article) > openai_max_request_len - 2000:
                article = article[:openai_max_request_len - 2000]
        # print(f"Fetch page as article: {article}")
        # start buidling the converstation history
        client = OpenAI()
        system_prompt = "Act like a programmer and generate your answers in HTML format."
        initial_prompt = f'''
                    Generate three multiple-choice questions based on the content found last in this message. 
                    The content is from a webpage found at {url}. 
                    Give the answer as a FORM. Omit all other HTML code in your answer: 
                    You MUST stick to this format:
                    <form>
                    <p><!-- question 1 --></p>
                    <input type="radio" name="q1" value="a"> <!--answer a--><br>
                    <input type="radio" name="q1" value="b"> <!--answer a--><br>
                    <input type="radio" name="q1" value="c"> <!--answer a--><br>
                    <p><!-- question 1 --></p>
                    ...
                    <input type="submit" value="Submit">
                    </form>

                    Here is the content for {url}.
                     {article}
                    '''
        openai_conversation_history.append({"role": "system", "content": system_prompt})
        openai_conversation_history.append({"role": "user", "content": initial_prompt})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=openai_conversation_history,
            temperature=1,
            max_tokens=1065,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        assistant_response = response.choices[0].message.content
        openai_conversation_history.append(
            {"role": "assistant", "content": assistant_response})  # add openai's resonse to the conversation history
        # truncate msg hsitroy if the convesaton history runs too long
        length_of_conversation = calculate_length_of_conversation()
        if length_of_conversation > openai_max_request_len:
            shorten_article(length_of_conversation - openai_max_request_len + 100)
        return assistant_response

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error: An issue occurred while generating questions."


def openai_send_answer(which_question, answer):
    result  = {"correct_answer": None, "openai_response": None}
    new_prompt= f'My answer to {which_question} is {answer}. Using less than 130 chars, explain why the this is wrong. Start with "Incorrect"'
    openai_conversation_history.append({ "role": "user", "content":new_prompt})
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_conversation_history,
            temperature=0.2,
            max_tokens=1065,
            seed=42
        )
        assistant_response = response.choices[0].message.content
        if calculate_length_of_conversation() + len(assistant_response) + 1000 < openai_max_request_len:
            openai_conversation_history.append( {"role": "assistant", "content": assistant_response})  # add openai's resonse to the conversation history
        #else ignore adding asnwer to conversation history
        return assistant_response
    except Exception as e:
        error_msg = "Error: Could not retrieve response from openai" + str(e)
        print (error_msg)
        return error_msg


# =============================================================================
# New Quiz API Functions (JSON-based, single question at a time)
# =============================================================================

def generate_quiz_questions(content, title="", url="", num_questions=3):
    """
    Generate quiz questions from article content.

    Returns a list of question objects, each with:
    {
        "question": "Question text",
        "options": {"a": "Option A", "b": "Option B", "c": "Option C"},
        "correct": "a",
        "explanations": {
            "a": "Correct! Explanation...",
            "b": "Incorrect. Explanation...",
            "c": "Incorrect. Explanation..."
        }
    }
    """
    if not content or len(content.strip()) < 100:
        return {"error": "Article content is too short or empty"}

    # Truncate content if too long
    max_content_len = 6000
    if len(content) > max_content_len:
        content = content[:max_content_len]

    client = OpenAI()

    system_prompt = """You are a quiz generator. Generate quiz questions based on article content.
You MUST respond with valid JSON only - no markdown, no code blocks, just pure JSON.
Each question must have exactly 3 options (a, b, c) and explanations for ALL options."""

    user_prompt = f"""Generate {num_questions} multiple-choice quiz questions based on this article.

Article Title: {title}
Article URL: {url}
Article Content:
{content}

Respond with a JSON array of question objects. Each object must have:
- "question": The question text
- "options": Object with keys "a", "b", "c" and their answer text
- "correct": The letter of the correct answer ("a", "b", or "c")
- "explanations": Object with keys "a", "b", "c" explaining why each is correct or incorrect

Example format:
[
  {{
    "question": "What year was Python created?",
    "options": {{
      "a": "1989",
      "b": "1991",
      "c": "1995"
    }},
    "correct": "b",
    "explanations": {{
      "a": "Incorrect. Python development started in 1989, but it wasn't released until 1991.",
      "b": "Correct! Python 0.9.0 was first released in February 1991.",
      "c": "Incorrect. By 1995, Python was already at version 1.2."
    }}
  }}
]

Generate exactly {num_questions} questions. Respond ONLY with the JSON array, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            seed=42
        )

        response_text = response.choices[0].message.content.strip()

        # Try to parse JSON, handling potential markdown code blocks
        if response_text.startswith("```"):
            # Remove markdown code block
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        questions = json.loads(response_text)

        # Validate structure
        if not isinstance(questions, list):
            return {"error": "Invalid response format from OpenAI"}

        for q in questions:
            if not all(key in q for key in ["question", "options", "correct", "explanations"]):
                return {"error": "Missing required fields in question"}

        return questions

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response was: {response_text[:500]}")
        return {"error": f"Failed to parse OpenAI response as JSON: {str(e)}"}
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"error": f"OpenAI API error: {str(e)}"}



#Utility functions for treating openAI output
from bs4 import BeautifulSoup

#clean_up_questions inserts the correct action into the form that OpenAI (hopefully) has returned
def clean_up_questions(questions):
    result = ""
    try:
        soup = BeautifulSoup(questions, 'html.parser')
        form_tags = soup.find_all("form")
        for form in form_tags:
            #form["id"] = "quiz-form"
            form["action"] = "/submit_answer" # /"+ form["id"]
            form["method"] = "POST"
        result = str(soup)
    except Exception as e:
        print("Error:Exception while parsing:" )
        print(e)

    return result
def split_questions(questions):
    result = []
    try:
        soup = BeautifulSoup(questions, 'html.parser')
        all_forms = soup.find_all("form")
        '''for i in range(len(all_forms)):
            form = all_forms[i]
            new_div = soup.new_tag("div")
            new_div["class"] = "row"
            new_div["id"] = "div_q_" + str(i)
            form.insert_before(new_div)
            new_div.append(form)
        # soup.b.string.insert_before(tag)'''
        for form in all_forms:
            form["action"] = "/submit_answer"  # /"+ form["id"]
            form["method"] = "POST"
            result.append(form)

    except Exception as e:
        print("Error:Exception while parsing:" )
        print(e)

    return result
if __name__ == "__main__":
    main()