from readability import Document #pip3 install readability-lxml
import requests #pip3 install requests

def extract_article(url):
    try:
        # Sending a request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parsing the content of the page
            doc = Document(response.text)

            # Extracting the inner text of the body tag
            summary = doc.summary()
            title = doc.title()

            return {'title': title, 'content': summary}
        else:
            return f"Failed to retrieve content, status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

#print(extract_article("https://northvolt.com/articles/northvolt-sodium-ion/"))