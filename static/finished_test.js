const downloadButton = document.getElementById('DownloadButton');
const test = document.getElementById('test');
const toggle_bar = document.getElementById

document.addEventListener("DOMContentLoaded", function() {
	
	console.log(test);
	console.log(downloadButton)

	downloadButton.addEventListener('click', function(){html2canvas(test).then(function(canvas){

		console.log(canvas)
		const imgData = canvas.toDataURL("image/png");
		print(imgData)
		let pdf = new jsPDF('p', 'pt', [canvas.width, canvas.height]);  // Create a new PDF document with the canvas dimensions as page size

		// Calculate the aspect ratio of the canvas content
		let canvasAspectRatio = canvas.width / canvas.height;

		// Calculate the aspect ratio of the PDF page
		let pdfWidth = pdf.internal.pageSize.getWidth();
		let pdfHeight = pdf.internal.pageSize.getHeight();
		let pdfAspectRatio = pdfWidth / pdfHeight;

		/*// Default image dimensions with assumption that the canvas is taller than PDF page
		let imgWidth = pdfHeight * canvasAspectRatio;
		let imgHeight = pdfHeight;*/

		// Change size of the image in the PDF using the aspect ratios if canvas is wider than PDF page
		if (canvasAspectRatio > pdfAspectRatio) {
			imgWidth = pdfWidth;
			imgHeight = pdfWidth / canvasAspectRatio;
		} 
	

		pdf.addImage(imgData, 'PNG', offsetX, offsetY, imgWidth, imgHeight);

		pdf.save("Test.pdf");  // Save the PDF
	})})


	toggle_bar.addEventListener(function(){
		borderToggleOption();
	})

	

})

function borderToggleOption() {
	// Toggle the position of the button
	if (borderToggle.style.transform === "translateX(0px)") {
		borderToggle.style.transform = "translateX(25px)";
	} 
	else {
		borderToggle.style.transform = "translateX(0px)";
	}
}