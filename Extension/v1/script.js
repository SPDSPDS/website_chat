// script.js
document.addEventListener('DOMContentLoaded', function () {
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const summarizeButton = document.getElementById('summarizeButton');
    const responseDiv = document.getElementById('response');

    // Add event listener for the button
    document.getElementById('pdfButton').addEventListener('click', function() {
        // Trigger file input click event
        document.getElementById('pdfFileInput').click();
    });

    // Add event listener for file input change event
    document.getElementById('pdfFileInput').addEventListener('change', function() {
        // Get selected file
        const file = this.files[0];
        if (file) {
            // Process the selected file here or send it to the server
            console.log('Selected PDF file:', file.name);
            // You can send the file to the server using XMLHttpRequest, Fetch API, etc.
        }
    });

    sendButton.addEventListener('click', async () => {
        responseDiv.innerHTML = "Fetching response..."
        const textToSend = userInput.value;

        // Query the active tab in the current window
        chrome.tabs.query({ active: true, currentWindow: true }, async function (tabs) {
            // Since only one tab should be active and in the current window at once,
            // the returned variable should only have one entry.
            const activeTab = tabs[0];
            const tabUrl = activeTab.url;

            try {
                // Send the text to localhost server (adjust the URL as needed)
                const response = await fetch('http://localhost:8000', {
                    method: 'POST',
                    body: JSON.stringify({ url:tabUrl, prompt: textToSend }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
    
                const data = await response.json();
                responseDiv.innerHTML = `${data.result}`;
            } catch (error) {
                responseDiv.innerHTML = `Error: ${error.message}`;
            }
        });

    });

    summarizeButton.addEventListener('click', async () => {
        responseDiv.innerHTML = "Fetching response..."
        const textToSend = "Summarize";

        // Query the active tab in the current window
        chrome.tabs.query({ active: true, currentWindow: true }, async function (tabs) {
            // Since only one tab should be active and in the current window at once,
            // the returned variable should only have one entry.
            const activeTab = tabs[0];
            const tabUrl = activeTab.url;

            try {
                // Send the text to localhost server (adjust the URL as needed)
                const response = await fetch('http://localhost:8000', {
                    method: 'POST',
                    body: JSON.stringify({ url:tabUrl, prompt: textToSend }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
    
                const data = await response.json();
                responseDiv.innerHTML = `${data.result}`;
            } catch (error) {
                responseDiv.innerHTML = `Error: ${error.message}`;
            }
        });

    });
});
