import os
from pathlib import Path
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google import genai
import random 

# 1. Configuration de l'environnement et Gemini (SDK actuel google-genai)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = "gemini-4-hydrogen"
EMBEDDING_MODEL_ID = "gemini-embedding-001"

CSV_PATH = BASE_DIR.parent / "data_star" / "StarCreator_Database.csv"


# 2. lignes CSV --> documents textuels
def charger_base_etoiles(csv_path: Path = CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["description_rag"] = df.apply(formater_etoile_en_texte, axis=1)
    return df


def formater_etoile_en_texte(row: pd.Series) -> str:
    """Convertit une ligne du CSV en fiche descriptive lisible par le LLM."""
    met = f"{row['metallicite_fe_h']} [Fe/H]" if pd.notna(row["metallicite_fe_h"]) else "Inconnue"
    spec = row["type_spectral"] if pd.notna(row["type_spectral"]) else "Non spécifié"
    rayon = f"{row['rayon_solaire']} R☉" if pd.notna(row["rayon_solaire"]) else "Inconnu"

    return (
        f"Étoile : {row['nom_etoile']} | "
        f"Spectre thermique : {row['spectre_thermique']} ({row['temperature_k']} K) | "
        f"Masse : {row['masse_solaire']} M☉ | "
        f"Rayon : {rayon} | "
        f"Métallicité : {met} ({row['population_metallique']}) | "
        f"Rotation estimée : {row['rotation_estimee']} | "
        f"Type spectral : {spec} | "
        f"Planètes en orbite : {int(row['planetes_en_orbite'])}"
    )


# 3. Récupération (Retrieval) par mot
def recuperer_etoiles_par_criteres(
    df: pd.DataFrame,
    requete: str = "",
    spectre: str | None = None,
    population: str | None = None,
    rotation: str | None = None,
    top_k: int = 5,
) -> list[str]:
    """Récupère les étoiles correspondant aux jauges du jeu ou à un nom d'étoile."""
    resultat = df.copy()

    if spectre:
        resultat = resultat[resultat["spectre_thermique"].str.lower() == spectre.lower()]
    if population:
        resultat = resultat[resultat["population_metallique"].str.contains(population, case=False, na=False)]
    if rotation:
        resultat = resultat[resultat["rotation_estimee"].str.lower() == rotation.lower()]

    if requete:
        # Recherche de mots-clés de la requête dans la fiche descriptive
        mots = [m for m in requete.lower().split() if len(m) > 2]
        if mots:
            scores = resultat["description_rag"].str.lower().apply(
                lambda txt: sum(mot in txt for mot in mots)
            )
            resultat = resultat.assign(score_mot=scores).sort_values("score_mot", ascending=False)

    return resultat["description_rag"].head(top_k).tolist()


# 4. Récupération (Retrieval) par Recherche vectorielle par Embeddings Gemini
def recuperer_etoiles_par_embeddings(
    textes_candidats: list[str],
    question: str,
    top_k: int = 5,
) -> list[str]:
    """Vectorise un ensemble d'étoiles et la question avec gemini-embedding-001."""
    # Vectorisation des documents candidats
    doc_emb_response = client.models.embed_content(
        model=EMBEDDING_MODEL_ID,
        contents=textes_candidats,
    )
    doc_vectors = np.array([emb.values for emb in doc_emb_response.embeddings])

    # Vectorisation de la question utilisateur
    query_emb_response = client.models.embed_content(
        model=EMBEDDING_MODEL_ID,
        contents=question,
    )
    query_vector = np.array(query_emb_response.embeddings[0].values)

    # Calcul de la similarité cosinus
    normes_docs = np.linalg.norm(doc_vectors, axis=1) * np.linalg.norm(query_vector)
    similarites = np.dot(doc_vectors, query_vector) / np.where(normes_docs == 0, 1e-10, normes_docs)

    meilleurs_indices = np.argsort(similarites)[::-1][:top_k]
    return [textes_candidats[i] for i in meilleurs_indices]


#sélection d'une étoile en fonction du niveau du joueur
def selectionner_etoile_cible(df: pd.DataFrame, niveau_joueur: int) -> list[str]:
    """Sélectionne aléatoirement UNE étoile cible adaptée à la difficulté du niveau."""
    
    resultat = df.copy()

    # Logique de difficulté de jeu (Game Design)
    if niveau_joueur <= 3:
        # Niveaux faciles (1 à 3) : 
        # On demande des étoiles standards (Jaunes/Blanches) de Pop I == car c'est le plus commun.
        resultat = resultat[
            (resultat["spectre_thermique"].isin(["Jaune", "Blanche"])) & 
            (resultat["population_metallique"] == "Pop I (Riche)")
        ]
    elif niveau_joueur <= 10:
        # Niveaux moyens (4 à 10) :
        # On introduit des étoiles extrêmes (Très chaudes/Bleues ou très froides/Rouges).
        resultat = resultat[
            (resultat["spectre_thermique"].isin(["Bleu", "Rouge"]))
        ]
    else:
        # Niveaux difficiles (11 à 20) :
        # On demande des étoiles très rares (Pauvres en métaux, configurations atypiques).
        resultat = resultat[
            (resultat["population_metallique"] == "Pop II (Pauvre)") |
            (resultat["masse_solaire"] > 10.0) # Très massive
        ]

    # Si le filtre est trop strict, on prend tout le catalogue pour éviter un crash
    if resultat.empty:
        resultat = df.copy()

    # On sélectionne UNE SEULE étoile aléatoire dans ce sous-groupe comme "Modèle à recréer"
    etoile_choisie = resultat.sample(n=1).iloc[0]
    
    # On renvoie uniquement sa description pour la passer au prompt de génération
    return [etoile_choisie["description_rag"]]

# 5. Génération Augmentée (Augmented Generation) avec Gemini
# Dans interroger_rag_star_creator :

def genere_challenge(df, action, niveau_joueur):
    
    if action == "challenge":
        # 1. Sélectionne une cible selon la difficulté
        contexte_etoiles = selectionner_etoile_cible(df, niveau_joueur)
        
        contexte_formate = contexte_etoiles[0] # Il n'y a qu'une étoile à forger par session
        
        prompt = (
            f"La civilisation a besoin d'un soleil ayant EXACTEMENT ces caractéristiques :\n"
            f"{contexte_formate}\n\n"
            f"Rédige le briefing de la mission en décrivant le monde mourant, "
            f"et donne au joueur les valeurs cibles à atteindre."
        )
        
        interaction = client.interactions.create(
            model=MODEL_ID,
            system_instruction=(
            """ 
                Tu es 'Le Bienfaiteur', l'IA astrophysique du jeu Star Creator. L'Univers de l'an 6026 se refroidit, et tu guides les joueurs (les Star Creators) pour forger de nouveaux soleils et sauver l'humanité. Ton ton est dramatique, solennel, immersif, mais scientifiquement précis et pédagogique.

                TES MISSIONS (Réponds uniquement à la tâche demandée par le système) :
                1. CHALLENGES : Génère des briefings de mission adaptés au niveau de l'utilisateur. Décris la détresse d'une civilisation et les paramètres stellaires qu'elle requiert (Masse, Métallicité, Rotation, Spectre thermique). Génère un challenge par requête. 
                2. QUIZ : Génère des quiz de 10 questions à choix multiples sur l'astrophysique pour faire gagner des dabloons au joueur.
                3. STAR DIARY : Rédige le rapport scientifique de l'étoile venant d'être créée pour le journal du joueur.

                RÈGLES STRICTES :
                - Base-toi EXCLUSIVEMENT sur les données stellaires fournies dans ton contexte (le RAG). Ne fais pas d'hallucinations sur les caractéristiques d'une étoile.
                - Reste toujours dans ton personnage. Ne dis jamais que tu es une intelligence artificielle d'une entreprise terrestre actuelle.
                - Rends tes réponses captivantes : tu parles du destin de milliards d'âmes qui dépendent de la bonne étoile.

                FORMAT DE SORTIE : Lorsque tu génères un challenge ou un quiz, renvoie TOUJOURS ta réponse au format JSON structuré, afin que le système du vaisseau puisse le parser.
                """
            ),
            input=prompt,
        )

        return interaction.output_text


# --- TEST DU PROTOTYPE ---
if __name__ == "__main__":
    print("Chargement de StarCreator_Database.csv...")
    df_stars = charger_base_etoiles()
    print(f"{len(df_stars)} étoiles chargées.\n")

    # Exemple 1 : Question ouverte avec recherche hybride (mots-clés + embeddings)
    question_test = (
        "Génère un challenge pour un joueur au niveau 1 "
        
    )
    print(f"Question : {question_test}\n")
    reponse = genere_challenge(
        df_stars,
        action= "challenge",
        niveau_joueur= 3
    )
    print("Réponse du RAG :\n", reponse)
