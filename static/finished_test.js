

document.addEventListener("DOMContentLoaded", function() {
	const downloadButton = document.getElementById('DownloadButton');
	const test = document.getElementById('test');
	const toggle_button = document.getElementById('toggle_button')
	const toggle_bar = document.getElementById('boundToggle')
	const choiceAnswer = document.querySelectorAll('.choiceAnswer')
	const writtenAnswer = document.querySelectorAll('.writtenAnswer')
	const noAnswer = document.querySelectorAll('.noAnswer')

	console.log(test);
	console.log(downloadButton)

	borderToggleOption();

	downloadButton.addEventListener('click', function(){html2canvas(test).then(function(canvas){

		print(test)
	})})


	toggle_bar.addEventListener('click', function(){
		borderToggleOption();
	})

	function borderToggleOption() {
		const currentTransform = window.getComputedStyle(toggle_button).transform;

		if (currentTransform === "none") {
			toggle_button.style.transform = "translateX(0px)"; // Move right
		}
		// Toggle the position of the button
		if (toggle_button.style.transform === "translateX(0px)") {
			toggle_button.style.transform = "translateX(25px)";
			for(let i = 0; i < writtenAnswer.length; i++){
				writtenAnswer[i].style.display = 'none'
				noAnswer[i].style.display = ''
			}
			for(let i = 0; i < choiceAnswer.length; i++){
				choiceAnswer[i].style.color = '#000000'
			}
			downloadButton.innerText = "Download Test"
		} 
		else {
			toggle_button.style.transform = "translateX(0px)";
			for(let i = 0; i < writtenAnswer.length; i++){
				writtenAnswer[i].style.display = ''
				noAnswer[i].style.display = 'none'
			}
			for(let i = 0; i < choiceAnswer.length; i++){
				choiceAnswer[i].style.color = ''
			}
			downloadButton.innerText = "Download Answer Key"
		}
	}

})

