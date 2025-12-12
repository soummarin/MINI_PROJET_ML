# generate_rules_complete.py
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import pickle
import os

# -----------------------------
# Charger dataset
# -----------------------------
dataset_path = os.path.join('..', 'data', 'meteorites_final_rebalanced.csv')
df = pd.read_csv(dataset_path)

print(f"Dataset chargé : {len(df)} lignes")

# -----------------------------
# Colonnes à utiliser pour apriori
# -----------------------------
columns = ["year_period", "mass_bin", "continent", "recclass_clean"]
df_small = df[columns].dropna()  # Supprimer les lignes avec valeurs manquantes

print(f"Données après nettoyage : {len(df_small)} lignes")
print(f"Valeurs uniques par colonne :")
for col in columns:
    print(f"  - {col}: {df_small[col].nunique()} valeurs")

# -----------------------------
# MODIFICATION 1: Encodage standard
# -----------------------------
df_encoded = pd.get_dummies(df_small).astype(bool)

print(f"Colonnes encodées : {len(df_encoded.columns)}")

# -----------------------------
# MODIFICATION 2: Support ULTRA-BAS pour MAX de règles
# -----------------------------
# Support à 0.0001 pour capturer TOUTES les règles possibles
frequent_itemsets = apriori(df_encoded, min_support=0.0001, use_colnames=True)

print(f"Itemsets fréquents trouvés : {len(frequent_itemsets)}")

# -----------------------------
# MODIFICATION 3: Génération avec CONFIDENCE comme métrique
# -----------------------------
# Utiliser confidence avec seuil à 0.6 pour cibler directement
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)

print(f"Règles générées (confidence ≥ 0.6) : {len(rules)}")

# -----------------------------
# MODIFICATION 4: Filtrage LARGE pour garder TOUT
# -----------------------------
# Garder tout ce qui a confidence ≥ 0.6 ET lift > 1.0
rules = rules[(rules['confidence'] >= 0.6) & (rules['lift'] > 1.0)]

print(f"Règles après filtrage basique : {len(rules)}")

# -----------------------------
# Filtrer pour garder les règles qui prédisent un type
# -----------------------------
def has_type_in_consequents(row):
    return any('recclass_clean_' in str(item) for item in row['consequents'])

type_rules = rules[rules.apply(has_type_in_consequents, axis=1)]
other_rules = rules[~rules.apply(has_type_in_consequents, axis=1)]

print(f"Règles prédisant un type : {len(type_rules)}")
print(f"Autres règles : {len(other_rules)}")

# -----------------------------
# MODIFICATION 5: Équilibrer MAIS garder MAXIMUM
# -----------------------------
# Compter les règles par type
type_to_rules = {}
for idx, row in type_rules.iterrows():
    for item in row['consequents']:
        if 'recclass_clean_' in str(item):
            type_name = str(item).replace('recclass_clean_', '')
            if type_name not in type_to_rules:
                type_to_rules[type_name] = []
            type_to_rules[type_name].append(idx)

print(f"\nTypes avec règles : {len(type_to_rules)}")

# MAX_RULES_PER_TYPE TRÈS ÉLEVÉ
MAX_RULES_PER_TYPE = 500  # TRÈS HAUT pour garder maximum

balanced_indices = []
for type_name, indices in type_to_rules.items():
    if len(indices) <= MAX_RULES_PER_TYPE:
        # Type rare → garder TOUTES ses règles
        balanced_indices.extend(indices)
    else:
        # Type fréquent → garder BEAUCOUP de règles
        type_df = type_rules.loc[indices]
        
        # Trier par confidence (pour avoir moyenne élevée)
        type_df = type_df.sort_values('confidence', ascending=False)
        
        # Garder les MAX_RULES_PER_TYPE meilleures
        best_rules = type_df.head(MAX_RULES_PER_TYPE)
        balanced_indices.extend(best_rules.index.tolist())

balanced_type_rules = type_rules.loc[list(set(balanced_indices))]
print(f"Règles de type après équilibrage : {len(balanced_type_rules)}")

# Pour autres règles, garder aussi BEAUCOUP
# Pas de filtrage supplémentaire
print(f"Autres règles conservées : {len(other_rules)}")

# Concaténer TOUT
rules = pd.concat([balanced_type_rules, other_rules])

print(f"\nTotal règles avant post-traitement : {len(rules)}")
# -----------------------------
# MODIFICATION 6: Post-traitement POUR AUGMENTER CONFIDENCE
# -----------------------------
# Séparer les règles par niveau de confidence
high_conf = rules[rules['confidence'] >= 0.7]  # Très hautes
medium_conf = rules[(rules['confidence'] >= 0.65) & (rules['confidence'] < 0.7)]  # Hautes
good_conf = rules[(rules['confidence'] >= 0.6) & (rules['confidence'] < 0.65)]  # Bonnes

print(f"\n📊 Distribution par confidence :")
print(f"  - ≥ 0.7 : {len(high_conf)} règles")
print(f"  - 0.65-0.7 : {len(medium_conf)} règles")
print(f"  - 0.6-0.65 : {len(good_conf)} règles")

# Stratégie: garder TOUTES les ≥0.7, 
# la plupart des 0.65-0.7 (surtout si bon lift),
# et certaines des 0.6-0.65 (uniquement si excellent lift)

# Pour medium_conf: garder si lift > 1.5
medium_conf = medium_conf[medium_conf['lift'] > 1.5]

# Pour good_conf: garder seulement si lift TRÈS bon (>2.0)
good_conf = good_conf[good_conf['lift'] > 2.0]

# Recombiner
rules = pd.concat([high_conf, medium_conf, good_conf])

print(f"\nRègles après optimisation confidence/lift : {len(rules)}")

# -----------------------------
# Ajouter colonnes utiles pour filtrage
# -----------------------------
rules['antecedents'] = rules['antecedents'].apply(lambda x: set(x))
rules['consequents'] = rules['consequents'].apply(lambda x: set(x))

# -----------------------------
# Statistiques finales DÉTAILLÉES
# -----------------------------
print("\n=== STATISTIQUES DES RÈGLES OPTIMISÉES ===")
print(f"Total règles : {len(rules)}")
print(f"Confidence moyenne : {rules['confidence'].mean():.3f}")
print(f"Lift moyen : {rules['lift'].mean():.3f}")
print(f"Support moyen : {rules['support'].mean():.6f}")

# Distribution détaillée confidence
print(f"\n📊 Distribution exacte confidence :")
for threshold in [0.6, 0.65, 0.7, 0.75, 0.8]:
    count = len(rules[rules['confidence'] >= threshold])
    percentage = (count / len(rules)) * 100 if len(rules) > 0 else 0
    print(f"  - ≥ {threshold} : {count} règles ({percentage:.1f}%)")

# Top types les plus prédits
type_counts = {}
for _, row in balanced_type_rules.iterrows():
    for item in row['consequents']:
        if 'recclass_clean_' in str(item):
            type_name = str(item).replace('recclass_clean_', '')
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

print("\nDistribution des règles par type (top 10) :")
sorted_types = sorted(type_counts.items(), key=lambda x: -x[1])[:10]
for t, c in sorted_types:
    print(f"  - {t}: {c} règles")

# -----------------------------
# Vérifier les règles pour les petites masses
# -----------------------------
small_mass_rules = rules[
    rules['antecedents'].apply(
        lambda x: any('<1g' in str(item) or '1-10g' in str(item) for item in x)
    )
]
print(f"\nRègles pour petites masses (<1g et 1-10g) : {len(small_mass_rules)}")

# -----------------------------
# TOP 10 règles par confidence
# -----------------------------
print(f"\n🏆 TOP 10 RÈGLES PAR CONFIDENCE :")
top_conf = rules.nlargest(10, 'confidence')
for idx, row in top_conf.iterrows():
    ants = ', '.join([str(a) for a in list(row['antecedents'])[:2]])
    cons = ', '.join([str(c) for c in list(row['consequents'])[:2]])
    print(f"\n  🔹 {ants} → {cons}")
    print(f"     Confidence: {row['confidence']:.3f} | Lift: {row['lift']:.2f} | Support: {row['support']:.6f}")

# -----------------------------
# TOP 10 règles par lift
# -----------------------------
print(f"\n🏆 TOP 10 RÈGLES PAR LIFT :")
top_lift = rules.nlargest(10, 'lift')
for idx, row in top_lift.iterrows():
    ants = ', '.join([str(a) for a in list(row['antecedents'])[:2]])
    cons = ', '.join([str(c) for c in list(row['consequents'])[:2]])
    print(f"\n  🔹 {ants} → {cons}")
    print(f"     Lift: {row['lift']:.2f} | Confidence: {row['confidence']:.3f} | Support: {row['support']:.6f}")

# -----------------------------
# Sauvegarder règles
# -----------------------------
rules_path = os.path.join(os.path.dirname(__file__), 'rules.pkl')
with open(rules_path, 'wb') as f:
    pickle.dump(rules, f)
    print(f"\n" + "="*60)
print("✅ Fichier rules.pkl créé avec succès !")
print(f"   📊 TOTAL RÈGLES : {len(rules)}")
print(f"   ✅ CONFIDENCE MOYENNE : {rules['confidence'].mean():.3f}")
print(f"   🎯 LIFT MOYEN : {rules['lift'].mean():.3f}")
print(f"   📈 Support moyen : {rules['support'].mean():.6f}")
print("="*60)