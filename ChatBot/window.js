// Insert your Cohere API Key here
const COHERE_API_KEY = "lXFezUPW929q4VuUMjNyxPKhojSWOGmVAl0FzDbA";

// Elements
const messagesDiv = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Function to display messages
function displayMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = message;
    messageDiv.className = `message ${sender}`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight; // Auto-scroll to bottom
}

// Function to create a collapsible explanation block with a [>_] icon
function createExplanationBlock(code) {
    const icon = document.createElement('div');
    icon.textContent = "[>_]"; // Icon representing the expandable block
    icon.style.display = 'inline-block';
    icon.style.width = '50px';
    icon.style.height = '20px';
    icon.style.lineHeight = '20px';
    icon.style.textAlign = 'center';
    icon.style.cursor = 'pointer';
    icon.style.marginLeft = '10px';
    icon.style.border = '1px solid #ccc';
    icon.style.borderRadius = '4px';
    icon.style.backgroundColor = '#f4f4f4';
    icon.style.fontSize = '12px';

    const explanationBlockDiv = document.createElement('div');
    explanationBlockDiv.textContent = code;
    explanationBlockDiv.style.backgroundColor = '#f4f4f4';
    explanationBlockDiv.style.padding = '8px';
    explanationBlockDiv.style.border = '1px solid #ccc';
    explanationBlockDiv.style.borderRadius = '4px';
    explanationBlockDiv.style.margin = '10px 0';
    explanationBlockDiv.style.display = 'none'; // Initially hidden

    // Toggle visibility on icon click
    icon.addEventListener('click', () => {
        explanationBlockDiv.style.display = explanationBlockDiv.style.display === 'none' ? 'block' : 'none';
    });

    messagesDiv.appendChild(icon);
    messagesDiv.appendChild(explanationBlockDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Function to extract math operations from a query
function extractMathOperation(query) {
    const match = query.match(/(\d+[\s\+\-\*\/\(\)]+[\d\s\+\-\*\/\(\)]+)/);
    return match ? match[0].trim() : null;
}

// Function to handle user input
async function handleUserInput() {
    const userMessage = userInput.value.trim();
    console.log(`User input: ${userMessage}`);
    if (!userMessage) return;

    displayMessage(userMessage, 'user'); // Display user message
    userInput.value = ''; // Clear input

    // Check if query contains a math operation
    const mathOperation = extractMathOperation(userMessage);
    if (mathOperation) {
        console.log(`Math problem detected: ${mathOperation}`);

        // Solve the math problem and generate pseudocode
        try {
            const result = eval(mathOperation); // Evaluate the math problem
            const explanation = `python:\nanswer = ${mathOperation}`; // Python-like pseudocode

            // Display the explanation block behind the [>_] icon
            createExplanationBlock(explanation);

            // Display the result
            displayMessage(`The answer is ${result}. [>_]`, 'bot'); // Natural language response
        } catch (error) {
            console.error("Error evaluating math problem:", error);
            displayMessage(`Error solving the math problem: ${error.message}`, 'bot');
        }
        return;
    }

    // Otherwise, send the input to Cohere for a response
    try {
        console.log("Sending request to Cohere API...");
        const response = await fetch('https://api.cohere.ai/v1/generate', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${COHERE_API_KEY}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: `You are a chatbot. Respond normally to user input. User: ${userMessage}\nBot:`,
                max_tokens: 100,
            }),
        });

        if (!response.ok) {
            console.error(`HTTP Error: ${response.status}`);
            displayMessage(`Error: API request failed with status ${response.status}`, 'bot');
            return;
        }

        const cohereResponse = await response.json();
        const botMessage = cohereResponse.generations[0]?.text.trim() || "No response from Cohere.";
        displayMessage(botMessage, 'bot');
    } catch (error) {
        console.error("Fetch error:", error);
        displayMessage(`Error: ${error.message}`, 'bot');
    }
}

// Event listeners
sendButton.addEventListener('click', handleUserInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleUserInput();
});
