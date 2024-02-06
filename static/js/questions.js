
/*document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quiz-form');
    form.addEventListener('click', function(event) {
        if (event.target.type === 'radio') {
            console.log(event.target.name);
            console.log(event.target.value);
            /*
            const data = new FormData(form);
            const xhr = new XMLHttpRequest();
            xhr.open('POST', form.action, true);
            xhr.onload = function () {
                if (xhr.status >= 200 && xhr.status < 300) {
                    console.log('Response:', xhr.responseText);
                    // Handle success here, maybe display a message to the user
                } else {
                    console.log('Failed to submit answer');
                     // Handle error here
                }
            };
            xhr.send(data);
            * /

        }
    });
});
*/

document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('quiz-form');
            form.addEventListener('click', function(event) {
                if (event.target.type === 'radio') {
                    const name = event.target.name;
                    const value = event.target.value;
                    const data = new FormData();
                    data.append(name, value);

                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/fetch_answer', true);
                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

                    xhr.onload = function () {
                        if (xhr.status >= 200 && xhr.status < 300) {
                            console.log('Success:', xhr.responseText);
                            let insertionPoint = event.target;
                            while (insertionPoint.nextElementSibling.nodeName !== 'INPUT' && insertionPoint.nextElementSibling.nodeName !== 'P')
                                insertionPoint = insertionPoint.nextElementSibling;
                            if (insertionPoint ) {
                                responseElement = document.createElement('p');
                                responseElement.id = "answer_" + name
                                event.target.parentNode.insertBefore(responseElement, insertionPoint.nextSibling);
                                responseElement.textContent = xhr.responseText;
                            }

                        } else {
                            console.log('Error:', xhr.statusText);
                            // Handle error here
                        }
                    };

                    // Convert FormData to URL encoded string
                    const payload = new URLSearchParams(data).toString();
                    xhr.send(payload);
                }
            });
        });


/* document.addEventListener('DOMContentLoaded', () => {
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
*/

