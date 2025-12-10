from flask import Flask, request, jsonify
import json
import os
import folium

app = Flask(__name__)

# ---- PATH RULES FILE ----
RULES_PATH = os.path.join(os.path.dirname(__file__), "rules", "rules.json")

# ---- LOAD RULES ----
def load_rules():
    if os.path.exists(RULES_PATH):
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

RULES = load_rules()

# ---- RECLASS FUNCTION ----
def convert_to_transaction(year, continent, mass):

    # YEAR → PERIOD
    try:
        y = int(year)
    except:
        y = None

    if y is None:
        period = "period_unknown"
    elif y < 1900:
        period = "period_pre_1900"
    elif y < 1950:
        period = "period_1900_1949"
    elif y < 2000:
        period = "period_1950_1999"
    else:
        period = "period_2000_2024"

    # MASS → BUCKET
    try:
        m = float(mass)
    except:
        m = None

    if m is None:
        mass_cat = "mass_unknown"
    elif m < 50:
        mass_cat = "mass_very_small"
    elif m < 500:
        mass_cat = "mass_small"
    elif m < 5000:
        mass_cat = "mass_medium"
    else:
        mass_cat = "mass_large"

    # CONTINENT TOKEN
    token_continent = f"continent_{continent}" if continent else "continent_unknown"

    return [token_continent, period, mass_cat]


# ---- MATCH RULES ----
def match_rules(transaction, rules):
    tset = set(transaction)
    matches = []
    for r in rules:
        antecedent = set(r.get("antecedent", []))
        if antecedent <= tset:  # subset
            matches.append(r)
    return matches

# ---- SELECT BEST RULE ----
def choose_best(matches):
    if not matches:
        return None
    sorted_rules = sorted(
        matches,
        key=lambda r: (r.get("confidence", 0), r.get("lift", 0)),
        reverse=True
    )
    return sorted_rules[0], sorted_rules[:3]


# ---- GENERATE MAP ----
def generate_map(points):
    if not points:
        return ""

    lat0 = points[0]["lat"]
    lon0 = points[0]["lon"]

    m = folium.Map(location=[lat0, lon0], zoom_start=4)

    for p in points:
        folium.Marker([p["lat"], p["lon"]], popup=p.get("name","")).add_to(m)

    return m._repr_html_()


# ---- API ROUTE ----
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    year = data.get("year")
    continent = data.get("continent")
    mass = data.get("mass")

    transaction = convert_to_transaction(year, continent, mass)

    matches = match_rules(transaction, RULES)

    if not matches:
        return jsonify({
            "pred_type": None,
            "confidence": 0,
            "lift": 0,
            "top3": [],
            "proof_points": [],
            "map_html": ""
        })

    best, top3 = choose_best(matches)

    # type extraction
    typ = best["consequent"][0].replace("type_", "") \
          if best.get("consequent") else "unknown"

    # proof points
    proof = best.get("examples", [])

    # make folium map
    map_html = generate_map(proof)

    # format top3
    top3_fmt = []
    for r in top3:
        c = r["consequent"][0].replace("type_", "")
        top3_fmt.append([c, r["confidence"]])

    return jsonify({
        "pred_type": typ,
        "confidence": best.get("confidence", 0),
        "lift": best.get("lift", 0),
        "top3": top3_fmt,
        "proof_points": proof,
        "map_html": map_html
    })


if __name__ == "__main__":
    app.run(debug=True)
