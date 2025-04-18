**Previous Paper Analyzer (PPA)**
=====================================

**Overview**
-----------

The Previous Paper Analyzer (PPA) is a web-based application that analyzes previous question papers and provides insights on the most frequently asked questions and most important questions. The application uses the Gemini 1.5 Pro AI model to analyze the question papers and generate a report in HTML format.

**Features**
------------

* Upload up to 4 PDF files of previous question papers
* Analyze the question papers using the Gemini 1.5 Pro AI model
* Generate a report in HTML format that includes the most frequently asked questions and most important questions
* Display the report in a user-friendly format

**Technical Details**
--------------------

* The application is built using Flask, a Python web framework
* The Gemini 1.5 Pro AI model is used for analyzing the question papers
* The application uses PyPDF2 to extract text from the PDF files
* The application uses JavaScript and HTML/CSS for the user interface

**How to Use**
--------------

1. Upload up to 4 PDF files of previous question papers by dragging and dropping them into the upload section or by selecting them using the file input field.
2. Click the "Upload and Analyze" button to start the analysis process.
3. The application will generate a report in HTML format and display it in the result section.

**Requirements**
---------------

* Python 3.x
* Flask
* PyPDF2
* Gemini 1.5 Pro AI model
* JavaScript and HTML/CSS for the user interface

**Acknowledgments**
----------------

* The Gemini 1.5 Pro AI model is used under the terms of the Google Generative AI API.

**Code Structure**
-----------------

* The application is divided into three main components: the Flask backend, the JavaScript frontend, and the HTML templates.
* The Flask backend handles the file uploads, analyzes the question papers using the Gemini 1.5 Pro AI model, and generates the report in HTML format.
* The JavaScript frontend handles the user interface and interacts with the Flask backend using AJAX requests.
* The HTML templates are used to render the user interface and display the report.