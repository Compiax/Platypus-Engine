/**
start.js
Split Bill Project

Run this script as:

node start.js image1filename.jpg image2filename.jpg image3filename.jpg

It should then output the textual representation of the images passed to it
in the same order that the images appear in the argument list.

The ocr.py file must be in the same directory as this file
Both Tesseract and the Python wrapper (pytesseract) must be 
installed for the Python script to execute.
*/

var filenames = [];

/* 
Save the names of the images into an array, 
these names are given as commandline arguments 
*/
process.argv.forEach(function(argument){
	if(argument != process.argv[0] && argument != process.argv[1]) {
		filenames.push(argument);
	}
})

/*
The "spawn" variable is a handle to the python process
within which we will run the tesseract image recognition
*/
var spawn = require('child_process').spawn,
	py = spawn('python',['ocr.py']),
	recognisedText = "";

/*
We save the output from the python script into the recognisedText variable

@todo The variable will eventually become a JSON object
*/
py.stdout.on('data',function(filenames) {
	recognisedText += filenames.toString();
});

/*
When the python script STOPS "outputting" this function will execute

@todo the value of the recognisedText variable needs to be sent back to the 
process that originally called the start.js script (will most likely be
something on the interface side)
*/
py.stdout.on('end',function() {
	console.log('Characters recognised: ',recognisedText);
});

/*
We pass the array of image names to the python script here
*/
py.stdin.write(JSON.stringify(filenames));
py.stdin.end();
