//connects to index.html to handle requests to server
//script is currently in script tag of index.html
answer_history = {}

document.addEventListener('DOMContentLoaded', () => {
   const form = document.querySelector("form");

   function debounce(callee, delay){
      let timeoutVar;
      return function(...args){
         clearTimeout(timeoutVar)
         timeoutVar = setTimeout(() => { callee.apply(this, args); }, delay);
      }
   }

   // handle highlighting: append selected text into the next answer input
   function recordHighlightOnParagraph(p){
      p.addEventListener('mouseup', () => {
         const selection = window.getSelection().toString().trim();
         if (!selection) return;
         // find the first form control (INPUT, SELECT, or TEXTAREA) among following siblings
         let sibling = p.nextElementSibling;
         let firstControl = null;
         while (sibling) {
            const tag = sibling.tagName;
            if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') { firstControl = sibling; break; }
            sibling = sibling.nextElementSibling;
         }
         if (!firstControl) return;
         // if the first control is a SELECT, do not apply highlight behavior
         if (firstControl.tagName === 'SELECT') return;
         // otherwise expect an INPUT-like element and append the selection
         const input = firstControl;
         const sep = input.value === '' ? '' : ' ';
         input.value = input.value + sep + selection;
         input.dispatchEvent(new Event('change'));
         window.getSelection().removeAllRanges();
      });
   }

   // Auto-save: append timestamped snapshot into corresponding log field
   function attachAutoSaveToAnswer(input){
      const m = input.name && input.name.match(/answers-(\d+)/);
      const idx = m ? m[1] : null;
      const log = idx !== null ? document.querySelector(`input[name='answer_logs-${idx}']`) : null;
      if (!log) return;

      const save = debounce(() => {
         const currentTime = new Date().toLocaleString();
         // append snapshot
         log.value += `${currentTime} : ${input.value};`;
      }, 5000);

      input.addEventListener('input', save);
   }

   // Auto-save for select controls: record selected option text into the log when changed
   function attachAutoSaveToSelect(select){
      const m = select.name && select.name.match(/answers-(\d+)/);
      const idx = m ? m[1] : null;
      const log = idx !== null ? document.querySelector(`input[name='answer_logs-${idx}']`) : null;
      if (!log) return;

      const save = function(){
         const currentTime = new Date().toLocaleString();
         const text = select.options[select.selectedIndex] ? select.options[select.selectedIndex].text : select.value;
         log.value += `${currentTime} : ${text};`;
      };

      select.addEventListener('change', save);
   }

   // wire up all answer inputs and corresponding paragraphs
   const answerInputs = document.querySelectorAll("input[name^='answers']");
   answerInputs.forEach((input) => { attachAutoSaveToAnswer(input); });
   const answerSelects = document.querySelectorAll("select[name^='answers']");
   answerSelects.forEach((s) => { attachAutoSaveToSelect(s); });

   const errorParas = document.querySelectorAll('p.erroneousAnswer');
   errorParas.forEach((p) => recordHighlightOnParagraph(p));

});

// placeholder helpers (UI actions handled in DOMContentLoaded block)
function loadQuestions(){}
function submitAnswers(){}
function getErrorInput(){return []}
function checkErrorAnswers(errorAnswers){}
