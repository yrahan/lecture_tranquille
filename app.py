import streamlit as st
import sqlite3
import time
import os
import re
from datetime import datetime
from init_db import init_database
from openai import OpenAI

# Configuration de la page - DOIT être en premier
st.set_page_config(
    page_title="Lecture tranquille",
    page_icon="📖",
    layout="centered"
)

# Mapping entre tranches d'âge et niveaux scolaires
# Ce mapping permet de garder la compatibilité avec la base de données
# tout en affichant les tranches d'âge à l'utilisateur
AGES_VERS_NIVEAUX = {
    "6–7 ans": "CP",
    "7–8 ans": "CE1",
    "8–9 ans": "CE2"
}

NIVEAUX_VERS_AGES = {v: k for k, v in AGES_VERS_NIVEAUX.items()}

def age_vers_niveau(tranche_age):
    """Convertit une tranche d'âge en niveau scolaire pour la base de données."""
    return AGES_VERS_NIVEAUX.get(tranche_age, "CP")

def niveau_vers_age(niveau):
    """Convertit un niveau scolaire en tranche d'âge pour l'affichage."""
    return NIVEAUX_VERS_AGES.get(niveau, "6–7 ans")

# Liste de mots interdits pour le filtrage du contenu enfant
# Cette liste est volontairement basique et peut être enrichie
MOTS_INTERDITS = [
    # Violence
    "tuer", "mort", "sang", "arme", "pistolet", "fusil", "couteau", "bombe",
    "guerre", "meurtre", "assassin", "violence", "frapper", "battre",
    # Contenu sexuel
    "sexe", "nu", "nue", "penis", "vagin", "seins", "pornographie",
    # Drogues
    "drogue", "cocaine", "heroine", "cannabis", "alcool", "cigarette", "fumer",
    # Insultes communes
    "merde", "putain", "connard", "salaud", "enculer", "nique", "bordel",
    "con", "pute", "bite", "couille"
]

# Textes de secours par mode (utilisés si la saisie est vidée après filtrage)
TEXTES_SECOURS = {
    "Histoire": "Raconte une histoire douce et joyeuse pour un enfant, avec des animaux et de l'amitié.",
    "Méditation pour dormir": "Propose une méditation très calme pour aider un enfant à se détendre avant de dormir.",
    "Vulgarisation scientifique": "Explique simplement un phénomène de la nature adapté à un enfant, comme pourquoi le ciel est bleu ou comment pousse une plante."
}

# Longueur cible du texte selon l'âge
LONGUEUR_PAR_AGE = {
    "6–7 ans": "100 à 150 mots",
    "7–8 ans": "150 à 200 mots",
    "8–9 ans": "200 à 250 mots"
}

def contains_forbidden_words(user_input):
    """
    Vérifie si la saisie contient des mots interdits.

    Returns:
        True si des mots interdits sont détectés, False sinon
    """
    if not user_input:
        return False

    texte_lower = user_input.lower()
    for mot in MOTS_INTERDITS:
        pattern = r'\b' + re.escape(mot) + r'\b'
        if re.search(pattern, texte_lower):
            return True
    return False

def sanitize_user_input(user_input, mode):
    """
    Nettoie la saisie utilisateur.
    Si des mots inappropriés sont détectés, retourne directement le texte de secours.

    Args:
        user_input: Le texte saisi par l'utilisateur
        mode: Le type de contenu (Histoire, Méditation, Vulgarisation)

    Returns:
        Le texte de secours si des mots interdits sont détectés, sinon le texte original
    """
    if not user_input:
        return TEXTES_SECOURS.get(mode, TEXTES_SECOURS["Histoire"])

    # Si des mots interdits sont détectés, utiliser directement le texte de secours
    if contains_forbidden_words(user_input):
        return TEXTES_SECOURS.get(mode, TEXTES_SECOURS["Histoire"])

    return user_input

def generate_ai_text(age_range, mode, user_input, existing_text=None):
    """
    Génère ou modifie un texte adapté aux enfants via l'API OpenRouter.

    Args:
        age_range: La tranche d'âge (ex: "6–7 ans")
        mode: Le type de contenu (Histoire, Méditation pour dormir, Vulgarisation scientifique)
        user_input: La saisie de l'utilisateur (déjà nettoyée)
        existing_text: Le texte existant à modifier (optionnel)

    Returns:
        Le texte généré ou modifié, ou un message d'erreur
    """
    # Récupérer la clé API depuis les secrets Streamlit
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except KeyError:
        return "❌ Erreur de configuration : la clé API n'est pas configurée."

    # Créer le client OpenAI pour OpenRouter
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    # Longueur cible selon l'âge
    longueur = LONGUEUR_PAR_AGE.get(age_range, "150 mots")

    # Construire le prompt système
    system_prompt = f"""Tu es une intelligence artificielle bienveillante qui écrit en français pour des enfants de {age_range}.

Règles à suivre :
- Écris des phrases courtes et simples
- Utilise un vocabulaire adapté à l'âge
- Adopte un ton chaleureux et encourageant
- Longueur cible : {longueur}
- INTERDICTIONS ABSOLUES : pas de violence, pas de contenu sexuel, pas de propos effrayants, haineux ou inappropriés pour des enfants

Type de contenu demandé : {mode}
"""

    # Si un texte existe déjà, on le modifie selon les instructions
    if existing_text:
        user_prompt = f"""Voici un texte existant :

{existing_text}

Modifie ce texte selon cette instruction : {user_input}

Réécris le texte complet en appliquant la modification demandée, en gardant le même style et la même longueur."""
    else:
        # Adapter le prompt utilisateur selon le mode
        if mode == "Histoire":
            user_prompt = f"Écris une histoire douce et imaginative à partir de cette idée : {user_input}"
        elif mode == "Méditation pour dormir":
            user_prompt = f"Écris une méditation calme et apaisante pour aider un enfant à s'endormir, inspirée par : {user_input}. Le texte sera lu par un parent à voix douce."
        else:  # Vulgarisation scientifique
            user_prompt = f"Explique de façon simple et concrète, avec des exemples du quotidien : {user_input}"

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"😔 Désolé, je n'arrive pas à générer le texte pour le moment. Réessaie plus tard."

def get_db_connection():
    """Crée une connexion à la base de données SQLite."""
    return sqlite3.connect("lecture.db", check_same_thread=False)

def get_textes_by_niveau(niveau):
    """Récupère tous les textes d'un niveau donné."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titre, texte, theme, difficulte, image_path
        FROM textes
        WHERE niveau = ?
        ORDER BY difficulte
    """, (niveau,))
    textes = cursor.fetchall()
    conn.close()
    return textes

def get_qcm_by_texte(texte_id):
    """Récupère les QCM d'un texte, triés par difficulté."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, question, option_a, option_b, option_c, reponse_correcte, ordre_difficulte
        FROM qcm
        WHERE texte_id = ?
        ORDER BY ordre_difficulte
    """, (texte_id,))
    qcm = cursor.fetchall()
    conn.close()
    return qcm

def get_questions_ouvertes_by_texte(texte_id):
    """Récupère les questions ouvertes d'un texte, triées par difficulté."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, question, proposition_reponse, ordre_difficulte
        FROM questions_ouvertes
        WHERE texte_id = ?
        ORDER BY ordre_difficulte
    """, (texte_id,))
    questions = cursor.fetchall()
    conn.close()
    return questions

def save_resultat(texte_id, temps_secondes, mots_lus, mots_par_minute):
    """Enregistre un résultat de lecture dans la base de données."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resultats (texte_id, date_lecture, temps_secondes, mots_lus, mots_par_minute)
        VALUES (?, ?, ?, ?, ?)
    """, (texte_id, datetime.now().isoformat(), temps_secondes, mots_lus, mots_par_minute))
    conn.commit()
    conn.close()

def compter_mots(texte):
    """Compte le nombre de mots dans un texte."""
    return len(texte.split())

def create_placeholder_image(image_path, titre):
    """Crée une icône illustrative style jeunesse sans texte."""
    try:
        from PIL import Image, ImageDraw

        # Thèmes et leurs configurations visuelles (icônes simples)
        themes = {
            # Animaux
            "chat": {
                "bg": "#FFF5E6",
                "shapes": [
                    ("ellipse", "#FFB366", 150, 120, 250, 200),  # Corps
                    ("ellipse", "#FFB366", 170, 80, 230, 130),   # Tête
                    ("ellipse", "#333333", 185, 95, 195, 105),   # Œil
                    ("ellipse", "#333333", 205, 95, 215, 105),   # Œil
                    ("polygon", "#FFB366", [(150, 85), (160, 60), (175, 85)]),  # Oreille
                    ("polygon", "#FFB366", [(225, 85), (240, 60), (250, 85)]),  # Oreille
                ]
            },
            "chien": {
                "bg": "#F5F0E6",
                "shapes": [
                    ("ellipse", "#8B4513", 140, 120, 260, 220),  # Corps
                    ("ellipse", "#8B4513", 160, 70, 240, 140),   # Tête
                    ("ellipse", "#333333", 180, 90, 190, 100),   # Œil
                    ("ellipse", "#333333", 210, 90, 220, 100),   # Œil
                    ("ellipse", "#5D3A1A", 190, 105, 210, 120),  # Museau
                ]
            },
            "hamster": {
                "bg": "#FFF8E1",
                "shapes": [
                    ("ellipse", "#D4A574", 150, 100, 250, 200),  # Corps rond
                    ("ellipse", "#F5DEB3", 170, 130, 230, 180),  # Ventre
                    ("ellipse", "#333333", 175, 120, 185, 130),  # Œil
                    ("ellipse", "#333333", 215, 120, 225, 130),  # Œil
                ]
            },
            # École
            "ecole": {
                "bg": "#E3F2FD",
                "shapes": [
                    ("rectangle", "#FFC107", 120, 100, 280, 220),  # Bâtiment
                    ("polygon", "#FF5722", [(120, 100), (200, 50), (280, 100)]),  # Toit
                    ("rectangle", "#795548", 180, 160, 220, 220),  # Porte
                    ("rectangle", "#81D4FA", 140, 120, 160, 150),  # Fenêtre
                    ("rectangle", "#81D4FA", 240, 120, 260, 150),  # Fenêtre
                ]
            },
            "recre": {
                "bg": "#E8F5E9",
                "shapes": [
                    ("rectangle", "#8BC34A", 0, 200, 400, 300),   # Sol
                    ("ellipse", "#FF5722", 180, 100, 220, 140),   # Ballon
                    ("ellipse", "#2196F3", 120, 160, 150, 190),   # Bille
                    ("ellipse", "#9C27B0", 250, 150, 280, 180),   # Bille
                ]
            },
            "spectacle": {
                "bg": "#FCE4EC",
                "shapes": [
                    ("rectangle", "#9C27B0", 100, 180, 300, 250),  # Scène
                    ("polygon", "#FFEB3B", [(200, 80), (180, 130), (220, 130)]),  # Étoile
                    ("ellipse", "#4CAF50", 160, 120, 190, 180),   # Personnage
                    ("ellipse", "#F44336", 210, 120, 240, 180),   # Personnage
                ]
            },
            # Jeux et activités
            "ballon": {
                "bg": "#FFEBEE",
                "shapes": [
                    ("ellipse", "#F44336", 140, 80, 260, 200),    # Ballon
                    ("ellipse", "#FFCDD2", 160, 100, 200, 140),   # Reflet
                ]
            },
            "velo": {
                "bg": "#E0F7FA",
                "shapes": [
                    ("ellipse", "#333333", 100, 150, 160, 210),   # Roue arrière
                    ("ellipse", "#333333", 240, 150, 300, 210),   # Roue avant
                    ("polygon", "#2196F3", [(130, 180), (200, 120), (270, 180), (200, 160)]),  # Cadre
                ]
            },
            "piscine": {
                "bg": "#E3F2FD",
                "shapes": [
                    ("rectangle", "#81D4FA", 80, 120, 320, 220),  # Eau
                    ("ellipse", "#BBDEFB", 120, 140, 180, 180),   # Vague
                    ("ellipse", "#BBDEFB", 200, 150, 260, 190),   # Vague
                ]
            },
            "foot": {
                "bg": "#E8F5E9",
                "shapes": [
                    ("rectangle", "#8BC34A", 0, 200, 400, 300),   # Pelouse
                    ("ellipse", "#FFFFFF", 160, 100, 240, 180),   # Ballon
                    ("polygon", "#333333", [(185, 120), (200, 110), (215, 120), (210, 135), (190, 135)]),  # Pentagone
                ]
            },
            # Quotidien
            "maman": {
                "bg": "#FCE4EC",
                "shapes": [
                    ("ellipse", "#F48FB1", 160, 80, 240, 160),    # Tête
                    ("ellipse", "#F48FB1", 140, 150, 260, 250),   # Corps
                    ("ellipse", "#E91E63", 170, 170, 230, 220),   # Cœur/tablier
                ]
            },
            "dejeuner": {
                "bg": "#FFF8E1",
                "shapes": [
                    ("rectangle", "#FFCC80", 100, 150, 300, 250), # Table
                    ("ellipse", "#FFFFFF", 150, 110, 220, 160),   # Bol
                    ("rectangle", "#D7CCC8", 240, 120, 270, 170), # Verre
                ]
            },
            "nuit": {
                "bg": "#303F9F",
                "shapes": [
                    ("ellipse", "#FFF59D", 260, 60, 320, 120),    # Lune
                    ("ellipse", "#FFFFFF", 120, 80, 130, 90),     # Étoile
                    ("ellipse", "#FFFFFF", 160, 100, 170, 110),   # Étoile
                    ("ellipse", "#FFFFFF", 200, 70, 210, 80),     # Étoile
                ]
            },
            # Nature et météo
            "parc": {
                "bg": "#E8F5E9",
                "shapes": [
                    ("rectangle", "#8BC34A", 0, 200, 400, 300),   # Herbe
                    ("ellipse", "#4CAF50", 100, 100, 180, 180),   # Arbre
                    ("rectangle", "#795548", 130, 180, 150, 220), # Tronc
                    ("ellipse", "#FFEB3B", 280, 50, 340, 110),    # Soleil
                ]
            },
            "jardin": {
                "bg": "#E8F5E9",
                "shapes": [
                    ("rectangle", "#8D6E63", 80, 180, 320, 260),  # Terre
                    ("ellipse", "#F44336", 120, 130, 160, 170),   # Tomate
                    ("ellipse", "#F44336", 200, 140, 240, 180),   # Tomate
                    ("polygon", "#4CAF50", [(140, 130), (145, 100), (150, 130)]),  # Feuille
                ]
            },
            "pluie": {
                "bg": "#ECEFF1",
                "shapes": [
                    ("ellipse", "#78909C", 120, 80, 280, 160),    # Nuage
                    ("ellipse", "#2196F3", 150, 180, 160, 200),   # Goutte
                    ("ellipse", "#2196F3", 200, 190, 210, 210),   # Goutte
                    ("ellipse", "#2196F3", 250, 175, 260, 195),   # Goutte
                ]
            },
            "tempete": {
                "bg": "#455A64",
                "shapes": [
                    ("ellipse", "#78909C", 100, 60, 300, 150),    # Nuage
                    ("polygon", "#FFEB3B", [(200, 150), (180, 200), (210, 190), (190, 240)]),  # Éclair
                ]
            },
            "orage": {
                "bg": "#37474F",
                "shapes": [
                    ("ellipse", "#607D8B", 100, 60, 300, 140),    # Nuage
                    ("polygon", "#FFEB3B", [(200, 140), (170, 200), (210, 180), (180, 250)]),  # Éclair
                ]
            },
            "camping": {
                "bg": "#E8F5E9",
                "shapes": [
                    ("polygon", "#FF7043", [(200, 100), (120, 220), (280, 220)]),  # Tente
                    ("rectangle", "#795548", 185, 180, 215, 220), # Entrée
                    ("ellipse", "#81D4FA", 80, 180, 160, 230),    # Lac
                ]
            },
            # Cuisine
            "gateau": {
                "bg": "#FBE9E7",
                "shapes": [
                    ("ellipse", "#D7CCC8", 100, 180, 300, 260),   # Assiette
                    ("rectangle", "#8D6E63", 140, 100, 260, 200), # Gâteau
                    ("rectangle", "#FFEB3B", 195, 70, 205, 100),  # Bougie
                    ("ellipse", "#FF5722", 193, 55, 207, 70),     # Flamme
                ]
            },
            # Lecture et découverte
            "biblio": {
                "bg": "#F3E5F5",
                "shapes": [
                    ("rectangle", "#CE93D8", 80, 80, 180, 240),   # Étagère
                    ("rectangle", "#F48FB1", 90, 90, 110, 150),   # Livre
                    ("rectangle", "#90CAF9", 115, 100, 135, 150), # Livre
                    ("rectangle", "#A5D6A7", 140, 85, 160, 150),  # Livre
                    ("rectangle", "#FFCC80", 220, 120, 300, 180), # Livre ouvert
                ]
            },
            "lettre": {
                "bg": "#E8EAF6",
                "shapes": [
                    ("rectangle", "#FFFFFF", 120, 100, 280, 200), # Enveloppe
                    ("polygon", "#C5CAE9", [(120, 100), (200, 150), (280, 100)]),  # Rabat
                    ("ellipse", "#F44336", 240, 160, 270, 190),   # Cœur/timbre
                ]
            },
            "musee": {
                "bg": "#EFEBE9",
                "shapes": [
                    ("rectangle", "#8D6E63", 100, 120, 300, 240), # Bâtiment
                    ("polygon", "#795548", [(100, 120), (200, 60), (300, 120)]),  # Fronton
                    ("rectangle", "#FFCC80", 140, 160, 170, 240), # Colonne
                    ("rectangle", "#FFCC80", 230, 160, 260, 240), # Colonne
                ]
            },
            "zoo": {
                "bg": "#FFF3E0",
                "shapes": [
                    ("ellipse", "#FFB74D", 120, 100, 200, 180),   # Lion
                    ("ellipse", "#FFE0B2", 140, 130, 180, 160),   # Crinière
                    ("ellipse", "#FFCC80", 250, 80, 280, 200),    # Girafe cou
                    ("ellipse", "#FFCC80", 240, 60, 290, 100),    # Girafe tête
                ]
            },
            # Autres
            "rentree": {
                "bg": "#E3F2FD",
                "shapes": [
                    ("rectangle", "#2196F3", 140, 100, 260, 200), # Cartable
                    ("rectangle", "#1976D2", 160, 80, 240, 110),  # Rabat
                    ("ellipse", "#FFC107", 180, 130, 220, 170),   # Boucle
                ]
            },
            "cabane": {
                "bg": "#E8F5E9",
                "shapes": [
                    ("rectangle", "#8D6E63", 120, 140, 280, 240), # Cabane
                    ("polygon", "#795548", [(110, 140), (200, 80), (290, 140)]),  # Toit
                    ("rectangle", "#4CAF50", 170, 180, 230, 240), # Entrée
                ]
            },
            "demenagement": {
                "bg": "#FFF8E1",
                "shapes": [
                    ("rectangle", "#8D6E63", 100, 140, 300, 240), # Carton
                    ("rectangle", "#A1887F", 100, 140, 300, 160), # Rabat
                    ("ellipse", "#F48FB1", 180, 80, 220, 120),    # Cœur
                ]
            },
            "marche": {
                "bg": "#FFF3E0",
                "shapes": [
                    ("rectangle", "#FF8A65", 100, 120, 200, 200), # Étal
                    ("ellipse", "#F44336", 120, 100, 150, 130),   # Pomme
                    ("ellipse", "#4CAF50", 160, 100, 190, 130),   # Pomme
                    ("ellipse", "#FF9800", 250, 140, 280, 200),   # Carotte
                ]
            },
            "default": {
                "bg": "#F5F5F5",
                "shapes": [
                    ("ellipse", "#BBDEFB", 120, 100, 200, 180),
                    ("ellipse", "#C8E6C9", 200, 120, 280, 200),
                ]
            }
        }

        # Déterminer le thème depuis le nom de fichier ou titre
        filename = os.path.basename(image_path).lower()
        titre_lower = titre.lower()

        theme_key = "default"

        # Chercher dans le nom de fichier d'abord
        for key in themes.keys():
            if key in filename:
                theme_key = key
                break

        # Si pas trouvé, chercher dans le titre
        if theme_key == "default":
            for key in themes.keys():
                if key in titre_lower:
                    theme_key = key
                    break

        # Cas spéciaux basés sur le titre
        if theme_key == "default":
            if "chat" in titre_lower or "minou" in titre_lower or "caramel" in titre_lower:
                theme_key = "chat"
            elif "chien" in titre_lower or "filou" in titre_lower:
                theme_key = "chien"
            elif "école" in titre_lower or "rentrée" in titre_lower:
                theme_key = "ecole"
            elif "bibliothèque" in titre_lower:
                theme_key = "biblio"
            elif "correspondant" in titre_lower:
                theme_key = "lettre"

        theme = themes[theme_key]

        # Créer l'image
        img = Image.new('RGB', (400, 300), color=theme["bg"])
        draw = ImageDraw.Draw(img)

        # Dessiner les formes
        for shape in theme["shapes"]:
            if shape[0] == "ellipse":
                draw.ellipse([shape[2], shape[3], shape[4], shape[5]], fill=shape[1])
            elif shape[0] == "rectangle":
                draw.rectangle([shape[2], shape[3], shape[4], shape[5]], fill=shape[1])
            elif shape[0] == "polygon":
                draw.polygon(shape[2], fill=shape[1])

        # Sauvegarder
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        img.save(image_path)
        return True
    except Exception:
        return False

def main():
    # Initialiser la base de données si elle n'existe pas (mode idempotent)
    if not os.path.exists("lecture.db"):
        init_database()

    # Titre principal
    st.title("📖 Lecture tranquille")
    st.markdown("### Pour les enfants de 6 à 9 ans")
    st.markdown("""
    Bienvenue ! Cette application t'aide à progresser en lecture, à ton rythme.
    Pas de stress, pas de pression : ici, on lit tranquillement et on s'amuse ! 🌟
    """)

    st.markdown("---")

    # Instructions pour l'adulte
    with st.expander("📋 Guide pour l'adulte accompagnant"):
        st.markdown("""
        **Comment utiliser l'application en 3 étapes :**

        1. **Choisir** la tranche d'âge (6–7, 7–8 ou 8–9 ans) et un texte adapté
        2. **Mesurer la fluence** : démarrer le chrono quand l'enfant lit à voix haute, puis l'arrêter
        3. **Vérifier la compréhension** : répondre aux questions ensemble

        💡 **Le chronomètre n'est qu'un outil ponctuel** : utilisez-le de temps en temps, sans pression. L'essentiel est que l'enfant prenne plaisir à lire, à découvrir l'histoire, à s'exprimer et à partager ce moment avec vous.

        *Restez bienveillant et encourageant. L'objectif est de progresser en confiance !*
        """)

    st.markdown("---")

    # Initialisation du session_state (partagé entre les onglets)
    if 'is_reading' not in st.session_state:
        st.session_state.is_reading = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'elapsed_time' not in st.session_state:
        st.session_state.elapsed_time = None
    if 'reading_finished' not in st.session_state:
        st.session_state.reading_finished = False
    if 'qcm_validated' not in st.session_state:
        st.session_state.qcm_validated = {}
    if 'show_proposition' not in st.session_state:
        st.session_state.show_proposition = {}
    if 'result_saved' not in st.session_state:
        st.session_state.result_saved = False
    if 'session_id' not in st.session_state:
        st.session_state.session_id = 0
    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = None

    # Navigation par onglets
    tab_lecture, tab_creation = st.tabs(["📖 Lecture", "✨ Création IA"])

    # ========== ONGLET LECTURE ==========
    with tab_lecture:
        # Section 1 : Choix du texte
        st.header("📚 Étape 1 : Choisis ton texte")

        col1, col2 = st.columns(2)

        with col1:
            tranche_age = st.selectbox("Ton âge :", list(AGES_VERS_NIVEAUX.keys()), key="lecture_age")
            niveau = age_vers_niveau(tranche_age)

        # Récupérer les textes du niveau
        textes = get_textes_by_niveau(niveau)

        if not textes:
            st.warning("Aucun texte trouvé pour cet âge.")
        else:
            with col2:
                titres = [t[1] for t in textes]
                titre_selectionne = st.selectbox("Texte :", titres)

            # Trouver le texte sélectionné
            texte_data = None
            for t in textes:
                if t[1] == titre_selectionne:
                    texte_data = t
                    break

            if texte_data:
                texte_id, titre, texte_contenu, theme, difficulte, image_path = texte_data
                nb_mots_total = compter_mots(texte_contenu)

                # Générer l'image si elle n'existe pas
                if image_path and not os.path.exists(image_path):
                    create_placeholder_image(image_path, titre)

                # Affichage du titre avec l'icône - design responsive
                if image_path and os.path.exists(image_path):
                    # Utiliser du HTML/CSS pour un alignement parfait et responsive
                    import base64
                    with open(image_path, "rb") as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode()

                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap;">
                        <img src="data:image/png;base64,{img_base64}"
                             style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; flex-shrink: 0;">
                        <div style="flex: 1; min-width: 200px;">
                            <h3 style="margin: 0; font-size: 1.3em; line-height: 1.2;">{titre}</h3>
                            <p style="margin: 4px 0 0 0; font-size: 0.85em; color: #666;">{theme} • {difficulte}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.subheader(f"📄 {titre}")

                st.info(texte_contenu)
                st.caption(f"📝 Ce texte contient **{nb_mots_total} mots**.")

                st.markdown("---")

                # Section 2 : Mesure de fluence
                st.header("⏱️ Étape 2 : Mesure ta vitesse de lecture")

                col_start, col_stop = st.columns(2)

                with col_start:
                    if st.button("▶️ Démarrer la lecture", disabled=st.session_state.is_reading, use_container_width=True):
                        st.session_state.is_reading = True
                        st.session_state.start_time = time.time()
                        st.session_state.elapsed_time = None
                        st.session_state.reading_finished = False
                        st.session_state.result_saved = False
                        st.rerun()

                with col_stop:
                    if st.button("⏹️ Arrêter la lecture", disabled=not st.session_state.is_reading, use_container_width=True):
                        st.session_state.is_reading = False
                        st.session_state.elapsed_time = time.time() - st.session_state.start_time
                        st.session_state.reading_finished = True
                        st.rerun()

                # Affichage de l'état
                if st.session_state.is_reading:
                    st.warning("⏱️ **Lecture en cours...** Lis à voix haute, tranquillement !")

                # Résultats de fluence
                if st.session_state.reading_finished and st.session_state.elapsed_time is not None:
                    elapsed_seconds = st.session_state.elapsed_time
                    elapsed_minutes = elapsed_seconds / 60

                    st.success(f"⏱️ **Temps de lecture : {elapsed_seconds:.1f} secondes**")

                    st.markdown("##### Combien de mots as-tu lus ?")
                    st.caption("Par défaut, c'est le texte entier. L'adulte peut ajuster si besoin.")

                    mots_lus = st.number_input(
                        "Nombre de mots lus :",
                        min_value=1,
                        max_value=nb_mots_total,
                        value=nb_mots_total,
                        step=1
                    )

                    # Calcul des mots par minute
                    if elapsed_minutes > 0:
                        mots_par_minute = mots_lus / elapsed_minutes

                        st.markdown("---")
                        st.markdown(f"""
                        ### 🎉 Bravo, c'est super !

                        Tu as lu **{mots_lus} mots** en **{elapsed_seconds:.1f} secondes**.

                        **➡️ Ta vitesse : {mots_par_minute:.0f} mots par minute**

                        Continue comme ça, tu progresses bien ! 📚✨
                        """)

                        # Sauvegarder le résultat
                        if not st.session_state.result_saved:
                            save_resultat(texte_id, elapsed_seconds, mots_lus, mots_par_minute)
                            st.session_state.result_saved = True

                st.markdown("---")

                # Section 3 : Compréhension
                st.header("🧠 Étape 3 : As-tu bien compris ?")
                st.markdown("Réponds aux questions pour vérifier que tu as bien compris le texte. Les questions vont du plus simple au plus réfléchi. Pas de stress, c'est pour apprendre ! 😊")

                # Récupérer les questions
                qcm_list = get_qcm_by_texte(texte_id)
                questions_ouvertes = get_questions_ouvertes_by_texte(texte_id)

                # QCM
                if qcm_list:
                    st.subheader("📝 Questions à choix multiple")
                    st.caption("Du plus simple au plus difficile")

                    for i, qcm in enumerate(qcm_list):
                        qcm_id, question, opt_a, opt_b, opt_c, reponse_correcte, ordre = qcm
                        key_qcm = f"{texte_id}_qcm_{qcm_id}"

                        # Indicateur de difficulté
                        if ordre == 1:
                            diff_icon = "🟢"
                        elif ordre == 2:
                            diff_icon = "🟡"
                        else:
                            diff_icon = "🟠"

                        st.markdown(f"**{diff_icon} Question {i+1} : {question}**")

                        options = [opt_a, opt_b, opt_c]
                        reponse = st.radio(
                            "Choisis ta réponse :",
                            options,
                            key=f"radio_{key_qcm}_{st.session_state.session_id}",
                            index=None,
                            label_visibility="collapsed"
                        )

                        col_valider, col_espace = st.columns([1, 3])
                        with col_valider:
                            if st.button("Valider", key=f"btn_{key_qcm}"):
                                st.session_state.qcm_validated[key_qcm] = reponse

                        if key_qcm in st.session_state.qcm_validated:
                            if st.session_state.qcm_validated[key_qcm] == reponse_correcte:
                                st.success("✅ Bravo, c'est la bonne réponse ! 🌟")
                            else:
                                st.info(f"💡 Ce n'est pas tout à fait ça. La bonne réponse était : **{reponse_correcte}**. Ce n'est pas grave, on peut relire un petit passage ensemble 🙂")

                        st.markdown("")

                # Questions ouvertes
                if questions_ouvertes:
                    st.subheader("✍️ Questions ouvertes")
                    st.caption("Écris ta réponse, puis tu peux voir une proposition pour comparer.")

                    for i, question in enumerate(questions_ouvertes):
                        q_id, q_texte, proposition, ordre = question
                        key_open = f"{texte_id}_open_{q_id}"

                        # Indicateur de difficulté
                        if ordre == 1:
                            diff_icon = "🟢"
                        elif ordre == 2:
                            diff_icon = "🟡"
                        else:
                            diff_icon = "🟠"

                        st.markdown(f"**{diff_icon} Question {i+1} : {q_texte}**")

                        st.text_area(
                            "Ta réponse :",
                            key=f"textarea_{key_open}_{st.session_state.session_id}",
                            height=80,
                            label_visibility="collapsed"
                        )

                        if st.button("💡 Voir une proposition de réponse", key=f"btn_prop_{key_open}"):
                            st.session_state.show_proposition[key_open] = True

                        if st.session_state.show_proposition.get(key_open, False):
                            st.info(f"**Proposition de réponse :** {proposition}")

                        st.markdown("")

                st.markdown("---")

                # Section 4 : Repères de fluence
                with st.expander("📊 Repères de vitesse de lecture en France"):
                    st.markdown("""
                    Voici des repères pour se situer. **Chacun avance à son rythme**, l'essentiel est de progresser tranquillement ! 🌱

                    | Âge | Vitesse moyenne (fin d'année) |
                    |--------|------------------------------|
                    | 6–7 ans | environ 50 mots/minute |
                    | 7–8 ans | environ 70 mots/minute |
                    | 8–9 ans | environ 90-110 mots/minute |

                    *Ces chiffres sont des moyennes. Certains enfants lisent plus vite, d'autres moins vite, et c'est très bien comme ça !*

                    🟢 Question facile • 🟡 Question moyenne • 🟠 Question plus réfléchie
                    """)

                st.markdown("---")

                # Bouton pour recommencer
                if st.button("🔄 Nouvelle lecture", use_container_width=True):
                    # Effacer les états de lecture
                    st.session_state.is_reading = False
                    st.session_state.start_time = None
                    st.session_state.elapsed_time = None
                    st.session_state.reading_finished = False
                    st.session_state.qcm_validated = {}
                    st.session_state.show_proposition = {}
                    st.session_state.result_saved = False

                    # Incrémenter session_id pour forcer la réinitialisation des widgets
                    st.session_state.session_id += 1

                    st.rerun()

    # ========== ONGLET CRÉATION IA ==========
    with tab_creation:
        st.header("✨ Création IA")
        st.markdown("""
        Donne une idée, quelques mots ou une phrase, et l'intelligence artificielle va créer un texte rien que pour toi !
        C'est magique et amusant ! 🌈
        """)

        # Sélection de la tranche d'âge
        age_creation = st.selectbox(
            "Ton âge :",
            list(AGES_VERS_NIVEAUX.keys()),
            key="creation_age"
        )

        # Sélection du type de contenu
        mode_creation = st.selectbox(
            "Que veux-tu créer ?",
            ["Histoire", "Méditation pour dormir", "Vulgarisation scientifique"],
            key="creation_mode"
        )

        # Description du mode sélectionné
        if mode_creation == "Histoire":
            st.caption("📖 Une histoire imaginative avec des personnages et des aventures douces.")
        elif mode_creation == "Méditation pour dormir":
            st.caption("🌙 Un texte calme et apaisant, parfait pour le moment du coucher.")
        else:
            st.caption("🔬 Une explication simple d'un phénomène, avec des exemples du quotidien.")

        # Zone de saisie - le placeholder change si un texte existe déjà
        if st.session_state.generated_text:
            placeholder_text = "Exemple : change le chat en chien, ajoute un arc-en-ciel, rends l'histoire plus drôle..."
            label_text = "Modifie le texte :"
        else:
            placeholder_text = "Exemple : un chat qui voyage dans l'espace, pourquoi le ciel est bleu, une forêt magique..."
            label_text = "Ton idée :"

        saisie_utilisateur = st.text_area(
            label_text,
            placeholder=placeholder_text,
            height=100,
            key=f"creation_input_{st.session_state.session_id}"
        )

        # Bouton de génération
        col_gen, col_new = st.columns(2)

        with col_gen:
            # Le label du bouton change si un texte existe
            btn_label = "🔄 Modifier" if st.session_state.generated_text else "🪄 Générer"

            if st.button(btn_label, use_container_width=True, type="primary"):
                if saisie_utilisateur.strip():
                    # Vérifier si des mots interdits sont présents
                    mots_interdits_detectes = contains_forbidden_words(saisie_utilisateur)

                    # Nettoyer la saisie (filtrage des mots inappropriés)
                    saisie_nettoyee = sanitize_user_input(saisie_utilisateur, mode_creation)

                    with st.spinner("✨ Création en cours..."):
                        # Passer le texte existant pour modification si disponible
                        texte_genere = generate_ai_text(
                            age_creation,
                            mode_creation,
                            saisie_nettoyee,
                            existing_text=st.session_state.generated_text
                        )
                        st.session_state.generated_text = texte_genere

                    # Effacer l'entrée après génération/modification
                    st.session_state.session_id += 1

                    st.rerun()
                else:
                    st.warning("Écris quelques mots ou une idée pour commencer !")

        with col_new:
            if st.button("🔄 Nouvelle idée", use_container_width=True):
                st.session_state.generated_text = None
                # Incrémenter session_id pour réinitialiser le champ de saisie
                st.session_state.session_id += 1
                st.rerun()

        # Affichage du texte généré
        if st.session_state.generated_text:
            st.markdown("---")
            st.markdown("### 📝 Ton texte")
            st.markdown(st.session_state.generated_text)

            # Compter les mots du texte généré
            nb_mots_genere = compter_mots(st.session_state.generated_text)
            st.caption(f"Ce texte contient **{nb_mots_genere} mots**.")

if __name__ == "__main__":
    main()
