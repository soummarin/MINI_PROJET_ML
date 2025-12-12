import requests

url = "http://127.0.0.1:5001/predict"

# Format recommandé pour les intervalles d'années: [start, end]
data =  {"years": None, "mass": ["1-10g"], "continents": None}
 
response = requests.post(url, json=data)
print(response.json())