from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# CORS is required to let your HTML (hosted anywhere) talk to this Python script
CORS(app)

# Database of Emission Factors (kg CO2 per $)
# Real-world apps would use an API like Climatiq here
EMISSION_FACTORS = {
    "travel": 0.57,     # High impact (Flights)
    "transport": 0.42,  # Medium-High (Uber/Taxi)
    "food": 0.35,       # Medium (Groceries/Restaurants)
    "retail": 0.18,     # Low-Medium (Clothes/Goods)
    "digital": 0.02     # Low (Software/Subscriptions)
}

@app.route('/')
def home():
    return "GREENIQ Neural Engine is Online."

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        category = data.get('category', 'retail')
        amount = float(data.get('amount', 0))
        merchant = data.get('merchant', 'Unknown')

        # 1. Calculate Logic
        factor = EMISSION_FACTORS.get(category, 0.2)
        co2_impact = round(amount * factor, 2)

        # 2. AI Insight Generation (Rule-based for demo)
        insight = f"Purchase at {merchant} processed."
        if category == "travel" and co2_impact > 100:
            insight = "High carbon event detected. Consider rail alternatives for trips under 400km."
        elif category == "food" and co2_impact > 20:
            insight = "Sourcing locally grown produce can reduce this footprint by up to 30%."
        elif category == "digital":
            insight = "Excellent. Digital services have a minimal carbon footprint."
        else:
            insight = "Transaction analyzed successfully. Footprint added to monthly total."

        # 3. Return Response to HTML
        return jsonify({
            "status": "success",
            "co2": co2_impact,
            "insight": insight,
            "factor_used": factor
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)