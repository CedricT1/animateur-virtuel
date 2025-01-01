# Configuration TTS
# Choix du moteur TTS ("edge", "elevenlabs" ou "google")
TTS_ENGINE = "edge"

# Configuration de la date
from datetime import date
today = date.today()
DATE_FORMAT = "%d.%m.%Y"  # Format de date à utiliser dans tout le projet
FORMATTED_DATE = today.strftime(DATE_FORMAT)

# Configuration Edge TTS
# Voix disponibles pour le français :
# - Microsoft Server Speech Text to Speech Voice (fr-FR, HenriNeural) - Homme
# - Microsoft Server Speech Text to Speech Voice (fr-FR, DeniseNeural) - Femme
# - Microsoft Server Speech Text to Speech Voice (fr-FR, EloiseNeural) - Femme
# - Microsoft Server Speech Text to Speech Voice (fr-FR, VivienneMultilingualNeural) - Femme multilingue
# - Microsoft Server Speech Text to Speech Voice (fr-FR, RemyMultilingualNeural) - Homme multilingue
EDGE_VOICE = "Microsoft Server Speech Text to Speech Voice (fr-FR, HenriNeural)"
EDGE_RATE = "+0%"
EDGE_PITCH = "+0Hz"

# Configuration Elevenlabs
ELEVENLABS_API_KEY = "votre_clé_api_elevenlabs"
# ID de la voix Elevenlabs (exemple : "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_VOICE_ID = "votre_voice_id"
# Paramètres de la voix (optionnels)
ELEVENLABS_STABILITY = 0.5  # Entre 0 et 1, défaut: 0.5
ELEVENLABS_CLARITY = 0.75   # Entre 0 et 1, défaut: 0.75

# Configuration Google Cloud TTS
# Chemin vers le fichier de credentials JSON
GOOGLE_CREDENTIALS_FILE = "path/to/your/google-credentials.json"
# Voix disponibles pour le français :
# - fr-FR-Neural2-A (Femme)
# - fr-FR-Neural2-B (Homme)
# - fr-FR-Neural2-C (Femme)
# - fr-FR-Neural2-D (Homme)
# - fr-FR-Neural2-E (Femme)
GOOGLE_VOICE = "fr-FR-Neural2-B"  # Voix masculine par défaut
GOOGLE_LANGUAGE_CODE = "fr-FR"
# Paramètres de la voix (optionnels)
GOOGLE_SPEAKING_RATE = 1.0  # Entre 0.25 et 4.0, défaut: 1.0
GOOGLE_PITCH = 0.0  # Entre -20.0 et 20.0, défaut: 0.0

# Configuration OpenAI/Together
TOGETHER_API_KEY = "votre_clé_api_together"
# Configuration du modèle LLM
LLM_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"  # Modèle à utiliser pour la génération de texte

# Configuration Subsonic
BASE_URL = "url_de_votre_serveur_subsonic"
USERNAME = "votre_nom_utilisateur"
PASSWORD = "votre_mot_de_passe"
PLAYLIST_MUSIQUES_ID = "id_de_votre_playlist"

# Configuration Podcast
PODCAST_IDS = {
    "nom_podcast": "id_du_podcast"
} 