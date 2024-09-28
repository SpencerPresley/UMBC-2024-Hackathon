document.addEventListener("DOMContentLoaded", function() {
	const downloadButton = document.getElementById('DownloadButton');
	const test = document.getElementById('test');
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


	
})