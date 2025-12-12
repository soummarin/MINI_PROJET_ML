import sys, os, pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '../training'))
from REGLES import process_user_selection

app = Flask(__name__)
CORS(app)

# Dataset
dataset_path = os.path.join(os.path.dirname(__file__), '../data/meteorites_final_rebalanced.csv')
df = pd.read_csv(dataset_path)

# Règles
rules_path = os.path.join(os.path.dirname(__file__), 'rules.pkl')
with open(rules_path, 'rb') as f:
    rules = pickle.load(f)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        sel = {
            "years": data.get("years"),
            "mass": data.get("mass"),
            "continents": data.get("continents")
        }
        result = process_user_selection(sel, rules, df)
        
        # Construire la réponse de base
        response = {
            "top_type": result["top_type"],
            "probability": result["probability"],
            "names": result["names"],
            "countries": result["countries"],
            "sample_years": result["sample_years"]
        }
        
        # N'ajouter les prédictions que si elles existent
        if "predicted_years" in result:
            response["predicted_years"] = result["predicted_years"]
        if "predicted_mass" in result:
            response["predicted_mass"] = result["predicted_mass"]
        if "predicted_continent" in result:
            response["predicted_continent"] = result["predicted_continent"]
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)