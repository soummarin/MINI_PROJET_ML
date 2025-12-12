# meteorite_functions.py

import pandas as pd
import numpy as np
import folium
from mlxtend.frequent_patterns import apriori, association_rules

# -----------------------------
# Filtrer les tautologies géographiques
# -----------------------------
def is_geographic_tautology(row):
    """
    Détecte les règles tautologiques comme {continent_X} → {country_X}
    ou {country_X} → {continent_X}
    """
    antecedents = row['antecedents']
    consequents = row['consequents']
    
    has_continent_ant = any('continent_' in str(item) for item in antecedents)
    has_country_cons = any('country_' in str(item) for item in consequents)
    has_country_ant = any('country_' in str(item) for item in antecedents)
    has_continent_cons = any('continent_' in str(item) for item in consequents)
    
    return (has_continent_ant and has_country_cons) or (has_country_ant and has_continent_cons)

# -----------------------------
# Vérifier si règle prédit un type
# -----------------------------
def is_type_prediction_rule(row):
    return any('recclass_clean_' in str(item) for item in row['consequents'])

# -----------------------------
# Filtrer règles selon critères
# -----------------------------
# -----------------------------
# CORRECTION DE LA FONCTION filter_rules
# -----------------------------
def filter_rules(rules, df, years=None, mass_bins=None, continents=None, strict=False):
    """
    CORRECTION: Ne pas utiliser issubset() qui est trop strict
    Cherche les règles qui contiennent AU MOINS UN des critères
    """
    user_criteria = set()

    # Création du mapping année -> période
    YEAR_TO_PERIOD = dict(zip(df['year'], df['year_period']))

    # Années - convertir en format one-hot
    if years:
        # Détecter si c'est une plage [start, end] ou une liste d'années [1990, 1991, 1992]
        if len(years) == 2 and all(isinstance(y, (int, float)) for y in years):
            # C'est probablement une plage [start_year, end_year]
            start_year, end_year = min(years), max(years)
            if end_year - start_year > 1:  # C'est une plage
                for year in df['year'].unique():
                    if start_year <= year <= end_year:
                        period = YEAR_TO_PERIOD.get(year)
                        if period:
                            user_criteria.add(f'year_period_{period}')
            else:  # Ce sont juste deux années individuelles
                for y in years:
                    if y in YEAR_TO_PERIOD:
                        user_criteria.add(f'year_period_{YEAR_TO_PERIOD[y]}')
        else:
            for y in years:
                if isinstance(y, (list, tuple)) and len(y) == 2:
                    # Plage d'années explicite
                    start_year, end_year = y
                    for year in df['year'].unique():
                        if start_year <= year <= end_year:
                            period = YEAR_TO_PERIOD.get(year)
                            if period:
                                user_criteria.add(f'year_period_{period}')
                elif y in YEAR_TO_PERIOD:
                    user_criteria.add(f'year_period_{YEAR_TO_PERIOD[y]}')

    # Mass bins
    if mass_bins:
        for m in mass_bins:
            if isinstance(m, (list, tuple)) and len(m) == 2:
                # Plage de masse: ajouter tous les mass_bins possibles
                user_criteria.update([f'mass_bin_VS', f'mass_bin_S', f'mass_bin_M', 
                                    f'mass_bin_L', f'mass_bin_VL'])
            else:
                user_criteria.add(f'mass_bin_{m}')

    # Continents
    if continents:
        user_criteria.update(f'continent_{c}' for c in continents)

    # CORRECTION PRINCIPALE: ne pas utiliser issubset() mais intersection()
    def match_criteria_corrected(antecedents):
        ant_set = set(str(item) for item in antecedents)
        if not user_criteria:
            return True
        if strict:
            return user_criteria.issubset(ant_set)
        else:
            return len(ant_set.intersection(user_criteria)) > 0

    # Appliquer le filtrage corrigé
    filtered = rules[rules['antecedents'].apply(match_criteria_corrected)]
    
    # Éliminer les tautologies géographiques
    filtered = filtered[~filtered.apply(is_geographic_tautology, axis=1)]
    
    # Prioriser les règles qui prédissent un type
    type_rules = filtered[filtered.apply(is_type_prediction_rule, axis=1)]
    
    # CORRECTION: Si pas de règles de type, prendre quand même d'autres règles
    # mais les trier par confiance
    if not type_rules.empty:
        return type_rules.sort_values('confidence', ascending=False)
    else:
        return filtered.sort_values('confidence', ascending=False)

# -----------------------------
# Obtenir le type le plus probable
# -----------------------------
def get_most_probable_type(filtered_rules, df):
    """
    Calcule le type le plus probable basé sur les règles filtrées.
    Utilise un scoring qui favorise la confidence et le lift.
    """
    type_scores = {}
    type_max_confidence = {}
    type_counts = {}
    
    if not filtered_rules.empty:
        # Trier par confidence * lift pour prioriser les meilleures règles
        sorted_rules = filtered_rules.sort_values(
            by=['confidence', 'lift'], 
            ascending=[False, False]
        )
        
        for _, row in sorted_rules.iterrows():
            for item in row['consequents']:
                if 'recclass_clean_' in item:
                    type_name = item.replace('recclass_clean_', '')
                    
                    # Score = confidence * lift (le support est déjà filtré en amont)
                    score = row['confidence'] * row['lift']
                    type_scores[type_name] = type_scores.get(type_name, 0) + score
                    
                    # Garder la meilleure confidence pour ce type
                    if type_name not in type_max_confidence:
                        type_max_confidence[type_name] = row['confidence']
                    else:
                        type_max_confidence[type_name] = max(type_max_confidence[type_name], row['confidence'])
                    
                    type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    if type_scores:
        # Normaliser les scores pour éviter que les types avec beaucoup de règles dominent
        normalized_scores = {}
        for t in type_scores:
            # Score normalisé = score moyen par règle * boost pour confidence max
            avg_score = type_scores[t] / type_counts[t]
            confidence_boost = type_max_confidence[t]
            normalized_scores[t] = avg_score * (1 + confidence_boost)
        
        top_type = max(normalized_scores, key=normalized_scores.get)
        
        # Probabilité = meilleure confidence pour ce type
        prob = type_max_confidence[top_type]
        
        # Bonus si plusieurs règles confirment
        if type_counts[top_type] >= 3:
            prob = min(prob * 1.1, 0.95)  # Boost de 10% si 3+ règles
        elif type_counts[top_type] >= 5:
            prob = min(prob * 1.15, 0.95)  # Boost de 15% si 5+ règles
            
    else:
        if not df.empty:
            top_type = df['recclass_clean'].value_counts().idxmax()
            prob = df['recclass_clean'].value_counts(normalize=True).max() * 0.6
        else:
            top_type = "Unknown"
            prob = 0.0
    
    # Garantir une probabilité minimale raisonnable si on a des règles
    if type_scores and prob < 0.3:
        prob = 0.3
    
    return top_type, round(prob, 3)





# -----------------------------
# Prédire valeurs manquantes
# -----------------------------
def predict_missing_criteria(df, top_type, user_years=None, user_mass=None, user_continents=None):
    """
    Prédit les critères manquants basés sur le type de météorite.
    Retourne toujours des listes pour la cohérence.
    """
    df_type = df[df['recclass_clean'] == top_type].copy()
    
    # Filtrer par années si fournies
    if user_years:
        years_flat = []
        # Détecter si c'est une plage [start, end]
        if len(user_years) == 2 and all(isinstance(y, (int, float)) for y in user_years):
            start_year, end_year = min(user_years), max(user_years)
            if end_year - start_year > 1:
                years_flat = list(range(int(start_year), int(end_year) + 1))
            else:
                years_flat = [int(y) for y in user_years]
        else:
            for y in user_years:
                if isinstance(y, (list, tuple)) and len(y) == 2:
                    years_flat.extend(range(int(y[0]), int(y[1]) + 1))
                else:
                    years_flat.append(int(y) if isinstance(y, float) else y)
        df_type = df_type[df_type['year'].isin(years_flat)]
    
    # Filtrer par masse si fournie
    if user_mass:
        mass_mask = pd.Series(False, index=df_type.index)
        mass_list = user_mass if isinstance(user_mass, list) else [user_mass]
        for m in mass_list:
            if isinstance(m, (list, tuple)) and len(m) == 2:
                mass_mask |= df_type['mass_cleaned'].between(m[0], m[1])
            else:
                mass_mask |= (df_type['mass_bin'] == m)
        df_type = df_type[mass_mask]
    
    # Filtrer par continents si fournis
    if user_continents:
        cont_list = user_continents if isinstance(user_continents, list) else [user_continents]
        df_type = df_type[df_type['continent'].isin(cont_list)]
    
    # Prédictions - toujours retourner des listes normalisées
    if user_years:
        year_pred = user_years
    elif not df_type.empty:
        # Retourner la période la plus fréquente
        year_pred = df_type['year_period'].mode()[0]
    else:
        year_pred = None
    
    if user_mass:
        mass_pred = user_mass if isinstance(user_mass, list) else [user_mass]
    elif not df_type.empty:
        mass_pred = [df_type['mass_bin'].mode()[0]]
    else:
        mass_pred = None
    
    if user_continents:
        continent_pred = user_continents if isinstance(user_continents, list) else [user_continents]
    elif not df_type.empty:
        continent_pred = [df_type['continent'].mode()[0]]
    else:
        continent_pred = None

    return year_pred, mass_pred, continent_pred

# -----------------------------
# Infos selon critères
# -----------------------------
def get_type_info(df, top_type, user_years=None, user_mass=None, user_continents=None,
                  pred_year=None, pred_mass=None, pred_continent=None):
    """
    Récupère les informations sur les météorites correspondant au type et aux critères.
    Les critères UTILISATEUR sont OBLIGATOIRES et ne sont jamais assouplis.
    """
    # ÉTAPE 1: Commencer avec le type prédit
    df_result = df[df['recclass_clean'] == top_type].copy()
    
    # ÉTAPE 2: Appliquer les critères UTILISATEUR (OBLIGATOIRES - jamais assouplis)
    if user_continents:
        cont_list = user_continents if isinstance(user_continents, list) else [user_continents]
        df_result = df_result[df_result['continent'].isin(cont_list)]
    
    if user_years:
        years_flat = _extract_years(user_years)
        if years_flat:
            df_result = df_result[df_result['year'].isin(years_flat)]
    
    if user_mass:
        mass_mask = pd.Series(False, index=df_result.index)
        mass_list = user_mass if isinstance(user_mass, list) else [user_mass]
        for m in mass_list:
            if isinstance(m, (list, tuple)) and len(m) == 2:
                mass_mask |= df_result['mass_cleaned'].between(m[0], m[1])
            else:
                mass_mask |= (df_result['mass_bin'] == m)
        df_result = df_result[mass_mask]
    
    # ÉTAPE 3: Si vide après critères utilisateur, chercher DANS LE CONTINENT demandé avec un autre type
    if df_result.empty and user_continents:
        # Garder le continent mais ignorer le type
        df_result = df.copy()
        cont_list = user_continents if isinstance(user_continents, list) else [user_continents]
        df_result = df_result[df_result['continent'].isin(cont_list)]
        
        # Appliquer les autres critères utilisateur si fournis
        if user_years:
            years_flat = _extract_years(user_years)
            if years_flat:
                df_temp = df_result[df_result['year'].isin(years_flat)]
                if not df_temp.empty:
                    df_result = df_temp
        
        if user_mass:
            mass_mask = pd.Series(False, index=df_result.index)
            mass_list = user_mass if isinstance(user_mass, list) else [user_mass]
            for m in mass_list:
                if isinstance(m, (list, tuple)) and len(m) == 2:
                    mass_mask |= df_result['mass_cleaned'].between(m[0], m[1])
                else:
                    mass_mask |= (df_result['mass_bin'] == m)
            df_temp = df_result[mass_mask]
            if not df_temp.empty:
                df_result = df_temp
    
    # ÉTAPE 4: Si l'utilisateur n'a PAS donné de continent, utiliser le continent PRÉDIT comme filtre
    if not user_continents and pred_continent:
        cont_list = pred_continent if isinstance(pred_continent, list) else [pred_continent]
        df_temp = df_result[df_result['continent'].isin(cont_list)]
        if not df_temp.empty:
            df_result = df_temp
    
    # ÉTAPE 5: Si toujours vide, fallback sur le type seul avec continent prédit
    if df_result.empty:
        df_result = df[df['recclass_clean'] == top_type].copy()
        if pred_continent:
            cont_list = pred_continent if isinstance(pred_continent, list) else [pred_continent]
            df_temp = df_result[df_result['continent'].isin(cont_list)]
            if not df_temp.empty:
                df_result = df_temp

    names = df_result['name'].tolist() if not df_result.empty else []
    countries = df_result['country'].dropna().unique().tolist() if not df_result.empty else []
    sample_years = df_result['year'].dropna().tolist() if not df_result.empty else []
    mass_bin = df_result['mass_bin'].mode()[0] if not df_result.empty and len(df_result['mass_bin'].mode()) > 0 else None

    return names, countries, sample_years, mass_bin, df_result


def _extract_years(years_input):
    """
    Extrait une liste d'années à partir de différents formats d'entrée.
    Gère: [1994, 2006], [[1994, 2006]], [(1994, 2006)], "20th Century", etc.
    """
    if years_input is None:
        return []
    
    # Si c'est une période (string)
    if isinstance(years_input, str):
        return []  # Sera traité par year_period
    
    years_flat = []
    
    # Si c'est une liste
    if isinstance(years_input, list):
        # Cas: [[1994, 2006]] ou [(1994, 2006)] - liste contenant une plage
        if len(years_input) == 1 and isinstance(years_input[0], (list, tuple)) and len(years_input[0]) == 2:
            start, end = years_input[0]
            years_flat = list(range(int(start), int(end) + 1))
        # Cas: [1994, 2006] - pourrait être une plage ou deux années
        elif len(years_input) == 2 and all(isinstance(y, (int, float)) for y in years_input):
            start, end = min(years_input), max(years_input)
            if end - start > 1:  # C'est une plage
                years_flat = list(range(int(start), int(end) + 1))
            else:  # Deux années individuelles
                years_flat = [int(y) for y in years_input]
        # Cas: liste d'années ou de plages
        else:
            for y in years_input:
                if isinstance(y, (list, tuple)) and len(y) == 2:
                    years_flat.extend(range(int(y[0]), int(y[1]) + 1))
                elif isinstance(y, (int, float)):
                    years_flat.append(int(y))
    
    return years_flat

# -----------------------------
# Statistiques de qualité des règles
# -----------------------------
def get_rules_statistics(filtered_rules):
    if filtered_rules.empty:
        return {
            'total': 0,
            'type_rules': 0,
            'geo_rules': 0,
            'mean_confidence': 0,
            'mean_lift': 0
        }
    
    type_rules = filtered_rules[filtered_rules.apply(is_type_prediction_rule, axis=1)]
    
    return {
        'total': len(filtered_rules),
        'type_rules': len(type_rules),
        'geo_rules': len(filtered_rules) - len(type_rules),
        'mean_confidence': filtered_rules['confidence'].mean(),
        'mean_lift': filtered_rules['lift'].mean()
    }

# -----------------------------
# Traitement d'une sélection utilisateur
# -----------------------------
def process_user_selection(sel, rules, df):
    """
    Traite la sélection utilisateur pour prédire le type de météorite.
    Utilise d'abord un filtrage non-strict, puis strict si trop de résultats.
    """
    # Récupérer les critères utilisateur
    years = sel.get('years') or []
    mass = sel.get('mass') or []
    continents = sel.get('continents') or []

    # D'abord essayer le mode strict
    filtered_rules = filter_rules(rules, df, years, mass, continents, strict=True)
    
    # Si pas assez de règles en mode strict, passer en mode non-strict
    if len(filtered_rules) < 3:
        filtered_rules = filter_rules(rules, df, years, mass, continents, strict=False)
    
    # Ne garder que les règles de qualité (lift >= 1)
    if not filtered_rules.empty:
        quality_rules = filtered_rules[filtered_rules['lift'] >= 1.0]
        if not quality_rules.empty:
            filtered_rules = quality_rules
    
    top_type, prob = get_most_probable_type(filtered_rules, df)

    # Prédire les critères manquants
    year_pred, mass_pred, continent_pred = predict_missing_criteria(
        df, top_type, years if years else None, mass if mass else None, continents if continents else None
    )

    # Filtrer le dataset selon le type et les critères/prédictions
    names, countries, sample_years, mass_bin, df_points = get_type_info(
        df, top_type, years if years else None, mass if mass else None, continents if continents else None,
        year_pred, mass_pred, continent_pred
    )

    # Si le type prédit est "OTHER", afficher le recclass le plus fréquent
    display_type = top_type
    if top_type == "OTHER" and not df_points.empty:
        mode_result = df_points['recclass'].mode()
        display_type = mode_result[0] if len(mode_result) > 0 else top_type

    # Construire le résultat avec seulement les valeurs PRÉDITES (non fournies par l'utilisateur)
    result = {
        'selection': sel,
        'filtered_rules': filtered_rules,
        'top_type': display_type,
        'probability': round(prob, 4),
        'names': names[:20] if len(names) > 20 else names,
        'countries': countries,
        'sample_years': sample_years[:20] if len(sample_years) > 20 else sample_years,
        'rules_count': len(filtered_rules),
        'rules_quality': get_rules_statistics(filtered_rules)
    }
    
    # N'ajouter les prédictions QUE si l'utilisateur n'a pas fourni la valeur
    if not years:  # L'utilisateur n'a pas donné d'années → on prédit
        result['predicted_years'] = year_pred
    
    if not mass:  # L'utilisateur n'a pas donné de masse → on prédit
        result['predicted_mass'] = mass_pred
    
    if not continents:  # L'utilisateur n'a pas donné de continent → on prédit
        result['predicted_continent'] = continent_pred
    
    return result
    



# -----------------------------
# Carte interactive
# -----------------------------
def plot_examples_on_map(examples_info, colors=None, map_file='map.html'):
    if colors is None:
        colors = ['hotpink', 'purple', 'orange', 'blue', 'green', 'darkred', 'yellow', 'red']
    
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    for i, info in enumerate(examples_info):
        df_points = info['df_points']
        color = colors[i % len(colors)]
        
        for _, row in df_points.iterrows():
            if pd.notna(row.get('reclat')) and pd.notna(row.get('reclong')):
                folium.CircleMarker(
                    location=[row['reclat'], row['reclong']],
                    radius=4,
                    popup=f"<b>{row['name']}</b><br>{row.get('mass_cleaned', 'N/A')} g<br>{row.get('country', 'N/A')}",
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7
                ).add_to(m)
    
    m.save(map_file)
    return m

# -----------------------------
# Évaluation qualité des règles
# -----------------------------
def evaluate_rules_quality(rules):
    eval_df = rules[~rules.apply(is_geographic_tautology, axis=1)].copy()
    conditions = [
        (eval_df['support'] >= 0.01) & (eval_df['confidence'] >= 0.7) & (eval_df['lift'] >= 1.2),
        (eval_df['support'] >= 0.005) & (eval_df['confidence'] >= 0.5) & (eval_df['lift'] >= 1.0),
        (eval_df['support'] < 0.005) | (eval_df['confidence'] < 0.5) | (eval_df['lift'] < 1.0)
    ]
    labels = ['Forte', 'Moyenne', 'Faible']
    eval_df['quality'] = np.select(conditions, labels, default='Faible')
    return eval_df
