document.addEventListener('DOMContentLoaded', () => {
    // Extract 'currentURL' from the query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const currentURL = urlParams.get('currentURL');

    // Make an asynchronous call to your server to get the questions
    fetch(`/generateQuestions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: currentURL,
            // Include any other necessary data
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Assuming 'data' contains the questions and options
        // Render the questions and options on the page
        renderQuestions(data);
    })
    .catch(error => console.error('Error fetching questions:', error));
});

// Function to render questions on the page
function renderQuestions(questionsData) {
    // Implement the logic to dynamically create and display question elements on the page
    questionsAsHTML = questionsData; //later we need to parse this to ensure ChatGTP returns the quiz in the correcte format. But for now lets just dump it!
    document.getElementById('question-placeholder').textContent = questionsAsHTML;
}
