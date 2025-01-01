# Animateur Virtuel

Un script Python qui génère automatiquement des émissions de radio personnalisées avec un animateur virtuel, de la musique et des podcasts.

## Fonctionnalités

- Génération de voix avec plusieurs moteurs TTS au choix (Edge TTS, ElevenLabs, Google Cloud TTS)
- Lecture de musique depuis un serveur Subsonic
- Intégration de podcasts
- Génération de bulletins d'information
- Support multi-voix pour les dialogues
- Système de scripts pour personnaliser le contenu des émissions
- Verset du jour avec méditation biblique

## Structure du Projet

```
.
├── data/
│   ├── emissions/      # Dossier contenant les émissions générées
│   └── configurations/ # Fichiers de configuration et scripts d'émission
├── versetjour/        # Dossier contenant les versets du jour générés
├── animateur.py       # Script principal
├── requirements.txt   # Dépendances Python
└── README.md         # Documentation
```

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/CedricT1/animateur-virtuel.git
cd animateur_virtuel
```

2. Créez et activez un environnement virtuel Python :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/MacOS
# ou
.\venv\Scripts\activate  # Sur Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Copiez le fichier de configuration exemple :
```bash
cp data/configurations/config.example.py data/configurations/config.py
```

5. Modifiez le fichier `data/configurations/config.py` avec vos paramètres

## Configuration

Le fichier `config.py` permet de configurer :
- Le moteur TTS (Edge, ElevenLabs ou Google Cloud)
- Les paramètres de voix pour chaque moteur
- Les identifiants Subsonic pour la musique
- Les identifiants des podcasts
- Les clés API nécessaires

## Utilisation

1. Créez un fichier `script_emission.txt` dans `data/configurations/` (vous pouvez vous inspirer du fichier exemple `script_emission.txt.exemple`)
2. Lancez le script :
```bash
python animateur.py
```

Les émissions générées seront sauvegardées dans le dossier `data/emissions/` avec un nom unique incluant la date et l'heure.

## Format des Scripts d'Émission

Les scripts d'émission doivent être placés dans le dossier `data/configurations/` avec l'extension `.txt`. Voici les commandes disponibles :

- `START` : Marque le début de l'émission et joue le jingle d'introduction
- `PLAY_SONG; ID; TRACK_ID` : Lecture d'une chanson
  - `ID` : Identifiant unique pour référencer la chanson plus tard avec [ID]
  - `TRACK_ID` : ID de la piste dans Subsonic ou "hasard" pour une chanson aléatoire
- `NEXT_PROMPT; TEXTE` : Fait parler l'animateur
  - Le texte peut inclure des références aux chansons avec [ID]
  - Exemple : "Nous venons d'écouter [1]" remplacera [1] par les détails de la chanson
- `ADD_PODCAST; TYPE` : Ajoute un podcast configuré dans config.py
- `INTERLOCUTEUR; FICHIER; VOIX` : Change de voix pour un dialogue
  - `FICHIER` : Chemin vers le fichier texte contenant le dialogue
  - `VOIX` : Identifiant de la voix à utiliser (ex: "fr-FR-DeniseNeural")
- `JOURNAL` : Insère le bulletin d'information
- `VERSET_DU_JOUR` : Insère le verset du jour avec une méditation biblique
  - Récupère automatiquement le verset du jour depuis bible.com
  - Génère une méditation évangélique sur le verset
- `INSERT; FICHIER` : Insère un fichier audio directement
  - `FICHIER` : Chemin vers le fichier audio à insérer
- `END` : Marque la fin de l'émission

Exemple de script :
```
START
NEXT_PROMPT;Bienvenue sur Radio Pneuma
VERSET_DU_JOUR
PLAY_SONG;1;hasard
NEXT_PROMPT;Nous venons d'écouter [1]
INTERLOCUTEUR;annonces.txt;fr-FR-DeniseNeural
END
```

## Licence

Ce projet est sous licence GNU General Public License v3.0 (GPL-3.0). Voir le fichier [LICENSE](LICENSE) pour plus de détails.
