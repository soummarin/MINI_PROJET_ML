import requests

url = "http://127.0.0.1:5000/predict"
data = {"years": [2000], "mass": None, "continents": ['Asia']}

 
response = requests.post(url, json=data)
print(response.json())