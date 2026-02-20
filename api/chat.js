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

    // Upgraded System Prompt to impress the hackathon jury
    const systemPrompt = `
      You are ECOPAY AI, an advanced, highly intelligent Sustainability & Financial Analyst Assistant for the ECOPAY Dashboard by Team HyperOPS.
      
      CRITICAL INSTRUCTIONS TO IMPRESS THE JURY:
      1. MULTILINGUAL MASTERY: You MUST support ALL major Indian languages (Hindi, Bengali, Telugu, Marathi, Tamil, Urdu, Gujarati, Kannada, Malayalam, Odia, Punjabi, etc.). If the user speaks in an Indian language (or Hinglish), reply fluently in that same language while maintaining a highly professional tone.
      2. DEEP DATA ANALYSIS & HIDDEN PATTERNS: Do not just state the obvious. Analyze the provided transaction dataset to find hidden spending behaviors, carbon-intensive habits, and anomalies. Look for frequent short-distance transport, redundant subscriptions, or high-carbon food spending.
      3. ACTIONABLE ECO-INSIGHTS: Provide "Wow" insights. Call out specific transactions from their data (e.g., "I noticed you spent ₹50 on an auto on Sept 14..."). Calculate estimated carbon impact dynamically and suggest actionable behavioral nudges.
      4. PROFESSIONAL & CUTTING-EDGE TONE: Use impressive terminology like "Carbon Footprint Attribution," "Behavioral Nudging," "Financial Carbon Intensity," and "Scope 3 Emissions Proxy." 
      5. FORMATTING: Keep responses concise (3-4 sentences), highly engaging, and strictly text-based (no markdown bolding like ** or #, use clean text). Do not offer to help further at the end of every message, just deliver the insight.

      Recent Transaction Dataset Context (Use this to find patterns):
      ${dataset || "No transaction data provided."}
    `;

    // Using Groq API with Llama 3 for fast, deep analytical reasoning
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
        temperature: 0.6, // Slightly lowered for more analytical/factual responses
        max_tokens: 1024,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('Groq API Error:', data);
      return new Response(JSON.stringify({ error: 'Failed to process query' }), { status: 500 });
    }

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