document.addEventListener('DOMContentLoaded', function() {
    // File upload functionality
    const fileInput = document.getElementById('resume-upload');
    const browseButton = document.getElementById('browse-button');
    const uploadButton = document.getElementById('upload-button');
    const fileNameDisplay = document.getElementById('file-name');
    const fileUploadBox = document.querySelector('.file-upload-box');
    
    console.log('DOM loaded, elements found:', {
        fileInput: !!fileInput, 
        browseButton: !!browseButton,
        uploadButton: !!uploadButton,
        fileNameDisplay: !!fileNameDisplay,
        fileUploadBox: !!fileUploadBox
    });
    if (browseButton && fileInput) {
        // Click browse button to trigger file input
        browseButton.addEventListener('click', function(e) {
            console.log('Browse button clicked');
            e.preventDefault();
            fileInput.click();
        });
        // Handle file selection
        fileInput.addEventListener('change', function() {
            console.log('File input changed');
            handleFileSelection(this);
        });
        // Drag and drop functionality
        if (fileUploadBox) {
            // Prevent default drag behaviors
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                fileUploadBox.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            });
            // Highlight drop area when item is dragged over it
            ['dragenter', 'dragover'].forEach(eventName => {
                fileUploadBox.addEventListener(eventName, highlight, false);
            });
            ['dragleave', 'drop'].forEach(eventName => {
                fileUploadBox.addEventListener(eventName, unhighlight, false);
            });
            // Handle dropped files
            fileUploadBox.addEventListener('drop', handleDrop, false);
            
            // Make entire upload box clickable
            fileUploadBox.addEventListener('click', function(e) {
                if (e.target !== browseButton && !browseButton.contains(e.target)) {
                    console.log('Upload box clicked');
                    fileInput.click();
                }
            });
        }
    }
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    function highlight() {
        fileUploadBox.classList.add('highlight');
    }
    function unhighlight() {
        fileUploadBox.classList.remove('highlight');
    }
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFileSelection(fileInput);
    }
    function handleFileSelection(input) {
        console.log('Handling file selection:', input.files);
        if (input.files && input.files[0]) {
            const file = input.files[0];
            console.log('File selected:', file.name, 'Type:', file.type);
            
            // Accept PDF files regardless of what the browser reports as type
            // Some browsers might report PDF files with different MIME types
            const fileName = file.name.toLowerCase();
            if (!fileName.endsWith('.pdf')) {
                alert('Please select a PDF file');
                input.value = '';
                return;
            }
            
            // Display file name and enable upload button
            fileNameDisplay.textContent = file.name;
            fileNameDisplay.classList.remove('d-none');
            uploadButton.disabled = false;
            
            // Add success class to upload box
            fileUploadBox.classList.add('file-selected');
            
            console.log('File accepted, upload enabled');
        } else {
            // Reset if no file is selected
            console.log('No file selected or file selection cancelled');
            fileNameDisplay.textContent = '';
            fileNameDisplay.classList.add('d-none');
            uploadButton.disabled = true;
            fileUploadBox.classList.remove('file-selected');
        }
    }
    // Show spinner when form is submitted
    const uploadForm = document.querySelector('.upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            uploadButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            uploadButton.disabled = true;
        });
    }
});
