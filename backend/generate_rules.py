# generate_rules_complete.py
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import pickle
import os

# -----------------------------
# Charger dataset
# -----------------------------
dataset_path = os.path.join('..', 'data', 'meteorites_final.csv')
df = pd.read_csv(dataset_path)

# -----------------------------
# Colonnes à utiliser pour apriori
# -----------------------------
columns = ["year_period", "mass_bin", "continent", "recclass_clean"]
df_small = df[columns]

# -----------------------------
# Encodage one-hot
# -----------------------------
df_encoded = pd.get_dummies(df_small).astype(bool)

# -----------------------------
# Calculer itemsets fréquents
# -----------------------------
# Support minimal raisonnable pour éviter règles trop rares
frequent_itemsets = apriori(df_encoded, min_support=0.005, use_colnames=True)

# -----------------------------
# Générer règles d'association
# -----------------------------
# min_threshold peut être ajusté pour garder plus ou moins de règles
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.2)

# -----------------------------
# Ajouter colonnes utiles pour filtrage
# -----------------------------
# Convertir antecedents et consequents en set de chaînes pour plus tard
rules['antecedents'] = rules['antecedents'].apply(lambda x: set(x))
rules['consequents'] = rules['consequents'].apply(lambda x: set(x))

# -----------------------------
# Sauvegarder règles
# -----------------------------
rules_path = os.path.join(os.path.dirname(__file__), 'rules.pkl')
with open(rules_path, 'wb') as f:
    pickle.dump(rules, f)

print("Fichier rules.pkl créé avec succès !")
