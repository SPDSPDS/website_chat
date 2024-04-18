// script.js
document.addEventListener('DOMContentLoaded', function () {
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const responseDiv = document.getElementById('response');

    sendButton.addEventListener('click', async () => {
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
                responseDiv.innerHTML = `Response from server: ${data.result}`;
            } catch (error) {
                responseDiv.innerHTML = `Error: ${error.message}`;
            }
        });

    });
});
