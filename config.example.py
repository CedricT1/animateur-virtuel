# Configuration TTS
# Choix du moteur TTS ("edge" ou "elevenlabs")
TTS_ENGINE = "edge"

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

# Configuration OpenAI/Together
TOGETHER_API_KEY = "votre_clé_api_together"

# Configuration Subsonic
BASE_URL = "url_de_votre_serveur_subsonic"
USERNAME = "votre_nom_utilisateur"
PASSWORD = "votre_mot_de_passe"
PLAYLIST_MUSIQUES_ID = "id_de_votre_playlist"

# Configuration Podcast
PODCAST_IDS = {
    "nom_podcast": "id_du_podcast"
} 