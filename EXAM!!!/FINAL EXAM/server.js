const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const { PythonShell } = require('python-shell');

const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());

// Route to handle Cohere API requests
app.post('/api/cohere', async (req, res) => {
    const { prompt } = req.body;

    try {
        const response = await axios.post('https://api.cohere.ai/v1/generate', {
            prompt,
            max_tokens: 100,
            temperature: 0.7,
        }, {
            headers: {
                'Authorization': `Bearer ABqF8Z0I1Yxjf68lt7V9UEAMcBHlzEgNIjgIZWVF`,
                'Content-Type': 'application/json',
            },
        });

        const reply = response.data.generations[0].text.trim();
        res.json({ reply });
    } catch (error) {
        console.error('Error communicating with Cohere:', error.message);
        res.status(500).json({ error: 'Failed to connect to Cohere API.' });
    }
});

// Route to execute Python code
app.post('/api/run-code', (req, res) => {
    const { code } = req.body;

    PythonShell.runString(code, null, (err, output) => {
        if (err) {
            console.error('Error executing Python code:', err.message);
            return res.status(500).json({ error: err.message });
        }
        res.json({ output: output.join('\n') });
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
