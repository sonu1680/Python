const express = require('express');
const fetch = require('node-fetch');

const app = express();
const port = process.env.PORT || 3000;

app.get('/portfolio', async (req, res) => {
    const year = req.query.year;

    if (!year) {
        return res.status(400).send('Year parameter is required');
    }

    try {
        const response = await fetch(`https://${process.env.VERCEL_URL}/api/portfolio_management.py?year=${year}`);
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error(`Error fetching Python function: ${error.message}`);
        res.status(500).send(`Error fetching Python function: ${error.message}`);
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
