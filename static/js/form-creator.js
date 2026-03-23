//client-side script for form-creator
//to do: convert to react
//submitted forms are saved to a database (temporarily data folder)

//object holds assignment objects
const assignments = {};
//= { firstAssignment:{}, secondAssignment{}, ...}

//assignment object 
//{
// title: "string",
// description: "string", 
// answer:"string", 
// media:"path/to/media in /media or database location"
//}

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
function loadAssignment(credentials, title){

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
