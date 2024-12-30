# Animateur Virtuel

Un script Python qui génère automatiquement des émissions de radio personnalisées avec un animateur virtuel, de la musique et des podcasts.

## Fonctionnalités

- Génération de voix avec plusieurs moteurs TTS au choix (Edge TTS, ElevenLabs, Google Cloud TTS)
- Lecture de musique depuis un serveur Subsonic
- Intégration de podcasts
- Génération de bulletins d'information
- Support multi-voix pour les dialogues
- Système de scripts pour personnaliser le contenu des émissions

## Structure du Projet

```
.
├── data/
│   ├── emissions/      # Dossier contenant les émissions générées
│   └── configurations/ # Fichiers de configuration et scripts d'émission
├── animateur.py        # Script principal
├── requirements.txt    # Dépendances Python
└── README.md          # Documentation
```

## Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd animateur_virtuel
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Copiez le fichier de configuration exemple :
```bash
cp data/configurations/config.example.py data/configurations/config.py
```

4. Modifiez le fichier `data/configurations/config.py` avec vos paramètres

## Configuration

Le fichier `config.py` permet de configurer :
- Le moteur TTS (Edge, ElevenLabs ou Google Cloud)
- Les paramètres de voix pour chaque moteur
- Les identifiants Subsonic pour la musique
- Les identifiants des podcasts
- Les clés API nécessaires

## Utilisation

1. Créez un script d'émission dans `data/configurations/` (voir les exemples existants)
2. Lancez le script :
```bash
python animateur.py
```

Les émissions générées seront sauvegardées dans le dossier `data/emissions/` avec un nom unique incluant la date et l'heure.

## Format des Scripts d'Émission

Les scripts d'émission supportent plusieurs commandes :
- `START` : Début de l'émission
- `PLAY_SONG` : Lecture d'une chanson
- `NEXT_PROMPT` : Texte de l'animateur
- `ADD_PODCAST` : Ajout d'un podcast
- `INTERLOCUTEUR` : Changement de voix pour un dialogue
- `JOURNAL` : Insertion d'un bulletin d'information
- `INSERT` : Insertion d'un fichier audio

## Licence

[À définir]
