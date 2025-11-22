# 📖 Lecture tranquille (CP-CE1-CE2)

Application bienveillante pour accompagner les enfants de CP, CE1 et CE2 dans leur apprentissage de la lecture.

## Fonctionnalités

- **Textes adaptés** : 3 textes par niveau (CP, CE1, CE2) avec longueurs appropriées
- **Images illustratives** : chaque histoire a son illustration
- **Mesure de fluence** : chronomètre pour calculer les mots lus par minute
- **Compréhension progressive** : QCM et questions ouvertes du plus simple au plus complexe
- **Repères français** : indications sur les vitesses moyennes de lecture
- **Sauvegarde des résultats** : historique des lectures dans une base SQLite
- **Expérience positive** : ton encourageant, aucune pression

## Structure du projet

```
lecture_tranquille/
├── app.py              # Application Streamlit principale
├── init_db.py          # Script d'initialisation de la base de données
├── lecture.db          # Base de données SQLite (créée automatiquement)
├── requirements.txt    # Dépendances Python
├── README.md           # Ce fichier
└── images/             # Dossier des illustrations
    ├── chat_minou.png
    ├── parc.png
    ├── petit_dejeuner.png
    ├── chat_caramel.png
    ├── parc_canards.png
    ├── gateau_chocolat.png
    ├── bibliotheque.png
    ├── jardin.png
    └── anniversaire.png
```

## Installation sous Linux

### 1. Créer un environnement virtuel

```bash
python3 -m venv venv
```

### 2. Activer l'environnement virtuel

```bash
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Initialiser la base de données

```bash
python init_db.py
```

Cette commande crée :
- La base de données `lecture.db` avec tous les textes et questions
- Le dossier `images/` pour les illustrations

### 5. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira dans votre navigateur à l'adresse `http://localhost:8501`.

## Base de données

### Structure des tables

- **textes** : id, niveau, titre, texte, theme, difficulte, image_path
- **qcm** : id, texte_id, question, options, reponse_correcte, ordre_difficulte
- **questions_ouvertes** : id, texte_id, question, proposition_reponse, ordre_difficulte
- **resultats** : id, texte_id, date_lecture, temps_secondes, mots_lus, mots_par_minute

### Ajouter des textes

Pour ajouter de nouveaux textes, modifiez le fichier `init_db.py` et relancez l'initialisation (après avoir supprimé `lecture.db`).

## Utilisation

### Pour l'adulte accompagnant

1. **Choisir** le niveau (CP, CE1 ou CE2) et un texte
2. **Démarrer** le chronomètre quand l'enfant commence à lire à voix haute
3. **Arrêter** quand la lecture est terminée
4. **Ajuster** le nombre de mots lus si l'enfant n'a pas tout lu
5. **Répondre** aux questions de compréhension ensemble

### Conseils pédagogiques

- Restez bienveillant et encourageant
- Ne comparez pas l'enfant aux autres
- Valorisez les progrès, même petits
- Faites des pauses si l'enfant se fatigue
- Les questions sont progressives : commencez toujours par les vertes (🟢)

### Indicateurs de difficulté des questions

- 🟢 Question facile (repérage simple)
- 🟡 Question moyenne (détails, ordre des événements)
- 🟠 Question plus réfléchie (inférence, réflexion)

## Longueur des textes

- **CP** : 20-40 mots (phrases très courtes, vocabulaire simple)
- **CE1** : 40-80 mots (phrases simples, petite histoire complète)
- **CE2** : 80-120 mots (phrases structurées, connecteurs simples)

## Images

Les images sont générées automatiquement comme placeholders colorés si elles n'existent pas. Pour de meilleures illustrations, remplacez les fichiers dans le dossier `images/` par vos propres images (format PNG recommandé, 400x300 pixels).

## Arrêter l'application

Appuyez sur `Ctrl+C` dans le terminal.

---

*Application créée pour accompagner les enfants dans leur apprentissage de la lecture, avec bienveillance et encouragement.*
