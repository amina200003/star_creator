import pandas as pd
import numpy as np

def preparer_bdd_star_creator():
    # 1. Charger le fichier CSV (Ignorer les lignes de commentaires commençant par '#')
    print("Chargement des données...")
    df = pd.read_csv('data_star/dataset1.csv', comment='#')

    # 2. Sélectionner les colonnes pertinentes
    colonnes_a_garder = [
        'hostname',       # Nom de l'étoile
        'st_mass',        # Masse (en masses solaires) -> Jauge 1
        'st_met',         # Métallicité [Fe/H] -> Jauge 2
        'st_teff',        # Température (K) -> Jauge 4 (Spectre)
        'st_spectype',    # Type spectral (MKK) -> Pour le Star Diary
        'st_rad',         # Rayon (en rayons solaires) -> Pour le visuel 3D
        'sy_pnum'         # Nombre de planètes -> Pour le Lore
    ]
    df_clean = df[colonnes_a_garder].copy()

    # 3. Nettoyage de base : supprimer les étoiles sans masse ou température
    df_clean = df_clean.dropna(subset=['st_mass', 'st_teff'])

    # 4. Supprimer les doublons (1 ligne = 1 système stellaire)
    df_clean = df_clean.drop_duplicates(subset=['hostname'])

    # 5. --- TRADUCTION DES DONNÉES EN MÉCANIQUES DE JEU ---

    # A. Catégorisation du Spectre Thermique
    def get_spectrum(temp):
        if temp >= 10000: return 'Bleu'
        elif temp >= 6000: return 'Blanche'
        elif temp >= 5000: return 'Jaune'
        else: return 'Rouge'
    
    df_clean['spectre_thermique'] = df_clean['st_teff'].apply(get_spectrum)

    # B. Catégorisation de la Métallicité (Pop I vs Pop II)
    # L'indice [Fe/H] est logarithmique. 0.0 est le Soleil.
    # On fixe un seuil : < -0.5 est généralement considéré comme pauvre en métaux pour les jeux.
    def get_population(met):
        if pd.isna(met): return 'Pop I (Riche)' # Valeur par défaut si inconnue
        elif met > -0.5: return 'Pop I (Riche)'
        else: return 'Pop II (Pauvre)'
        
    df_clean['population_metallique'] = df_clean['st_met'].apply(get_population)

    # C. Simulation de la Rotation (Puisque les données réelles sont incomplètes)
    # Logique astrophysique : Plus l'étoile est chaude/massive (Bleue/Blanche), 
    # plus elle a tendance à tourner vite (Rapide). Les naines (Rouge) tournent lentement.
    def simulate_rotation(temp):
        if temp >= 8000:
            return np.random.choice(['Rapide', 'Moyenne'], p=[0.8, 0.2])
        elif temp >= 6000:
            return np.random.choice(['Moyenne', 'Rapide'], p=[0.7, 0.3])
        else:
            return np.random.choice(['Lente', 'Moyenne'], p=[0.8, 0.2])

    # Appliquer une graine aléatoire pour que les résultats soient les mêmes à chaque exécution
    np.random.seed(6026) 
    df_clean['rotation_estimee'] = df_clean['st_teff'].apply(simulate_rotation)

    # 6. Renommer les colonnes pour que ce soit propre pour l'IA et la BDD
    df_clean = df_clean.rename(columns={
        'hostname': 'nom_etoile',
        'st_mass': 'masse_solaire',
        'st_teff': 'temperature_k',
        'st_met': 'metallicite_fe_h',
        'st_spectype': 'type_spectral',
        'st_rad': 'rayon_solaire',
        'sy_pnum': 'planetes_en_orbite'
    })

    # 7. Sauvegarder la nouvelle base de données prête pour le jeu
    df_clean.to_csv('StarCreator_Database.csv', index=False)
    
    print("\n--- BASE DE DONNÉES STAR CREATOR GÉNÉRÉE ---")
    print(f"Total d'étoiles prêtes à jouer : {len(df_clean)}")
    print("\nRépartition par Spectre :")
    print(df_clean['spectre_thermique'].value_counts())
    
    return df_clean

# Lancer le script
preparer_bdd_star_creator()