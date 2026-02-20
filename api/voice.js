/**
 * ECOPAY Voice AI Backend handler (/api/voice)
 * Connects to GitHub Models via the Phi-4-multimodal-instruct model.
 * Handles voice transcriptions and fallback text, returning a reply and a navigation route.
 */

export default async function handler(req, res) {
    // Only allow POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { text } = req.body;
    
    // Check for GitHub token in Vercel environment variables
    const token = process.env.GITHUB_TOKEN; 

    if (!token) {
        console.error("Missing GITHUB_TOKEN environment variable.");
        return res.status(500).json({ error: 'GitHub API token not configured.' });
    }

    try {
        const response = await fetch('https://models.inference.ai.azure.com/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                model: "Phi-4-multimodal-instruct",
                messages: [
                    {
                        role: "system",
                        content: `You are ECOPAY Voice AI. Your job is to answer the user briefly and politely in 1 or 2 spoken sentences.
                        Crucially, if the user implies they want to see a specific dashboard module, identify it and map it to a "navigate" URL. 
                        
                        Routing Guidelines:
                        - If user asks about Carbon Scoring, Footprint, or Module 1 -> set "navigate" to "module1.html".
                        - If Offset Marketplace, Buying Offsets, or Module 2 -> set "navigate" to "module_02_marketplace.html".
                        - If Global Accord, Compliance, Policies, or Module 3 -> set "navigate" to "module3.html".
                        - If Sustainable Commerce, Shop, or Module 4 -> set "navigate" to "module4.html".
                        - If no specific module is requested, set "navigate" to "null".
                        
                        You MUST return your response strictly as a JSON object, with absolutely no surrounding markdown formatting or text.
                        Example format: {"reply": "Opening the carbon scoring engine for you now.", "navigate": "module1.html"}`
                    },
                    {
                        role: "user",
                        content: text
                    }
                ],
                temperature: 0.1, // Low temperature for highly consistent JSON output
                max_tokens: 150
            })
        });

        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        const aiMessage = data.choices[0].message.content;
        
        // Clean the response in case the model wraps the JSON in markdown blocks (e.g. ```json ... ```)
        const cleanedMessage = aiMessage.replace(/```json/g, '').replace(/```/g, '').trim();
        const parsedData = JSON.parse(cleanedMessage);

        return res.status(200).json(parsedData);
        
    } catch (error) {
        console.error('Voice AI Backend Error:', error);
        return res.status(500).json({ 
            reply: 'Sorry, I encountered an error connecting to the AI model. Please try again later.', 
            navigate: "null" 
        });
    }
}