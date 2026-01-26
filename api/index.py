from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database of Emission Factors
EMISSION_FACTORS = {
    "travel": 0.57,
    "transport": 0.42,
    "food": 0.35,
    "retail": 0.18,
    "digital": 0.02
}

# Important: The route must match the URL structure /api/calculate
@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        category = data.get('category', 'retail')
        amount = float(data.get('amount', 0))
        merchant = data.get('merchant', 'Unknown')

        factor = EMISSION_FACTORS.get(category, 0.2)
        co2_impact = round(amount * factor, 2)

        insight = f"Purchase at {merchant} processed."
        if category == "travel" and co2_impact > 100:
            insight = "High carbon event. Consider rail alternatives."
        elif category == "food" and co2_impact > 20:
            insight = "Sourcing local produce reduces footprint by 30%."
        elif category == "digital":
            insight = "Excellent. Minimal carbon footprint."

        return jsonify({
            "status": "success",
            "co2": co2_impact,
            "insight": insight
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel requires the app to be exposed as 'app'