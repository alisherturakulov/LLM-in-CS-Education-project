//connects to index.html to handle requests to server
//script is currently in script tag of index.html
answer_history = {
   //"time" : "answer", and so on every 
}


const form = document.querySelector("form");

/**
 * records the part of the question that has been highlighted to put into the stringfield that holds the answers
 * the highlight answer input types are stringfields but store 
 * on separate lines the highlighted text in order of appearance in the question
 * @param {Event} event the mouseup event
 */
function recordHighlight(event){
      const selection = window.getSelection();
      const highlightedText = selection.toString().trim();//current highlighted text 
      
      //console.log(highlightedText);

      
      if (highlightedText.length > 0) {
                 //answerfield is consecutive input after <p.erroneousAnswer> container of the question string
            let sibling = event.target.nextElementSibling;
            while(sibling && sibling.tagName !== "INPUT"){
               sibling = sibling.nextElementSibling;
            }
            const correspondingInput = sibling;
            if (correspondingInput && correspondingInput.tagName === "INPUT") {
                //Append with a newline (use a comma or space if it's a standard text input)
               
                const separator = correspondingInput.value === "" ? "" : " ";
                correspondingInput.value += separator + highlightedText;
                
                //remove the highlight after processing
                selection.removeAllRanges();
                let changeEvent = new Event("change");
                event.target.dispatchEvent(changeEvent)
            }
      }
}

const errorAnswers = document.querySelectorAll("p.erroneousAnswer");

errorAnswers.forEach((element) => {
   //retreive the current highlighted text and append to a string;
   //separated by \n characters so place a \n character before kadding to the string each time
   element.addEventListener( "mouseup", recordHighlight);//mouseup once done highlighting
});


/**
 * records the current value of the input field and the time of recording
 * on a new line int he logfield
 * @param {InputEvent} event the input event attached to the call
 */
function autoSaveToLogfield(event){
   const inputField = event.target
   const inputValue = inputField.value
   let sibling = event.target.nextElementSibling;
   while(sibling && sibling.nextElementSibling.tagName !== "INPUT"){
      sibling  = sibling.nextElementSibling;
      console.log(sibling.tagName)
   }
   const logField = sibling;    //update history
   
   console.log("finally: " + logField.tagName)

    //time in est
    const currentTime = new Date().toLocaleString("en-US", {
        timeZone: "America/New_York",
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });

   logField.value += currentTime + " EST: " + inputValue + ";";// semicolons mark each line of logs
   //logfields to be processed on the server
}

/**
 * @param {Function} callee the function
 * @param {number} delay the ms delay to fire the functoin
 */
function debounce(callee, delay){
   let timeoutVar;
   return function(...args){
      clearTimeout(timeoutVar)
      timeoutVar = setTimeout(() => {
         callee.apply(this, args);
      }, delay);
   }
}

//save every 3000 ms
let autoSave = debounce((event) => autoSaveToLogfield(event), 1000);
//select all answerfields which are string input fields
const answerFields = document.querySelectorAll("p.erroneousAnswer ~ input");
answerFields.forEach((element) => {
   element.addEventListener("change", (e) => autoSave(e));
});




   //For highlight feature
   //use highlighting when selected by teacher in original form
//add event listeners to each that check for highlighting

//connect to  recordHighlight function which retrieves the highlighted text

//put each highlight in its own line ordered by index of apearance in the question string

//the input will be uneditable and will update as the user highlights text,

//to remove highlights, directly edit the input field

//students can still type in answers but can only use highlighting if selected for that field


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
