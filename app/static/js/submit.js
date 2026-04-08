//connects to index.html to handle requests to server
//script is currently in script tag of index.html

/**
 * records the part of the question that has been highlighted to put into the stringfield that holds the answers
 * the highlight answer input types are stringfields but store 
 * on separate lines the highlighted text in order of appearance in the question
 */
function recordHighlight(){

}

//select all answerfields which are string input fields
answers= document.querySelectorAll("p.erroneousAnswer + input");

//add event listeners to each that check for highlighting

//connect to  recordHighlight function which retrieves the highlighted text

//put each highlight in its own line ordered by index of apearance in the question string

//the input will be uneditable and will update as the user highlights text,

//to remove highlights, directly edit the input field

//students can still type in answers but can only
//use highlighting when selected by teacher in original form

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
