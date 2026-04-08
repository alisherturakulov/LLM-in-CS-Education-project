//client-side script for form-creator
//submitted forms are saved to a database (temporarily data folder)
            //listens and updates based on the number of questions selection field 
document.addEventListener("DOMContentLoaded", () => {
    const wrapper = document.querySelector("form#assignment");
    const number_of_q_selection = wrapper.querySelector("input#number_of_questions");
    
    //listen for when number input loses focus
    number_of_q_selection.addEventListener("change", (e) => {
        console.log(wrapper.className);
        let question_fields = wrapper.querySelectorAll(".questionsContainer");
        console.log(question_fields);
        
        const num_questions = parseInt(e.target.value) || 1;//min entries = 1
        console.log("questions: " + num_questions);
        if(question_fields.length > num_questions){
            //remove extra question, left with num_questions count of qs
            // const keep = prompt(`You have more than ${num_questions}, type 'yes' or 'y' to remove extra questions`);
            // if(keep?.toLowerCase().includes("yes") || keep?.toLowerCase().includes("y")){
                for(let i = question_fields.length-1; i>=num_questions; --i){
                    question_fields[i].remove();
                }
            // }else{
            //     e.target.value = question_fields.length;
            // }
        }else{
            //const lastQuestion = question_fields[question_fields.length-1];
            for(let i = question_fields.length; i < num_questions; ++i){
                console.log("calling cloneNode");
                question_fields = wrapper.querySelectorAll(".questionsContainer");
                const cloneQ = question_fields[0].cloneNode(true);
                //console.log(cloneQ.toString());
                const inputs = cloneQ.querySelectorAll("input, select");
                let name;
                let idIndex = 0
                inputs.forEach((input) => {
                    //get name
                    name = input.name?.substring(input.name.lastIndexOf("-"));
                    if (input.name) input.name = `questions-${i}${name}`;
                    if (input.id) input.id = `questions-${i}${name}`;
                    if(input.type && input.type !== "submit" && input.type !== "button"){
                    input.value = "";
                    }
                    ++idIndex
                });
                const labels = cloneQ.querySelectorAll("label");
                idIndex = 0
                labels.forEach((label)=>{
                    name = label.name?.substring(label.name.lastIndexOf("-"));
                    if(label.htmlFor) {
                        label.htmlFor = `questions-${i}${name}`;
                    }
                    ++idIndex
                });
                
                wrapper.querySelector(".questionFieldDiv").append(cloneQ);
            }
            };
    });
});


