# Project Protoype
Web app similar to socrates system: https://github.com/junli-cuny/Socrates
## Minimum Viable Product:
 ### Features:
 - Allow teachers to create assignments;
 - Assignments can be created, shared with students via qr code, and submitted by students;
 - Pipeline uses LLM apis to generate/verify error explanations that students give for each question.
 - Submitted assignments are stored in a database;
 - Information on performance across assignments and questions available for Instructors;
 
 ### Feature Details:
 - Assignments are organized into tasks;
	- Each task can have a question description, sample (error) solutions, and input fields;
- LLMs can be cycled through in case one LLM is busy
- LLM Chat feature to ask questions
- Settings are available controlling properties such as:
	- Attempts allowed; level of AI assistance; 
	- Display/ hide correctness of submitted answers; 
	- How many attempts are allowed, score visibility; 
	- Degree to which LLM model assists students with answering; 
- Database to store students and assignment submissions
	- Instructors can view data on student submissions and performance
	- Database also stores account credentials for instructors
	- Each instructor has a column of assignments
	- Each assignment has a column of submissions
	- Submissions have a columnf for submission time, time taken, token usage, chat history/submission logs, and the generated task itself
	
 ### After prototype:
- Comment section to allow students to ask questions about the assingment; can be toggled by instructor to make visible to instructor/class only.
	
