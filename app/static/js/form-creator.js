//client-side script for form-creator
//to do: convert to react
//submitted forms are saved to a database (temporarily data folder)

//object holds assignment objects
const assignments = {};
// window.onload(()=>{
    
// });
// const number_of_questions = 
//= { firstAssignment:{}, secondAssignment{}, ...}

//assignment object 
//{
// title: "string",
// description: "string", 
// answer:"string", 
// media:"path/to/media in /media or database location"
//}
/**
 * 
 * @param {Integer} count
 */
async function generate_questions(count){
    const question_data = await fetch("./assign", {
        method:"GET",
    }
    );
    const questions = question_data.questions;
    return questions;
}

/**
 * generates the current assignment and saves into the database
 * @param {object} credentials if from a databse; for accessing
 */
function generateAssignment(credentials, title){

}


/**
 * loads saved assingments from data folder/database into current assignment viewer
 * @param {object} credentials credential obj if from a database; for accessing
 */
async function loadAssignment(count, credentials=undefined){
    const questions = await generate_questions(count);
    const form = document.querySelector("#assignment");
    for(let i =0; i<questions.size(); ++i){
        const question = document.createElement("p");
        question.className = "question";
        question.textContent = questions[i].question;
        form.appendChild(question);
    }
    
}

/**
 * remove the specific assignment from list of assignments
 * @param {object} credentials
 * @param {integer} title 
 */
function removeAssignment(credentials, title){

}

/**
 * removes the question with the given id from the list of questions in the current assignment
 * @param {string} questionId 
 */
function removeQuestion(questionId){

}
