import sys
from openai import OpenAI
from dotenv import load_dotenv
from article_scraper import extract_article

load_dotenv()

openai_conversation_history = [] #global variable that keeps track of the conversation with openai
openai_max_request_len = 10000 #the maximum length of the request prompt

def main():
    # Check if a URL is provided as a command-line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url=input("Please paste in an URL (with https:// included")

    questions = generate_questions(url)

    print(f"Here are the questions: {questions}")



    which_question = input("Name of First answer:")
    answer1 = input("Value of First answer:")
    solution1 = generate_answer(which_question, answer1)
    print(f"answer: {solution1}")

    which_question = input("Name of 2nd answer:")
    answer2 = input("Value of 2nd answer:")
    solution2 = generate_answer(which_question, answer2)
    print(f"answer: {solution2}")

    which_question = input("Name of 3rd answer:")
    answer3 = input("Value of 3rd answer:")
    solution3 = generate_answer(which_question, answer2)
    print(f"answer: {solution3}")
        
def generate_questions(url):
    try:
        article = extract_article(url)
        if len(article) > openai_max_request_len-500:
            article = article[:openai_max_request_len-500]
        #print(f"Fetch page as article: {article}")
        #start buidling the converstation history
        client = OpenAI()
        system_prompt= "Act like a programmer and generate your answers in HTML format."
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
        openai_conversation_history.append({ "role": "system", "content": system_prompt})
        openai_conversation_history.append({ "role": "user", "content":initial_prompt})


        response = client.chat.completions.create(
            model="gpt-4",
            messages= openai_conversation_history,
            temperature=1,
            max_tokens=1065,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        assistant_response = response.choices[0].message.content
        openai_conversation_history.append({ "role": "assistant", "content": assistant_response}) #add openai's resonse to the conversation history
        return assistant_response
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error: An issue occurred while generating questions."

def generate_answer(which_question, answer):
    new_prompt= f'name = "{which_question}" value ="{answer}". Correct? Motivate. Start response with one of these words: Correct,  Right, Wrong, Incorrect, Nailed it, Fantastic, Not right'
    openai_conversation_history.append({ "role": "assistant", "content":new_prompt})
    client = OpenAI()
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
    return assistant_response


if __name__ == "__main__":
    main()