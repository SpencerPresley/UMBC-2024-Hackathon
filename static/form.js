
document.addEventListener('DOMContentLoaded', function() {
const form = document.getElementById('form');
const loading = document.getElementById('loading');

console.log(form)
loading.style.display = 'none';
form.addEventListener('submit', function(event){
    event.preventDefault(); // Prevent the default form submission
    loading.style.display = ''; // Show the loading indicator
    console.log('triggered')
    //display: none;
    // Optionally, you can submit the form here after a short delay
     setTimeout(() => {
         form.submit(); // Submit the form after displaying loading
     }, 100); // Adjust the timeout as necessary
})
})
