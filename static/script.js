document.addEventListener('DOMContentLoaded', function() {
    const uploadBtn = document.getElementById('upload-btn');
    const pdfFilesInput = document.getElementById('pdf_files');
    const resultText = document.getElementById('result-text');
    const loader = document.getElementById('loader');
    const questionPapersRadio = document.getElementById('question_papers');
    const testPapersRadio = document.getElementById('test_papers');
    const questionPapersDesc = document.getElementById('question_papers_desc');
    const testPapersDesc = document.getElementById('test_papers_desc');
    
    // Toggle analysis description based on selection
    questionPapersRadio.addEventListener('change', function() {
        if (this.checked) {
            questionPapersDesc.style.display = 'block';
            testPapersDesc.style.display = 'none';
        }
    });
    
    testPapersRadio.addEventListener('change', function() {
        if (this.checked) {
            questionPapersDesc.style.display = 'none';
            testPapersDesc.style.display = 'block';
        }
    });
    
    // Handle file drop
    const dropContainer = document.getElementById('dropcontainer');
    
    dropContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropContainer.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
        dropContainer.style.borderColor = 'rgba(52, 152, 219, 0.5)';
    });
    
    dropContainer.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropContainer.style.backgroundColor = '#f0f8ff';
        dropContainer.style.borderColor = '#3498db';
    });
    
    dropContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        dropContainer.style.backgroundColor = '#f0f8ff';
        dropContainer.style.borderColor = '#3498db';
        
        if (e.dataTransfer.files.length) {
            pdfFilesInput.files = e.dataTransfer.files;
            updateFileCounter();
        }
    });
    
    // Show selected file count
    function updateFileCounter() {
        const fileCount = pdfFilesInput.files.length;
        if (fileCount > 0) {
            dropContainer.querySelector('.drop-title').textContent = `${fileCount} file${fileCount !== 1 ? 's' : ''} selected`;
        } else {
            dropContainer.querySelector('.drop-title').textContent = 'Drop PDF files here';
        }
    }
    
    pdfFilesInput.addEventListener('change', updateFileCounter);
    
    // Handle upload and analysis
    uploadBtn.addEventListener('click', function() {
        if (!pdfFilesInput.files || pdfFilesInput.files.length === 0) {
            alert('Please select at least one PDF file to analyze.');
            return;
        }
        
        // Get the selected analysis type
        const analysisType = document.querySelector('input[name="analysis_type"]:checked').value;
        
        // Create FormData and append files
        const formData = new FormData();
        for (let i = 0; i < pdfFilesInput.files.length; i++) {
            formData.append('pdf_files[]', pdfFilesInput.files[i]);
        }
        formData.append('analysis_type', analysisType);
        
        // Show loader
        resultText.innerHTML = '';
        loader.style.display = 'block';
        
        // Send the files to the server
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            loader.style.display = 'none';
            
            // Display the result
            resultText.innerHTML = data.result;
        })
        .catch(error => {
            // Hide loader
            loader.style.display = 'none';
            
            console.error('Error:', error);
            resultText.innerHTML = '<p>An error occurred during analysis. Please try again.</p>';
        });
    });
});