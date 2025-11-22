import sqlite3
import os

def init_database():
    """Initialise la base de données SQLite avec les tables et les données."""

    # Créer le dossier images s'il n'existe pas
    os.makedirs("images", exist_ok=True)

    # Connexion à la base de données
    conn = sqlite3.connect("lecture.db")
    cursor = conn.cursor()

    # Suppression des anciennes tables pour réinitialisation
    cursor.execute("DROP TABLE IF EXISTS resultats")
    cursor.execute("DROP TABLE IF EXISTS questions_ouvertes")
    cursor.execute("DROP TABLE IF EXISTS qcm")
    cursor.execute("DROP TABLE IF EXISTS textes")

    # Création des tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS textes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niveau TEXT NOT NULL,
            titre TEXT NOT NULL,
            texte TEXT NOT NULL,
            theme TEXT,
            difficulte TEXT,
            image_path TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qcm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texte_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            reponse_correcte TEXT NOT NULL,
            ordre_difficulte INTEGER DEFAULT 1,
            FOREIGN KEY (texte_id) REFERENCES textes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions_ouvertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texte_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            proposition_reponse TEXT NOT NULL,
            ordre_difficulte INTEGER DEFAULT 1,
            FOREIGN KEY (texte_id) REFERENCES textes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texte_id INTEGER NOT NULL,
            date_lecture TEXT NOT NULL,
            temps_secondes REAL,
            mots_lus INTEGER,
            mots_par_minute REAL,
            FOREIGN KEY (texte_id) REFERENCES textes(id)
        )
    """)

    # =====================================================
    # TEXTES CP (10 textes, 20-50 mots, difficulté progressive)
    # =====================================================

    textes_cp = [
        # Niveau 1 - Très facile
        {
            "titre": "Mon chat",
            "texte": "J'ai un chat. Il est gris. Il dort sur mon lit. Je l'aime.",
            "theme": "animaux",
            "difficulte": "1 - Très facile",
            "image": "images/cp_chat.png",
            "qcm": [
                ("De quelle couleur est le chat ?", "Noir", "Gris", "Blanc", "Gris", 1),
            ],
            "questions_ouvertes": [
                ("Où dort le chat ?", "Le chat dort sur le lit.", 1),
            ]
        },
        # Niveau 2
        {
            "titre": "Le ballon",
            "texte": "J'ai un ballon rouge. Je joue dans le jardin. Le ballon roule. C'est amusant !",
            "theme": "jeux",
            "difficulte": "2 - Facile",
            "image": "images/cp_ballon.png",
            "qcm": [
                ("De quelle couleur est le ballon ?", "Bleu", "Rouge", "Vert", "Rouge", 1),
                ("Où joue l'enfant ?", "À l'école", "Dans le jardin", "À la maison", "Dans le jardin", 2),
            ],
            "questions_ouvertes": [
                ("Que fait le ballon ?", "Le ballon roule.", 1),
            ]
        },
        # Niveau 3
        {
            "titre": "Ma maman",
            "texte": "Ma maman est gentille. Elle me fait des câlins. Elle me lit des histoires. Je l'aime très fort.",
            "theme": "famille",
            "difficulte": "3 - Facile",
            "image": "images/cp_maman.png",
            "qcm": [
                ("Comment est la maman ?", "Méchante", "Gentille", "Triste", "Gentille", 1),
            ],
            "questions_ouvertes": [
                ("Que fait la maman à l'enfant ?", "Elle lui fait des câlins et lui lit des histoires.", 1),
            ]
        },
        # Niveau 4
        {
            "titre": "Le petit déjeuner",
            "texte": "C'est le matin. Je mange des tartines. Je bois du lait. Miam, c'est bon ! Je suis prêt pour l'école.",
            "theme": "quotidien",
            "difficulte": "4 - Facile",
            "image": "images/cp_dejeuner.png",
            "qcm": [
                ("Quand se passe l'histoire ?", "Le soir", "Le matin", "L'après-midi", "Le matin", 1),
                ("Que boit l'enfant ?", "Du jus", "Du lait", "De l'eau", "Du lait", 2),
            ],
            "questions_ouvertes": [
                ("Où va l'enfant après ?", "Il va à l'école.", 1),
            ]
        },
        # Niveau 5
        {
            "titre": "Au parc",
            "texte": "Je vais au parc avec papa. Il y a un toboggan. Je glisse, c'est amusant ! Après, je fais de la balançoire. Papa me pousse.",
            "theme": "jeux",
            "difficulte": "5 - Moyen",
            "image": "images/cp_parc.png",
            "qcm": [
                ("Avec qui va l'enfant au parc ?", "Avec maman", "Avec papa", "Avec mamie", "Avec papa", 1),
                ("Que fait l'enfant sur le toboggan ?", "Il saute", "Il glisse", "Il court", "Il glisse", 2),
            ],
            "questions_ouvertes": [
                ("Que fait papa ?", "Papa pousse l'enfant sur la balançoire.", 1),
            ]
        },
        # Niveau 6
        {
            "titre": "Mon chien Filou",
            "texte": "J'ai un chien. Il s'appelle Filou. Filou est marron. Il aime courir dans le jardin. Il aboie quand il est content. Je joue avec lui.",
            "theme": "animaux",
            "difficulte": "6 - Moyen",
            "image": "images/cp_chien.png",
            "qcm": [
                ("Comment s'appelle le chien ?", "Médor", "Filou", "Rex", "Filou", 1),
                ("De quelle couleur est Filou ?", "Noir", "Blanc", "Marron", "Marron", 2),
            ],
            "questions_ouvertes": [
                ("Que fait Filou quand il est content ?", "Il aboie quand il est content.", 1),
                ("Où court Filou ?", "Il court dans le jardin.", 2),
            ]
        },
        # Niveau 7
        {
            "titre": "La pluie",
            "texte": "Aujourd'hui, il pleut. Je mets mes bottes et mon manteau. Je saute dans les flaques. Splash ! C'est rigolo. Après, je rentre me sécher.",
            "theme": "météo",
            "difficulte": "7 - Moyen",
            "image": "images/cp_pluie.png",
            "qcm": [
                ("Quel temps fait-il ?", "Il neige", "Il pleut", "Il fait soleil", "Il pleut", 1),
                ("Que met l'enfant ?", "Des sandales", "Des bottes", "Des chaussures", "Des bottes", 2),
            ],
            "questions_ouvertes": [
                ("Que fait l'enfant dans les flaques ?", "Il saute dans les flaques.", 1),
            ]
        },
        # Niveau 8
        {
            "titre": "Le gâteau",
            "texte": "Maman fait un gâteau. Je veux aider. Je casse les œufs. Je mélange la pâte. Le gâteau cuit dans le four. Il sent bon. On va se régaler !",
            "theme": "cuisine",
            "difficulte": "8 - Difficile",
            "image": "images/cp_gateau.png",
            "qcm": [
                ("Qui fait le gâteau ?", "Papa", "Maman", "Mamie", "Maman", 1),
                ("Que casse l'enfant ?", "Des noix", "Des œufs", "Du chocolat", "Des œufs", 2),
            ],
            "questions_ouvertes": [
                ("Où cuit le gâteau ?", "Le gâteau cuit dans le four.", 1),
                ("Comment sent le gâteau ?", "Le gâteau sent bon.", 2),
            ]
        },
        # Niveau 9
        {
            "titre": "L'école",
            "texte": "Je vais à l'école. Ma maîtresse s'appelle Marie. Elle est gentille. J'apprends à lire et à écrire. À la récré, je joue avec mes amis. J'aime l'école.",
            "theme": "école",
            "difficulte": "9 - Difficile",
            "image": "images/cp_ecole.png",
            "qcm": [
                ("Comment s'appelle la maîtresse ?", "Sophie", "Marie", "Julie", "Marie", 1),
                ("Qu'apprend l'enfant ?", "À chanter", "À lire et écrire", "À dessiner", "À lire et écrire", 2),
            ],
            "questions_ouvertes": [
                ("Que fait l'enfant à la récré ?", "Il joue avec ses amis.", 1),
                ("Comment est la maîtresse ?", "Elle est gentille.", 2),
            ]
        },
        # Niveau 10
        {
            "titre": "La nuit",
            "texte": "C'est la nuit. Je mets mon pyjama. Maman me lit une histoire. Elle me fait un bisou. Je ferme les yeux. Je fais de beaux rêves. Bonne nuit !",
            "theme": "quotidien",
            "difficulte": "10 - Difficile",
            "image": "images/cp_nuit.png",
            "qcm": [
                ("Quand se passe l'histoire ?", "Le matin", "La nuit", "L'après-midi", "La nuit", 1),
                ("Que fait maman ?", "Elle chante", "Elle lit une histoire", "Elle cuisine", "Elle lit une histoire", 2),
            ],
            "questions_ouvertes": [
                ("Que met l'enfant ?", "Il met son pyjama.", 1),
                ("Que fait l'enfant après le bisou ?", "Il ferme les yeux et fait de beaux rêves.", 2),
            ]
        },
    ]

    # =====================================================
    # TEXTES CE1 (10 textes, 40-80 mots, difficulté progressive)
    # =====================================================

    textes_ce1 = [
        # Niveau 1
        {
            "titre": "Mon chat Caramel",
            "texte": "J'ai un petit chat roux. Il s'appelle Caramel. Caramel aime dormir sur le canapé. Le matin, il joue avec une balle. Je lui donne des croquettes. Il ronronne quand il est content.",
            "theme": "animaux",
            "difficulte": "1 - Très facile",
            "image": "images/ce1_chat.png",
            "qcm": [
                ("De quelle couleur est Caramel ?", "Noir", "Roux", "Blanc", "Roux", 1),
                ("Où dort Caramel ?", "Sur le lit", "Sur le canapé", "Par terre", "Sur le canapé", 2),
            ],
            "questions_ouvertes": [
                ("Avec quoi joue Caramel ?", "Il joue avec une balle.", 1),
            ]
        },
        # Niveau 2
        {
            "titre": "La récréation",
            "texte": "C'est l'heure de la récré ! Je sors dans la cour avec mes amis. Léo veut jouer au foot. Moi, je préfère les billes. On décide de jouer ensemble. C'est plus amusant à plusieurs !",
            "theme": "école",
            "difficulte": "2 - Facile",
            "image": "images/ce1_recre.png",
            "qcm": [
                ("Où vont les enfants ?", "En classe", "Dans la cour", "À la cantine", "Dans la cour", 1),
                ("À quoi veut jouer Léo ?", "Aux billes", "Au foot", "À cache-cache", "Au foot", 2),
            ],
            "questions_ouvertes": [
                ("Pourquoi c'est plus amusant à plusieurs ?", "On peut jouer ensemble et partager.", 1),
            ]
        },
        # Niveau 3
        {
            "titre": "Le marché",
            "texte": "Samedi matin, je vais au marché avec mamie. Il y a beaucoup de monde. On achète des pommes rouges et des carottes. Le marchand est gentil. Il me donne une clémentine. Merci !",
            "theme": "quotidien",
            "difficulte": "3 - Facile",
            "image": "images/ce1_marche.png",
            "qcm": [
                ("Avec qui va l'enfant au marché ?", "Avec maman", "Avec mamie", "Avec papa", "Avec mamie", 1),
                ("Qu'achètent-ils ?", "Des poires", "Des pommes et carottes", "Du pain", "Des pommes et carottes", 2),
            ],
            "questions_ouvertes": [
                ("Que donne le marchand à l'enfant ?", "Il lui donne une clémentine.", 1),
            ]
        },
        # Niveau 4
        {
            "titre": "La piscine",
            "texte": "Aujourd'hui, je vais à la piscine avec ma classe. Je mets mon maillot de bain et mon bonnet. L'eau est un peu froide au début. Je nage avec mes copains. Le maître-nageur nous apprend la brasse. C'est super !",
            "theme": "sport",
            "difficulte": "4 - Facile",
            "image": "images/ce1_piscine.png",
            "qcm": [
                ("Avec qui va l'enfant à la piscine ?", "Avec sa famille", "Avec sa classe", "Tout seul", "Avec sa classe", 1),
                ("Comment est l'eau ?", "Chaude", "Un peu froide", "Tiède", "Un peu froide", 2),
            ],
            "questions_ouvertes": [
                ("Qu'apprend le maître-nageur ?", "Il apprend la brasse aux enfants.", 1),
            ]
        },
        # Niveau 5
        {
            "titre": "Le jardin de papi",
            "texte": "Papi a un grand jardin. Il y a des tomates, des salades et des fraises. Je l'aide à arroser les plantes. On enlève aussi les mauvaises herbes. Papi me montre une coccinelle sur une feuille. Elle est rouge avec des points noirs.",
            "theme": "nature",
            "difficulte": "5 - Moyen",
            "image": "images/ce1_jardin.png",
            "qcm": [
                ("Qu'y a-t-il dans le jardin de papi ?", "Des fleurs", "Des légumes et fruits", "Des arbres", "Des légumes et fruits", 1),
                ("De quelle couleur est la coccinelle ?", "Jaune", "Rouge", "Orange", "Rouge", 2),
            ],
            "questions_ouvertes": [
                ("Que fait l'enfant pour aider papi ?", "Il arrose les plantes et enlève les mauvaises herbes.", 1),
            ]
        },
        # Niveau 6
        {
            "titre": "La tempête",
            "texte": "Cette nuit, il y a eu une tempête. Le vent soufflait très fort. Les volets claquaient. J'avais un peu peur. Maman est venue me rassurer. Ce matin, il y a des branches par terre dans le jardin. Papa va les ramasser.",
            "theme": "météo",
            "difficulte": "6 - Moyen",
            "image": "images/ce1_tempete.png",
            "qcm": [
                ("Quand la tempête a-t-elle eu lieu ?", "Le matin", "Cette nuit", "L'après-midi", "Cette nuit", 1),
                ("Qu'y a-t-il par terre ce matin ?", "Des feuilles", "Des branches", "De l'eau", "Des branches", 2),
            ],
            "questions_ouvertes": [
                ("Que faisaient les volets ?", "Les volets claquaient à cause du vent.", 1),
                ("Que va faire papa ?", "Il va ramasser les branches.", 2),
            ]
        },
        # Niveau 7
        {
            "titre": "La bibliothèque",
            "texte": "Mercredi, je suis allé à la bibliothèque avec maman. J'ai choisi un livre sur les dinosaures et une bande dessinée. La bibliothécaire m'a montré comment utiliser ma carte. Je peux garder les livres trois semaines. J'ai hâte de les lire !",
            "theme": "lecture",
            "difficulte": "7 - Moyen",
            "image": "images/ce1_biblio.png",
            "qcm": [
                ("Quel jour l'enfant va-t-il à la bibliothèque ?", "Lundi", "Mercredi", "Samedi", "Mercredi", 1),
                ("Combien de temps peut-il garder les livres ?", "Une semaine", "Trois semaines", "Un mois", "Trois semaines", 2),
            ],
            "questions_ouvertes": [
                ("Quels livres a choisi l'enfant ?", "Il a choisi un livre sur les dinosaures et une bande dessinée.", 1),
            ]
        },
        # Niveau 8
        {
            "titre": "Le vélo",
            "texte": "Papa m'apprend à faire du vélo sans les petites roues. Au début, j'ai peur de tomber. Papa tient la selle pour m'aider. Je pédale de plus en plus vite. Soudain, je me retourne : papa ne tient plus ! Je roule tout seul ! Je suis trop content !",
            "theme": "sport",
            "difficulte": "8 - Difficile",
            "image": "images/ce1_velo.png",
            "qcm": [
                ("Qui apprend à l'enfant ?", "Maman", "Papa", "Papi", "Papa", 1),
                ("Que tient papa ?", "Le guidon", "La selle", "La roue", "La selle", 2),
            ],
            "questions_ouvertes": [
                ("Pourquoi l'enfant a-t-il peur au début ?", "Il a peur de tomber.", 1),
                ("Comment se sent l'enfant à la fin ?", "Il est très content car il roule tout seul.", 2),
            ]
        },
        # Niveau 9
        {
            "titre": "Le spectacle",
            "texte": "Notre classe prépare un spectacle pour Noël. Je joue le rôle d'un lutin. J'ai un costume vert et un bonnet pointu. On répète tous les jours. J'ai un peu le trac mais mes parents seront là pour m'encourager. J'espère ne pas oublier mon texte !",
            "theme": "école",
            "difficulte": "9 - Difficile",
            "image": "images/ce1_spectacle.png",
            "qcm": [
                ("Quel rôle joue l'enfant ?", "Un père Noël", "Un lutin", "Un renne", "Un lutin", 1),
                ("De quelle couleur est le costume ?", "Rouge", "Vert", "Bleu", "Vert", 2),
            ],
            "questions_ouvertes": [
                ("Pourquoi l'enfant a-t-il le trac ?", "Il a peur d'oublier son texte devant ses parents.", 1),
                ("Quand est le spectacle ?", "Le spectacle est pour Noël.", 2),
            ]
        },
        # Niveau 10
        {
            "titre": "Le hamster",
            "texte": "Ma sœur a eu un hamster pour son anniversaire. Il s'appelle Noisette car il adore les noisettes. Il vit dans une cage avec une roue. La nuit, il court dans sa roue et ça fait du bruit ! Le week-end, on le laisse se promener dans le salon. Il est trop mignon.",
            "theme": "animaux",
            "difficulte": "10 - Difficile",
            "image": "images/ce1_hamster.png",
            "qcm": [
                ("Pourquoi le hamster s'appelle Noisette ?", "Il est marron", "Il adore les noisettes", "Il est petit", "Il adore les noisettes", 1),
                ("Quand court-il dans sa roue ?", "Le jour", "La nuit", "Le matin", "La nuit", 2),
                ("Où se promène-t-il le week-end ?", "Dans la chambre", "Dans le salon", "Dans le jardin", "Dans le salon", 3),
            ],
            "questions_ouvertes": [
                ("À quelle occasion la sœur a-t-elle eu le hamster ?", "Elle l'a eu pour son anniversaire.", 1),
            ]
        },
    ]

    # =====================================================
    # TEXTES CE2 (10 textes, 80-120 mots, difficulté progressive)
    # =====================================================

    textes_ce2 = [
        # Niveau 1
        {
            "titre": "La rentrée",
            "texte": "C'est le jour de la rentrée. Je suis en CE2 maintenant. Ma nouvelle maîtresse s'appelle Madame Dupont. Elle a l'air gentille. Je retrouve mes copains dans la cour. On se raconte nos vacances. La classe est grande et lumineuse. J'ai une nouvelle trousse et un beau cartable bleu. J'ai hâte d'apprendre de nouvelles choses cette année.",
            "theme": "école",
            "difficulte": "1 - Très facile",
            "image": "images/ce2_rentree.png",
            "qcm": [
                ("En quelle classe est l'enfant ?", "CE1", "CE2", "CM1", "CE2", 1),
                ("Comment s'appelle la maîtresse ?", "Madame Martin", "Madame Dupont", "Madame Durand", "Madame Dupont", 2),
            ],
            "questions_ouvertes": [
                ("Comment est la classe ?", "La classe est grande et lumineuse.", 1),
            ]
        },
        # Niveau 2
        {
            "titre": "La sortie au zoo",
            "texte": "Aujourd'hui, toute la classe va au zoo. On prend le car. C'est la première fois que je vois des lions en vrai ! Ils sont énormes. On voit aussi des girafes, des éléphants et des singes. Les singes sont très drôles, ils sautent partout. À midi, on pique-nique sur l'herbe. C'est une super journée !",
            "theme": "animaux",
            "difficulte": "2 - Facile",
            "image": "images/ce2_zoo.png",
            "qcm": [
                ("Comment va la classe au zoo ?", "En train", "En car", "À pied", "En car", 1),
                ("Comment sont les lions ?", "Petits", "Énormes", "Moyens", "Énormes", 2),
            ],
            "questions_ouvertes": [
                ("Que font les singes ?", "Les singes sautent partout, ils sont très drôles.", 1),
            ]
        },
        # Niveau 3
        {
            "titre": "Le gâteau d'anniversaire",
            "texte": "C'est l'anniversaire de maman. Avec papa, on décide de lui faire une surprise. On prépare un gâteau au chocolat. Je casse les œufs et papa mesure la farine. On mélange bien la pâte. Pendant que le gâteau cuit, on décore la table avec des ballons. Quand maman rentre, elle est très contente. Le gâteau est délicieux !",
            "theme": "cuisine",
            "difficulte": "3 - Facile",
            "image": "images/ce2_gateau.png",
            "qcm": [
                ("Pour qui est la surprise ?", "Pour papa", "Pour maman", "Pour mamie", "Pour maman", 1),
                ("Que fait papa ?", "Il casse les œufs", "Il mesure la farine", "Il décore", "Il mesure la farine", 2),
            ],
            "questions_ouvertes": [
                ("Comment décorent-ils la table ?", "Ils décorent la table avec des ballons.", 1),
            ]
        },
        # Niveau 4
        {
            "titre": "La cabane",
            "texte": "Avec mes cousins, on construit une cabane dans le jardin de papi. On utilise des planches et des vieilles couvertures. C'est un peu difficile mais on s'entraide. La cabane n'est pas très grande mais on est fiers de notre travail. On y met des coussins pour s'asseoir. C'est notre coin secret pour jouer et raconter des histoires.",
            "theme": "jeux",
            "difficulte": "4 - Facile",
            "image": "images/ce2_cabane.png",
            "qcm": [
                ("Où construisent-ils la cabane ?", "Dans la forêt", "Dans le jardin de papi", "À l'école", "Dans le jardin de papi", 1),
                ("Qu'utilisent-ils ?", "Des briques", "Des planches et couvertures", "Du carton", "Des planches et couvertures", 2),
            ],
            "questions_ouvertes": [
                ("Pourquoi sont-ils fiers ?", "Ils sont fiers car ils ont réussi à construire la cabane ensemble.", 1),
            ]
        },
        # Niveau 5
        {
            "titre": "La correspondante",
            "texte": "Dans ma classe, on a des correspondants. Ma correspondante s'appelle Léonie. Elle habite à Marseille. On s'écrit des lettres. Elle me raconte sa ville et la mer. Moi, je lui parle de ma campagne et de mes animaux. Elle m'a envoyé une photo d'elle avec son chien. J'aimerais bien la rencontrer un jour. Peut-être qu'on pourra se voir en fin d'année.",
            "theme": "école",
            "difficulte": "5 - Moyen",
            "image": "images/ce2_lettre.png",
            "qcm": [
                ("Comment s'appelle la correspondante ?", "Lucie", "Léonie", "Léa", "Léonie", 1),
                ("Où habite-t-elle ?", "À Paris", "À Marseille", "À Lyon", "À Marseille", 2),
            ],
            "questions_ouvertes": [
                ("De quoi parle Léonie dans ses lettres ?", "Elle parle de sa ville et de la mer.", 1),
                ("Que souhaite l'enfant ?", "Il souhaite rencontrer sa correspondante un jour.", 2),
            ]
        },
        # Niveau 6
        {
            "titre": "Le camping",
            "texte": "Cet été, on part en camping avec mes parents. On monte la tente près d'un lac. C'est difficile mais papa m'explique comment faire. La nuit, j'entends les grenouilles et les grillons. Le matin, on se baigne dans le lac. L'eau est fraîche mais c'est agréable. Le soir, on fait griller des chamallows sur le feu. J'adore ces vacances en pleine nature !",
            "theme": "vacances",
            "difficulte": "6 - Moyen",
            "image": "images/ce2_camping.png",
            "qcm": [
                ("Où la famille installe-t-elle la tente ?", "En forêt", "Près d'un lac", "À la montagne", "Près d'un lac", 1),
                ("Qu'entend l'enfant la nuit ?", "Des oiseaux", "Des grenouilles et grillons", "Le vent", "Des grenouilles et grillons", 2),
            ],
            "questions_ouvertes": [
                ("Que font-ils le soir ?", "Ils font griller des chamallows sur le feu.", 1),
            ]
        },
        # Niveau 7
        {
            "titre": "Le musée",
            "texte": "Notre classe visite le musée d'histoire naturelle. On voit un squelette de dinosaure immense. Le guide nous explique que ce dinosaure vivait il y a des millions d'années. On découvre aussi des fossiles et des pierres précieuses. Ma partie préférée, c'est la salle des papillons. Il y en a de toutes les couleurs ! Je prends beaucoup de photos pour montrer à mes parents.",
            "theme": "découverte",
            "difficulte": "7 - Moyen",
            "image": "images/ce2_musee.png",
            "qcm": [
                ("Quel musée visitent-ils ?", "Musée d'art", "Musée d'histoire naturelle", "Musée de la mer", "Musée d'histoire naturelle", 1),
                ("Quelle est la partie préférée de l'enfant ?", "Les dinosaures", "La salle des papillons", "Les fossiles", "La salle des papillons", 2),
            ],
            "questions_ouvertes": [
                ("Quand vivaient les dinosaures ?", "Les dinosaures vivaient il y a des millions d'années.", 1),
            ]
        },
        # Niveau 8
        {
            "titre": "Le tournoi de foot",
            "texte": "Samedi, c'est le grand tournoi de foot de notre club. Je suis un peu stressé mais très excité. On joue trois matchs. Le premier, on gagne deux à zéro. Le deuxième est plus difficile mais on fait match nul. Pour le dernier match, je marque un but ! On finit à la deuxième place. L'entraîneur nous félicite. On a tous une médaille. Je suis vraiment fier de mon équipe.",
            "theme": "sport",
            "difficulte": "8 - Difficile",
            "image": "images/ce2_foot.png",
            "qcm": [
                ("Combien de matchs jouent-ils ?", "Deux", "Trois", "Quatre", "Trois", 1),
                ("Quel est le résultat du premier match ?", "Match nul", "Défaite", "Victoire deux à zéro", "Victoire deux à zéro", 2),
            ],
            "questions_ouvertes": [
                ("À quelle place finissent-ils ?", "Ils finissent à la deuxième place.", 1),
                ("Pourquoi l'enfant est-il fier ?", "Il est fier car il a marqué un but et son équipe a bien joué.", 2),
            ]
        },
        # Niveau 9
        {
            "titre": "L'orage",
            "texte": "Hier soir, il y a eu un gros orage. Le ciel était très sombre. Soudain, un éclair a illuminé toute la maison. Puis le tonnerre a grondé si fort que j'ai sursauté. La pluie tombait très fort sur le toit. J'avais un peu peur alors maman est restée avec moi. Elle m'a expliqué comment se forme un orage. C'est la différence de température qui crée l'électricité. C'est fascinant finalement !",
            "theme": "météo",
            "difficulte": "9 - Difficile",
            "image": "images/ce2_orage.png",
            "qcm": [
                ("Quand l'orage a-t-il eu lieu ?", "Ce matin", "Hier soir", "Cette nuit", "Hier soir", 1),
                ("Qu'est-ce qui crée l'électricité ?", "Le vent", "La différence de température", "La pluie", "La différence de température", 2),
            ],
            "questions_ouvertes": [
                ("Comment était le ciel ?", "Le ciel était très sombre.", 1),
                ("Pourquoi l'enfant trouve-t-il l'orage fascinant finalement ?", "Car maman lui a expliqué comment il se forme.", 2),
            ]
        },
        # Niveau 10
        {
            "titre": "Le déménagement",
            "texte": "Ma meilleure amie Chloé va déménager. Elle part habiter dans une autre ville car son papa a trouvé un nouveau travail. Je suis très triste. On se connaît depuis la maternelle. Chloé aussi est triste mais elle me promet qu'on restera amies. On pourra s'appeler et s'écrire. Peut-être même que j'irai la voir pendant les vacances. Le jour du départ, on se fait un gros câlin. Je sais qu'on ne s'oubliera jamais.",
            "theme": "amitié",
            "difficulte": "10 - Difficile",
            "image": "images/ce2_demenagement.png",
            "qcm": [
                ("Pourquoi Chloé déménage-t-elle ?", "Sa maman est malade", "Son papa a un nouveau travail", "Elle change d'école", "Son papa a un nouveau travail", 1),
                ("Depuis quand se connaissent-elles ?", "Le CP", "La maternelle", "Le CE1", "La maternelle", 2),
            ],
            "questions_ouvertes": [
                ("Comment vont-elles rester en contact ?", "Elles vont s'appeler, s'écrire et peut-être se voir pendant les vacances.", 1),
                ("Comment se sent l'enfant et pourquoi ?", "L'enfant est triste car sa meilleure amie part.", 2),
            ]
        },
    ]

    # Insertion des textes et questions
    all_textes = [
        ("CP", textes_cp),
        ("CE1", textes_ce1),
        ("CE2", textes_ce2)
    ]

    for niveau, textes in all_textes:
        for texte_data in textes:
            # Insérer le texte
            cursor.execute("""
                INSERT INTO textes (niveau, titre, texte, theme, difficulte, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                niveau,
                texte_data["titre"],
                texte_data["texte"],
                texte_data["theme"],
                texte_data["difficulte"],
                texte_data["image"]
            ))

            texte_id = cursor.lastrowid

            # Insérer les QCM
            for qcm in texte_data["qcm"]:
                cursor.execute("""
                    INSERT INTO qcm (texte_id, question, option_a, option_b, option_c, reponse_correcte, ordre_difficulte)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (texte_id, qcm[0], qcm[1], qcm[2], qcm[3], qcm[4], qcm[5]))

            # Insérer les questions ouvertes
            for q_ouverte in texte_data["questions_ouvertes"]:
                cursor.execute("""
                    INSERT INTO questions_ouvertes (texte_id, question, proposition_reponse, ordre_difficulte)
                    VALUES (?, ?, ?, ?)
                """, (texte_id, q_ouverte[0], q_ouverte[1], q_ouverte[2]))

    conn.commit()
    conn.close()

    print("Base de données initialisée avec succès !")
    print(f"- {len(textes_cp)} textes CP (difficulté 1 à 10)")
    print(f"- {len(textes_ce1)} textes CE1 (difficulté 1 à 10)")
    print(f"- {len(textes_ce2)} textes CE2 (difficulté 1 à 10)")

if __name__ == "__main__":
    init_database()
