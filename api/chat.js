export const config = {
  runtime: 'edge',
};

export default async function handler(req) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  try {
    const { message, dataset } = await req.json();

    // System prompt defining the ECOPAY AI persona
    const systemPrompt = `
      You are ECOPAY AI, a professional sustainability assistant for the ECOPAY Dashboard by Team HyperOPS.
      
      Your Role:
      - Help users analyze their carbon footprint based on their financial transactions.
      - Keep responses short (2-3 sentences), professional, and encouraging.
      - Answer their queries using the provided recent transaction dataset.
      - Do NOT use markdown formatting symbols like ** or #.

      Recent Transaction Dataset Context:
      ${dataset || "No transaction data provided."}
    `;

    // Using Groq API with OpenAI compatibility and your Groq_new environment variable
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.Groq_new}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: message }
        ],
        temperature: 0.7,
        max_tokens: 1024,
      }),
    });

    const data = await response.json();

    // Error handling for the API response
    if (!response.ok) {
      console.error('Groq API Error:', data);
      return new Response(JSON.stringify({ error: 'Failed to process query' }), { status: 500 });
    }

    // Extract the content from Groq's OpenAI-compatible response structure
    const botResponse = data.choices[0].message.content;

    return new Response(JSON.stringify({ reply: botResponse }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Server Error:', error);
    return new Response(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
  }
}