//connects to index.html to handle requests to server
//script is currently in script tag of index.html
answer_history = {
   //"time" : "answer", and so on every 
}


/**
 * records the part of the question that has been highlighted to put into the stringfield that holds the answers
 * the highlight answer input types are stringfields but store 
 * on separate lines the highlighted text in order of appearance in the question
 */
function recordHighlight(){

}

//select all answerfields which are string input fields
errorAnswers = document.querySelectorAll("p.erroneousAnswer");
answerFields = document.querySelectorAll("p.erroneousAnswer + input");
form = document.querySelector("form");
form.on("submit", ()=>{
   //add the answer_history obejct to the response body, to be processed in the server routes.py
})

function debounce(callee, delay){
   clearTimeout(tout)
   return (args) => {

   }
}

function autoSaveToHistoryObject(event){

}

answerFields.array.forEach((element) => {
   element.addEventListener("change", autoSaveToHistoryObject(event));
   //once the changes are made and the user clicks off, the autosave feature is connected
   //event.parent.value is saved by using time(): "answer input" to place into history object
   const currentInput = event.parent.value
   const time = Time()
   const currentTime = time.now()

   answer_history[currentTime] = currentInput;

});

   //For highlight feature
   //use highlighting when selected by teacher in original form
//add event listeners to each that check for highlighting

//connect to  recordHighlight function which retrieves the highlighted text

//put each highlight in its own line ordered by index of apearance in the question string

//the input will be uneditable and will update as the user highlights text,

//to remove highlights, directly edit the input field

//students can still type in answers but can only
errorAnswers.forEach((element) => {
   element.addEventListener("mousedown", autoSaveToHistoryObject(event));
   //retreive the current highlighted text and append to a string;
   //separated by \n characters so place a \n character before kadding to the string each time
   const highlightedText = //highlighted text
   const newAddition = "\n" + highlightedText

   const currentTime = time.now()
   const correspondingInput = event.parent.querySelector("input");

   correspondingInput.value += newAddition

   
});

   //History feature
//addEventListener("change")
//check for changes every few seconds
//or save a new time after each burst of changes from tpying

//send the change history as a object of time:answer pairs to be put into the submission in submissions.json

   /**
             * requests questions form the pipeline running on the server and
             * adds questions with values in the container 
             * with id values corresponding to index in server response 
            */
            function loadQuestions(){

            }

            /**
             * Submits the error answers to the server pipeline
             * returns the feedback from the server on the error answer
             * @return {string} the feedback on the correctness of the user errorAnswer
            */
            function submitAnswers(){

            }

            /**
             * gets the string input value of the errorAnswer field
             * @return {string} errorAnswer input value from user
            */
            function getErrorInput(){

            }

            /**
             * gets the feedback to the list of answers  from the server
             * errorAnswer indices are in the same order as the questions were received in
             * @param {string[]} 
             * 
            */
            function checkErrorAnswers(errorAnswers){

            }
