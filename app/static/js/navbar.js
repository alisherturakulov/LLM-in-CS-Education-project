// Navbar script for webpages

document.addEventListener("DOMContentLoaded", ()=>{
const navbarInputs = document.querySelectorAll("nav input.inline");
const navbarLinks = document.querySelectorAll("nav a");
let linkIndex = 0;
navbarInputs.forEach((input)=>{
    
    input.addEventListener("input", ()=>{
        console.log(input.value)
        const link_tag = input.previousElementSibling;
        let link_text = link_tag.href;
        let link_page = link_text.substring(0, link_text.lastIndexOf("/")+1);
        let newLink = link_page + input.value;
        console.log(newLink);
        link_tag.href = newLink;
        console.log(link_tag.href);
    });
});
    
});

