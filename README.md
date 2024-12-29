# Créer le fichier README.md
echo '# Animateur Radio Virtuel

Un système automatisé pour créer des émissions de radio avec un animateur virtuel, spécialement conçu pour une radio chrétienne.

## Fonctionnalités

- 🎵 Lecture de musique depuis un serveur Subsonic
- 🎙️ Animation virtuelle via LLama AI
- 🗣️ Synthèse vocale pour l"animateur
- 📻 Intégration de podcasts
- 🎧 Assemblage automatique d"émissions complètes

## Installation

1. Clonez le dépôt
2. Installez les dépendances : `pip install -r requirements.txt`
3. Configurez votre `config.py`
4. Lancez avec `python animateur.py`

## Configuration

Créez un fichier `config.py` avec :
- TOGETHER_API_KEY
- USERNAME et PASSWORD (Subsonic)
- BASE_URL
- Autres paramètres TTS

## Utilisation

Créez un fichier `script_emission.txt` avec les commandes :
- START
- PLAY_SONG
- NEXT_PROMPT
- ADD_PODCAST
- INTERLOCUTEUR
- INSERT' > README.md

# Créer le fichier requirements.txt
echo 'requests>=2.31.0
openai>=1.12.0
pydub>=0.25.1
python-dateutil>=2.8.2
PyYAML>=6.0.1' > requirements.txt
