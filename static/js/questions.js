

document.addEventListener('DOMContentLoaded', function() {
    AddFormListener('q1');
    AddFormListener('q2');
    AddFormListener('q3');

});

function AddFormListener (id) {
    const form = document.getElementById(id);
    //retrieve the correct solution
    formSolution = ""
    let node = form.firstElementChild;
    while (node){
        if (node.tagName === "INPUT" && node.type === "hidden") {
            formSolution = node.value;
            break;
        }
        node = node.nextElementSibling;
    }
    form.addEventListener('click', function(event) {
        if (event.target.type === 'radio') {
            const name = event.target.name;
            const value = event.target.value;
            let insertionPoint = event.target;
            if (formSolution && formSolution == value){
                insertAnswer (insertionPoint, "Correct!")
            }else {
                const data = new FormData();
                data.append(name, value);

                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/fetch_answer', true);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

                xhr.onload = function () {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        console.log('Success:', xhr.responseText);

                        insertAnswer(insertionPoint, xhr.responseText)

                    } else {
                        console.log('Error:', xhr.statusText);
                        // Handle error here
                    }
                };
            }

            // Convert FormData to URL encoded string
            const payload = new URLSearchParams(data).toString();
            xhr.sendc(payload);
            //Kill interaction with other radiobuttons
            disableRadioButtons(name);
            //enable next question button
            enableNextButton();
        }
    });

}

function insertAnswer(insertionPoint, response) {
    while (insertionPoint.nextElementSibling.nodeName !== 'INPUT' && insertionPoint.nextElementSibling.nodeName !== 'P')
        insertionPoint = insertionPoint.nextElementSibling;
    if (insertionPoint) {
        responseElement = document.createElement('p');
       // responseElement.id = "answer_" + name
        insertionPoint.parentNode.insertBefore(responseElement, insertionPoint.nextSibling);
        responseElement.textContent = response;
    }
}

function enableNextButton(){}
function enableBackButton(){}

function clickNextButton(){
    enableBackButton()
}

function clickBackButton(){}

function disableNextButton(){}
function disableBackButton(){}

//make sure the user can't click again
function disableRadioButtons(whichQuestion){}¨å



























/*
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
*/
